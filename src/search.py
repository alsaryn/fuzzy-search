"""Read in searches from disk and gather related posts."""

import os
import time
import sqlite3
import pickle
import multiprocessing

import util
from progressbar import progressbar
import analysis
from utilfilepath import filepath
from utiltext import translate
from utiloptions import options
from util import custom, blacklist, tag_to_category


def read_and_process_queries() -> None:
    """Read queries from disk into Fuzzy Search."""
    query_list = []
    for filename in os.listdir(filepath.tags_in_dir):
        query_file = filepath.tags_in_dir / filename
        # Each row is treated as a single query, containing one or more tags
        with open(query_file, "rt", encoding="utf-8") as in_file:
            for line in in_file:
                # Ignore comments and whitespace/newlines
                if line[0] != "#" and line[0] != "\n":
                    query_list.append(line.strip("\n").split(" "))

    # If no queries were found, create a sample file.
    if len(query_list) == 0:
        print(
            f"No searches found in {filepath.tags_in_dir}.\n"
            f"  Creating and using sample search file instead."
        )
        query_list = util.generate_sample_searches()
        with open(
            filepath.tags_in_dir / filepath.sample_queries,
            "wt",
            encoding="utf-8",
        ) as out_file:
            for line in query_list:
                out_file.write(" ".join(line) + "\n")
    else:
        print(
            translate.text(
                f"Found {len(query_list)} searches in {filepath.tags_in_dir}."
            )
        )

    # Process discovered queries
    split_query_list(query_list)


def split_query_list(query_list: list[list[str]]) -> None:
    """Split a list of queries into single tasks."""
    # The input tags are all combined.
    # Initial pass: Check for any invalid tags in all queries.
    # Open a DB connection to check if the user-specified tag exists.
    if not filepath.cache_postid_database.exists():
        raise (
            util.CacheFileNotFound(
                message=f"Cache File Not Found: {filepath.cache_postid_database}"
            )
        )

    con = sqlite3.connect(filepath.cache_postid_database)
    cur = con.cursor()
    for tag_list in query_list:
        for tag in tag_list:
            # Ignore the negation and or operators, if present
            try:
                if tag[0] == "-" or tag[0] == "~":
                    base = tag[1:]
                else:
                    base = tag
                if not tag_to_category.get_category(base, print_missing_tag=False):
                    if base != options.all_posts:
                        print(
                            f"Error: {base} is not a valid tag."
                            f" Full search: {tag_list}."
                        )
                        return
            except IndexError:
                print(f"Error: {tag} is not a valid tag. Full search: {tag_list}.")
                return
            # Sanity check: tag exists in the post id database
            if base != options.all_posts:
                cur.execute("SELECT posts FROM ids WHERE tag = ?", (base,))
                if cur.fetchone() is None:
                    print(f"Error: {base} is not a valid tag. Full search: {tag_list}.")
                    return
    con.close()

    progressbar.start_new_stage("Processing Queries", len(query_list))
    start_time = time.time()

    # If we have multiple queries, create a new process for each query.
    # This enables multiprocessing to improve speed.
    if len(query_list) > 1:
        with multiprocessing.Pool() as pool:
            # imap_unordered returns as each individual job completes.
            # This means we can update the progress bar after each job completes.
            results = pool.imap_unordered(process_single_query, query_list)
            # Each process has a separate copy of progress bar,
            # so updating progress per-process won't work.
            # Instead, we have to use imap_unordered to send a callback to the main
            # process, so only one copy of progress bar gets all the update_step().
            for result in results:
                progressbar.update_step()

    # If there are only a few queries,
    # then it's faster to split the queries into parallel sub-tasks.
    # This algorithm also is better-suited for queries with millions of posts
    # to avoid running out of memory.
    else:
        # Queries will be processed sequentially (single core), but we free up cores
        # to use on parallelizing sub-tasks of query analysis (NYI).
        for tag_list in query_list:
            process_single_query(tag_list)

    # Finished processing all queries; print stats
    duration = time.time() - start_time
    print(
        translate.text(
            f"Time to process {len(query_list)} searches: {round(duration, 2)} s"
        )
    )


def process_single_query(tag_list: list[str]) -> None:
    """Create directory containing an individual query's analysis."""
    print(translate.text(f"  Pre-processing {tag_list}"))

    # Split the input tags into include/or/exclude tags.
    include_tags = []
    or_tags = []
    exclude_tags = []
    for tag in tag_list:
        # Check for the or and negation operators.
        if tag[0] == "-":
            exclude_tags.append(tag[1:])
        elif tag[0] == "~":
            or_tags.append(tag[1:])
        else:
            include_tags.append(tag)
    # Sort each list alphabetically.
    include_tags = sorted(include_tags)
    or_tags = sorted(or_tags)
    exclude_tags = sorted(exclude_tags)

    post_ids, post_data, num_blacklisted = get_valid_posts(
        " ".join(tag_list), include_tags, or_tags, exclude_tags
    )
    if len(post_ids) == 0:
        print(translate.text(f"Skipping Search (No posts found): {tag_list}.\n"))
        progressbar.update_step()
        return

    # [--- Filename ---]
    # The folder storing this query's output depends on these metrics
    scores_list = []
    favorites_list = []
    comments_list = []
    # Iterate over each valid post
    for post in post_data:
        # rating_str = score favs comments_count rating_char
        rating = post.rating_str.split(" ")
        scores_list.append(int(rating[0]))
        favorites_list.append(int(rating[1]))
        # Remove the leading "C" from comments_count
        comments_list.append(int(rating[2][1:]))

    # Store this info so we can reuse it later
    query_stats = {
        "score_avg": util.get_average(scores_list),
        "score_med": util.get_median(scores_list),
        "fav_avg": util.get_average(favorites_list),
        "fav_med": util.get_median(favorites_list),
        "com_avg": util.get_average(comments_list),
        "com_med": util.get_median(comments_list),
        "num_blacklisted": num_blacklisted,
    }

    # Analysis results will be placed in a folder.
    # Folder name that uses the same order of tags as in the query
    folder_name = " ".join(tag_list)

    # Append the number of valid posts and median score to the folder name.
    # These appended values make it easier to compare query results at a glance.
    folder_name = f"{folder_name} {len(post_ids)} {query_stats['score_med']}"

    output_dir = filepath.tags_out_dir / folder_name

    if options.url_only:
        analysis.process_tags_url(output_dir, post_data)
        # If we output URL information, skip all other data analysis
        return

    # Don't analyze search if we find the output folder already exists
    if output_dir.exists() and not options.override:
        print(translate.text(f"  {folder_name} already exists, skipping search."))
        progressbar.update_step()
    else:
        print(translate.text(f"  Analyzing: {folder_name}"))
        # Create the folder housing the output for this query
        output_dir.mkdir(parents=True, exist_ok=True)
        # Generate and save analysis data to disk
        analysis.analyze_single_query(
            tag_list, output_dir, post_ids, post_data, query_stats
        )
        print(translate.text(f"  Finished analysis: {folder_name}"))
        progressbar.update_step()


def get_valid_posts(
    query_tag_list: str,
    include_tags: list[str],
    or_tags: list[str],
    exclude_tags: list[str],
) -> tuple[set[int], list[util.PostData], int]:
    """Get the list of valid (not excluded) tags from the database.

    Returns a tuple with 2 elements.
        Element 1: set of all post ids (in str format).
        Element 2: list of all PostData objects corresponding to post ids.
    """
    post_ids = get_post_ids_initial(include_tags, or_tags, exclude_tags)
    if len(post_ids) == 0:
        return set(), [], 0

    if len(post_ids) > options.max_query_size:
        print(f"Warning: {query_tag_list} returned {len(post_ids)} posts.")
        print(
            "  Note: This value is before posts have been pruned"
            " by options such as --min_score and --start_date."
        )
        print(
            f"  To limit RAM usage, Fuzzy Search limits searches to at most"
            f" {options.max_query_size} posts."
        )
        print("  Use the --max_posts argument to increase this limit.")
        print("  As a guide, processing 1 million posts peaks at about 8 GB of RAM.")
        print("  If your machine has multiple cores, process huge queries one-by-one.")
        return set(), [], 0

    # Use each post id to access the associated post's data from the posts database.
    # While E6 contains millions of posts, queries often filter down to <10k posts.
    # Therefore, it's (usually) fine to store all these posts in memory at once.
    post_list = []
    con = sqlite3.connect(filepath.cache_post_data_database)
    cur = con.cursor()
    valid_post_ids = set()
    num_blacklisted = 0
    # Store this to be reused
    blacklist_category = None
    if "Blacklist" in custom.categories:
        blacklist_category = custom.categories["Blacklist"]

    # Determine the valid posts, and fill out post data
    for postid in sorted(list(post_ids), reverse=options.descending):
        res = cur.execute(
            "SELECT * FROM posts WHERE postid = ?", (int(postid),)
        ).fetchone()
        post = util.PostData(res)

        post_code = is_post_valid(post, blacklist_category)
        # Add valid posts
        if post_code == 0:
            post_list.append(post)
            valid_post_ids.add(postid)
        # Skip invalid posts
        elif post_code == 1:
            # Tally posts hit by the blacklist
            num_blacklisted += 1

    con.close()
    # Announce if no posts were found after applying blacklist
    if len(post_ids) == 0:
        print("Search contains no Safe/non-blacklisted posts; too spicy :(")

    # Order posts by custom category score
    if options.order == options.or_category:
        category_tags = {}
        for tag in or_tags:
            category_tags[tag] = 1.0
        post_info = []
        for post in post_list:
            post_score = 0
            for tag_list in post.tags.values():
                for tag in tag_list:
                    if tag in category_tags:
                        post_score += category_tags[tag]
            post_info.append((post_score, post))
        # Sort posts
        post_info = sorted(post_info, key=lambda v: (v[0]), reverse=options.descending)
        # Reform the post/post id lists with the new order
        post_list = []
        valid_post_ids = set()
        for post in post_info:
            post_list.append(post[1])
            valid_post_ids.add(post[1].post_id)
    elif options.order != "":
        # Find the custom category with matching name
        if options.order not in custom.categories:
            print(
                "WARNING: Search requested filtering by custom category,"
                " but no such category exists. Skipping filtering."
            )
        else:
            category_tags = custom.categories[options.order]
            post_info = []
            for post in post_list:
                post_score = 0
                for tag_list in post.tags.values():
                    for tag in tag_list:
                        if tag in category_tags.keys():
                            post_score += category_tags[tag]
                post_info.append((post_score, post))
            # Sort posts
            post_info = sorted(
                post_info, key=lambda v: (v[0]), reverse=options.descending
            )
            # Reform the post/post id lists with the new order
            post_list = []
            valid_post_ids = set()
            for post in post_info:
                post_list.append(post[1])
                valid_post_ids.add(post[1].post_id)

    # Return the top % of sorted posts
    if options.percent_posts_to_keep < 100.0:
        # Find the number of posts to omit
        num_posts = int(len(valid_post_ids) * options.percent_posts_to_keep / 100)
        # Clamp value to correspond with the first or lst post
        num_posts = max(1, num_posts)
        num_posts = min(len(valid_post_ids), num_posts)
        # Update the post list
        post_list = post_list[:num_posts]
        # Reform the set of post ids
        valid_post_ids = set()
        for post in post_list:
            valid_post_ids.add(post.post_id)
    return valid_post_ids, post_list, num_blacklisted


def unpickle_ids(tag:str, res) -> list[int]:
    """Unpickle database blob into a list of post ids."""
    try:
        res = pickle.loads(res[0])
        return res
    except TypeError:
        print(f"Warning: skipping corrupted data {tag}"
              f" in {filepath.cache_postid_database}.")
        return []


def get_post_ids_initial(
    include_tags: list[str], or_tags: list[str], exclude_tags: list[str]
) -> set[int]:
    """Get the initial list of post ids from the database."""
    post_ids = set()

    # Read in from the postid database
    # Exit if the file is missing
    if not filepath.cache_postid_database.exists():
        raise (
            util.CacheFileNotFound(
                message=f"Cache File Not Found: {filepath.cache_postid_database}"
            )
        )

    con = sqlite3.connect(filepath.cache_postid_database)
    cur = con.cursor()
    # Special case:
    # If no include and no ~tags were specified, use the set of all post ids.
    if len(include_tags) == 0 and len(or_tags) == 0:
        include_tags = [options.all_posts]
    if options.all_posts in include_tags:
        print(
            "WARNING:\n  Search includes entire database.\n"
            "  This search may take considerable resources to process.\n"
        )

    # Initialize the set of post ids to be the union of ~tags
    if len(or_tags) != 0:
        for tag in or_tags:
            res = cur.execute("SELECT posts FROM ids WHERE tag = ?",
                              (tag,)).fetchone()
            res = unpickle_ids(tag, res)
            post_ids.update(res)

    # If no ~tags were found,
    # Initialize the set of valid post ids to posts with the first include tag
    if len(or_tags) == 0:
        res = cur.execute(
            "SELECT posts FROM ids WHERE tag = ?", (include_tags[0],)
        ).fetchone()
        res = unpickle_ids(include_tags[0], res)
        # Get the superset of all ids with the current and newly-found lists of ids
        post_ids.update(res)

        # Set the include tags to be the remaining include tags
        include_tags = include_tags[1:]

    # Sanity check: post_ids should be non-empty after initialization
    if len(post_ids) == 0:
        print("WARNING: Search involved an invalid tag with 0 associated posts.")
        return set()

    # Filter for the posts that contain all other include tags
    for tag in include_tags:
        res = cur.execute("SELECT posts FROM ids WHERE tag = ?", (tag,)).fetchone()
        res = unpickle_ids(tag, res)
        post_ids.intersection_update(res)
        # Stop processing if we end up with no valid posts
        if len(post_ids) == 0:
            print("Search returned zero posts.")
            con.close()
            return set()

    # Filter for the posts that don't contain any of the exclude tags
    for tag in exclude_tags:
        res = cur.execute("SELECT posts FROM ids WHERE tag = ?", (tag,)).fetchone()
        res = unpickle_ids(tag, res)
        post_ids.difference_update(res)
        # Stop processing if we end up with no valid posts
        if len(post_ids) == 0:
            print("Search returned zero posts.")
            con.close()
            return set()
    con.close()
    return post_ids


def is_post_valid(post: util.PostData, blacklist_in: dict) -> int:
    """Return 0 if post should be included in query.

    PARAMETERS
        blacklist_in: The "Blacklist" custom category (dict [str, float])
            Maps blacklisted tags to their weight.

    RETURNS:
        0: Include post
        1: Exclude post (blacklisted)
        2: Exclude post (other reason)
    """
    # Exclude posts if their rating isn't in the included ratings option
    if post.rating_str[-1] not in options.rating:
        return 2

    # Check start/end date ranges
    if options.start_date is not None:
        # Exclude posts created before the start date
        if post.created_at < options.start_date:
            return 2
    if options.end_date is not None:
        # Exclude posts created after the end date
        if post.created_at > options.end_date:
            return 2

    # Exclude posts outside the score range
    score = int(post.rating_str.partition(" ")[0])
    if score < options.score_min:
        return 2
    if score > options.score_max:
        return 2

    # Exclude hard blacklist tags
    if blacklist.contains_post(post):
        return 1

    # Exclude soft blacklist (custom category) tags
    if options.blacklist_score_threshold > 0.0:
        # If the blacklist category doesn't exist, do nothing
        if "Blacklist" in custom.categories:
            post_score = 0.0
            for tag_list in post.tags.values():
                for tag in tag_list:
                    if tag in blacklist_in.keys():
                        post_score += blacklist_in[tag]
            if post_score >= options.blacklist_score_threshold:
                return 1

    # The post passed all checks, so it must be valid
    return 0
