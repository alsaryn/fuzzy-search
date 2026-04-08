"""Provide core logic of processing a query."""

import math
import os
import datetime
import time
import sqlite3
import pickle
import pathlib
import multiprocessing
from collections import defaultdict

import util
import progressbar
import chart


def is_post_valid(post: util.PostData, blacklist: dict) -> int:
    """Return True if post should be included in query, False otherwise."""
    # 0: Include post
    # 1: Exclude post (blacklisted)
    # 2: Exclude post (non-blacklsit reason)

    # Exclude posts if their rating isn't in the included ratings option
    if post.rating_str[-1] not in util.Options.rating:
        return 2

    # Check start/end ranges
    # Uses terrible, awful string comparisons
    if util.Options.start_date is not None:
        # Exclude posts created before the start date
        if post.created_at < util.Options.start_date:
            return 2
    if util.Options.end_date is not None:
        # Exclude posts created before the end date
        if post.created_at > util.Options.end_date:
            return 2

    # Exclude posts outside the score range
    score = int(post.rating_str.partition(" ")[0])
    if score < util.Options.score_min:
        return 2
    if score > util.Options.score_max:
        return 2

    # Exclude hard blacklist tags
    if util.post_blacklisted(post):
        return 1

    # Exclude custom category (soft) blacklist tags
    if util.Options.blacklist_score_threshold > 0.0:
        # If the blacklist category doesn't exist, do nothing
        if "Blacklist" in util.CustomCategories.categories:
            post_score = 0.0
            for tag_list in post.tags.values():
                for tag in tag_list:
                    if tag in blacklist.keys():
                        post_score += blacklist[tag]
            if post_score >= util.Options.blacklist_score_threshold:
                return 1

    # The post passed all checks, so it must be valid
    return 0


def get_valid_posts(
    query_tag_list: str, include_tags: list[str], or_tags: list[str], exclude_tags: list[str]
) -> tuple[set[int], list[util.PostData], int]:
    """Get the list of valid (not excluded) tags from the database."""
    # Returns a tuple with 2 elements.
    # Element 1: list of all post ids (in str format).
    # Element 2: list of all PostData objects corresponding to post ids.

    # While E6 contains millions of posts, queries often filter down to <10k posts.
    # Therefore, it's fine to store all these posts in memory at once.
    post_ids = set()

    # Read in from the postid database
    # Exit if the file is missing
    if not util.Filepath.cache_postid_database.exists():
        raise (
            util.CacheFileNotFound(
                message=f"Cache File Not Found: {util.Filepath.cache_postid_database}"
            )
        )

    con = sqlite3.connect(util.Filepath.cache_postid_database)
    cur = con.cursor()
    # Special case:
    # If no include and no OR tags were specified, use the set of all post ids.
    if len(include_tags) == 0 and len(or_tags) == 0:
        include_tags = [util.Options.all_posts]
    if util.Options.all_posts in include_tags:
        print(
            "WARNING:\n  Search includes entire database.\n"
            "  This search may take considerable resources to process.\n"
        )

    # Initialize the set of post ids to be the union of or tags
    if len(or_tags) != 0:
        for tag in or_tags:
            res = cur.execute("SELECT posts FROM ids WHERE tag = ?", (tag,)).fetchone()
            res = pickle.loads(res[0])
            post_ids.update(res)

    # If no or tags were found,
    # Initialize the set of valid post ids to posts with the first include tag
    if len(or_tags) == 0:
        res = cur.execute(
            "SELECT posts FROM ids WHERE tag = ?", (include_tags[0],)
        ).fetchone()
        res = pickle.loads(res[0])
        # Get the superset of all ids with the current and newly-found lists of ids
        post_ids.update(res)

        # Set the include tags to be the remaining include tags
        include_tags = include_tags[1:]

    # Sanity check: post_ids should be non-empty after initialization
    if len(post_ids) == 0:
        print("WARNING: Search involved an invalid tag with 0 associated posts.")
        return set(), [], 0

    # Filter for the posts that contain all other include tags
    for tag in include_tags:
        res = cur.execute("SELECT posts FROM ids WHERE tag = ?", (tag,)).fetchone()
        res = pickle.loads(res[0])
        post_ids.intersection_update(res)
        # Stop processing if we end up with no valid posts
        if len(post_ids) == 0:
            print("Search returned zero posts.")
            con.close()
            return set(), [], 0

    # Filter for the posts that don't contain any of the exclude tags
    for tag in exclude_tags:
        res = cur.execute("SELECT posts FROM ids WHERE tag = ?", (tag,)).fetchone()
        res = pickle.loads(res[0])
        post_ids.difference_update(res)
        # Stop processing if we end up with no valid posts
        if len(post_ids) == 0:
            print("Search returned zero posts.")
            con.close()
            return set(), [], 0
    con.close()

    if len(post_ids) > util.Options.max_query_size:
        print(f"Warning: {query_tag_list} returned {len(post_ids)} posts.")
        print(
            "  Note: This value is before posts have been pruned"
            " by options such as --min_score and --start_date."
        )
        print(
            f"  To limit RAM usage, Fuzzy Search limits searches to at most"
            f" {util.Options.max_query_size} posts."
        )
        print("  Use the --max_posts argument to increase this limit.")
        print("  As a guide, processing 1 million posts peaks at about 8 GB of RAM.")
        print(
            "  If your machine has multiple cores, process huge queries one-by-one."
        )
        return set(), [], 0

    # Use each post id to access the associated post's data from the posts database.
    post_list = []
    con = sqlite3.connect(util.Filepath.cache_post_data_database)
    cur = con.cursor()
    valid_post_ids = set()
    num_blacklisted = 0
    # Store this to be reused
    blacklist = None
    if "Blacklist" in util.CustomCategories.categories:
        blacklist = util.CustomCategories.categories["Blacklist"]

    # Determine the valid posts, and fill out post data
    for postid in sorted(list(post_ids), reverse=util.Options.descending):
        res = cur.execute(
            "SELECT * FROM posts WHERE postid = ?", (int(postid),)
        ).fetchone()
        post = util.PostData(res)

        post_code = is_post_valid(post, blacklist)
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
    if util.Options.order == util.Options.or_category:
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
        post_info = sorted(
            post_info, key=lambda v: (v[0]), reverse=util.Options.descending
        )
        # Reform the post/post id lists with the new order
        post_list = []
        valid_post_ids = set()
        for post in post_info:
            post_list.append(post[1])
            valid_post_ids.add(post[1].post_id)
    elif util.Options.order != "":
        # Find the custom category with matching name
        if util.Options.order not in util.CustomCategories.categories:
            print(
                "WARNING: Search requested filtering by custom category,"
                " but no such category exists. Skipping filtering."
            )
        else:
            category_tags = util.CustomCategories.categories[util.Options.order]
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
                post_info, key=lambda v: (v[0]), reverse=util.Options.descending
            )
            # Reform the post/post id lists with the new order
            post_list = []
            valid_post_ids = set()
            for post in post_info:
                post_list.append(post[1])
                valid_post_ids.add(post[1].post_id)

    # Return the top % of sorted posts
    print(util.Options.percent_posts_to_keep)
    if util.Options.percent_posts_to_keep < 100.0:
        # Find the number of posts to omit
        num_posts = int(len(valid_post_ids) * util.Options.percent_posts_to_keep / 100)
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


def read_in_query_list() -> None:
    """Read queries from disk into the program."""
    query_list = []
    for filename in os.listdir(util.Filepath.tags_in_dir):
        query_file = util.Filepath.tags_in_dir / filename
        # Each row is treated as a single query, containing one or more tags
        with open(query_file, "rt", encoding="utf-8") as in_file:
            for line in in_file:
                # Ignore comments and whitespace/newlines
                if line[0] != "#" and line[0] != "\n":
                    query_list.append(line.strip("\n").split(" "))

    # If no queries were found, create an example file for users to study.
    if len(query_list) == 0:
        print(
            f"No searches found in {util.Filepath.tags_in_dir}.\n"
            f"  Creating and using sample search file instead."
        )
        query_list = [
            ["domestic_cat", "slit_pupils"],
            ["loona_(helluva_boss)", "detailed_background"],
            ["uwu"],
        ]
        with open(
            util.Filepath.tags_in_dir / util.Filepath.sample_queries,
            "wt",
            encoding="utf-8",
        ) as out_file:
            for line in query_list:
                out_file.write(" ".join(line) + "\n")
    else:
        util.print_tr(
            f"Found {len(query_list)} searches in {util.Filepath.tags_in_dir}."
        )

    # Process discovered queries
    split_query_list(query_list)


def split_query_list(query_list: list[list[str]]) -> None:
    """Split a list of queries into single tasks."""
    # The input tags are all combined.
    # Initial pass: Check for any invalid tags in all queries.
    # Open a DB connection to check if the user-specified tag exists.
    if not util.Filepath.cache_postid_database.exists():
        raise (
            util.CacheFileNotFound(
                message=f"Cache File Not Found: {util.Filepath.cache_postid_database}"
            )
        )

    con = sqlite3.connect(util.Filepath.cache_postid_database)
    cur = con.cursor()
    for tag_list in query_list:
        for tag in tag_list:
            # Ignore the negation and or operators, if present
            try:
                if tag[0] == "-" or tag[0] == "~":
                    base = tag[1:]
                else:
                    base = tag
                if not util.get_category(base, print_missing_tag=False):
                    if base != util.Options.all_posts:
                        print(
                            f"Error: {base} is not a valid tag."
                            f" Full search: {tag_list}."
                        )
                        return
            except IndexError:
                print(f"Error: {tag} is not a valid tag. Full search: {tag_list}.")
                return
            # Sanity check: tag exists in the post id database
            if base != util.Options.all_posts:
                cur.execute("SELECT posts FROM ids WHERE tag = ?", (base,))
                if cur.fetchone() is None:
                    print(f"Error: {base} is not a valid tag. Full search: {tag_list}.")
                    return
    con.close()

    # Process queries in order.
    progressbar.start_new_stage("Processing Queries", len(query_list))
    start_time = time.time()

    # If we have multiple queries, create a new process for each query.
    # This enables multiprocessing to improve speed.
    if len(query_list) > 1:
        with multiprocessing.Pool() as pool:
            # imap_unordered returns as each individual job completes.
            # This means we can update the progress bar after each job completes.
            results = pool.imap_unordered(process_single_query, query_list)
            for result in results:
                progressbar.update_step_one()

    # If there are only a few queries,
    # then it's faster to split the queries into parallel sub-tasks.
    # This algorithm also is better-suited for queries with millions of posts
    # to avoid running out of memory.
    else:
        # Queries will be processed sequentially (single core), but we free up cores
        # to use on parallelizing sub-tasks of query analysis.
        # TODO: Implement using multiple cores to speed up charts/recommendations
        util.Options.parallelize_query_subtask = True
        for tag_list in query_list:
            process_single_query(tag_list)
    duration = time.time() - start_time
    util.print_tr(f"Time to process {len(query_list)} searches: {round(duration, 2)} s")


def process_single_query(tag_list: list[str]) -> None:
    """Create directory containing an individual query's analysis."""
    util.print_tr(f"  Pre-processing {tag_list}")

    # Split the input tags into include/or/exclude tags.
    include_tags = []
    or_tags = []
    exclude_tags = []
    for tag in tag_list:
        # Check for the or and negation operators.
        if tag[0] == "-":
            exclude_tags.append(tag[1:])
        if tag[0] == "~":
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
        util.print_tr(f"Skipping Search (No posts found): {tag_list}.\n")
        progressbar.update_step_one()
        return

    # [--- Filename ---]
    # The folder storing this query's output depends on these metrics
    scores_list = []
    favorites_list = []
    comments_list = []
    # Iterate over each valid post
    for post in post_data:
        # rating = score favs comments_count rating_char
        rating = post.rating_str.split(" ")
        scores_list.append(int(rating[0]))
        favorites_list.append(int(rating[1]))
        # Remove the leading "C" from comments_count
        comments_list.append(int(rating[2][1:]))

    # Store this info so we can pass it on to a later function
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

    output_dir = util.Filepath.tags_out_dir / folder_name

    if util.Options.url_only:
        process_tags_url(output_dir, post_data)
        # If we output URL information, skip all other data analysis
        return

    # Don't recalculate data if we find th output folder already exists
    if output_dir.exists():
        util.print_tr(f"  {folder_name} already exists, skipping search.")
        progressbar.update_step_one()
    else:
        util.print_tr(f"  Analyzing: {folder_name}")
        # Create the folder housing the output for this query
        os.mkdir(output_dir)
        # Generate and save analysis data to disk
        data_analysis_for_single_query(
            tag_list, output_dir, post_ids, post_data, query_stats
        )
        util.print_tr(f"  Finished analysis: {folder_name}")
        progressbar.update_step_one()


def process_tags_url(output_dir: pathlib.Path, post_list: list[util.PostData]) -> None:
    """Print post URLs."""
    if not util.Options.url and not util.Options.url_only:
        return

    # If we're only outputting URLs, then:
    # 1. change the filename to be the query tags
    # 2. Save the file in the Downloads directory
    if util.Options.url_only:
        util.print_tr(str(output_dir))
        urls_filename = output_dir.stem + ".txt"
        output_dir = util.Filepath.downloads_dir
    else:
        urls_filename = util.Filepath.urls_filename
    # Write each posts' URL to disk
    with open(output_dir / urls_filename, "wt", encoding="utf-8") as out_file:
        # Iterate over each valid post
        for row in post_list:
            if util.Options.url_mode == "md5":
                out_file.write(f"{row.md5}\n")
            elif util.Options.url_mode == "url":
                url = (
                    f"https://static1.e621.net/data/{row.md5[0:2]}"
                    f"/{row.md5[2:4]}/{row.md5}.{row.file_ext}"
                )
                out_file.write(f"{url}\n")
            elif util.Options.url_mode == "full":
                filename = f"{row.post_id}.{row.file_ext}"
                # Note: All URLs begin with 'https://static1.e621.net/data/',
                # which is omitted here for space.
                # The remaining URL first duplicates the first four characters
                # of the MD5 hash to index into two folders.
                # Then we have the md5 hash in full and finally the file extension.
                url = (
                    f"https://static1.e621.net/data/{row.md5[0:2]}/"
                    f"{row.md5[2:4]}/{row.md5}.{row.file_ext}"
                )
                # Convert file size from bytes into megabytes
                file_size = round(int(row.file_size) / 1048576, 1)
                out_file.write(f"{filename}\t{url}\t{file_size}\n")


def save_post_sources(output_dir: pathlib.Path, post_ids: set[int]):
    """Write out individual/per-post data (primarily sources) to markdown."""
    if not util.Filepath.cache_post_data_sources.exists():
        raise (
            util.CacheFileNotFound(
                message=f"File Not Found: {util.Filepath.cache_post_data_sources}"
            )
        )
    # Connect to the database.
    con = sqlite3.connect(util.Filepath.cache_post_data_sources)
    # Create the cursor.
    cur = con.cursor()

    with open(
        output_dir / util.Filepath.per_post_sources, "wt", encoding="utf-8"
    ) as out_file:
        for post_id in post_ids:
            cur.execute("SELECT source FROM posts WHERE postid = ?", (post_id,))
            # Sources are stored as a newline-delimited string
            content = f"#### {post_id}\n"
            for source in cur.fetchone()[0].split("\n"):
                content += f"{source}\n"
            content += "\n"
            out_file.write(content)


def save_post_descriptions(output_dir: pathlib.Path, post_ids: set[int]):
    """Write out individual/per-post data (primarily descriptions) to markdown."""
    if not util.Filepath.cache_post_data_descriptions.exists():
        raise (
            util.CacheFileNotFound(
                message=f"File Not Found: {util.Filepath.cache_post_data_descriptions}"
            )
        )
    # Connect to the database.
    con = sqlite3.connect(util.Filepath.cache_post_data_descriptions)
    # Create the cursor.
    cur = con.cursor()

    with open(
        output_dir / util.Filepath.per_post_descriptions, "wt", encoding="utf-8"
    ) as out_file:
        for post_id in post_ids:
            cur.execute("SELECT description FROM posts WHERE postid = ?", (post_id,))
            # Descriptions are stored as a single string
            content = f"#### {post_id}\n{cur.fetchone()[0]}\n\n"
            out_file.write(util.get_tr(content))


def save_post_durations(output_dir: pathlib.Path, post_ids: set[int]):
    """Write out individual/per-post data (primarily durations) to markdown."""
    if not util.Filepath.cache_post_data_durations.exists():
        raise (
            util.CacheFileNotFound(
                message=f"File Not Found: {util.Filepath.cache_post_data_durations}"
            )
        )
    # Connect to the database.
    con = sqlite3.connect(util.Filepath.cache_post_data_durations)
    # Create the cursor.
    cur = con.cursor()

    with open(
        output_dir / util.Filepath.per_post_durations, "wt", encoding="utf-8"
    ) as out_file:
        for post_id in post_ids:
            cur.execute("SELECT duration FROM posts WHERE postid = ?", (post_id,))
            # Durations are stored as a float.
            # If the duration is zero or not-applicable,
            # then there is no entry in the database.
            res = cur.fetchone()
            if res is None:
                # out_file.write(f"#### {post_id}\n\n")
                pass
            else:
                # Convert time from seconds into minutes and seconds
                seconds = float(res[0])
                minutes = math.floor(seconds / 60)
                seconds = math.ceil(seconds - (minutes * 60))

                # Do some formatting to get varied time formats to line up
                # 10:57 (717-second video)
                #  1:57 (117-second video)
                #    57 (57-second video)
                #     7 (7-second video)

                if minutes >= 1:
                    minutes = str(minutes).rjust(2, " ")
                    # Add a leading 0 to seconds
                    seconds = str(seconds).rjust(2, "0")
                    out_file.write(f"#### {post_id}\n {minutes}:{seconds}\n")
                else:
                    seconds = str(seconds).rjust(5, " ")
                    out_file.write(f"#### {post_id}\n {seconds}\n")


def save_post_tags(
    output_dir: pathlib.Path, post_list: list[util.PostData], query_stats: dict
) -> None:
    """Write out individual/per-post data (primarily tags) to markdown."""
    with open(
        output_dir / util.Filepath.per_post_data, "wt", encoding="utf-8"
    ) as out_file:
        # Numerical Stats
        final_stats = "#### Search Statistics::\n"
        final_stats += f"Total Posts: {len(post_list)}\n"
        final_stats += f"  (Blacklisted: {query_stats["num_blacklisted"]})\n"
        final_stats += (
            f"Avg Score: {query_stats['score_avg']}"
            f" ({query_stats['score_med']} median)\n"
        )
        final_stats += (
            f"Avg Favs: {query_stats['fav_avg']} ({query_stats['fav_med']} median)\n"
        )
        final_stats += (
            f"Avg Comments: {query_stats['com_avg']}"
            f" ({query_stats['com_med']} median)\n\n"
        )
        out_file.write(final_stats)

        # Per-post data
        for row in post_list:
            # header
            content = f"#### {row.post_id}\n"
            # Print the rating string in full
            content += f"{row.rating_str}\n"
            # Print the date created
            content += f"Posted: {row.created_at}\n"
            # For each non-empty tag category, print a header + list of tags.
            for item in row.tags.items():
                if len(item[1]) > 0:
                    # Print the category.
                    # Special case: plural for artists
                    if item[0] == "artist":
                        content += "Artists\n"
                    else:
                        # General case: first letter becomes uppercase.
                        content += f"{item[0][0].upper()}{item[0][1:]}\n"

                    # Print all the tags
                    for tag in item[1]:
                        content += f"\t{tag}\n"
            # Add an ending spacer
            content += "\n"
            out_file.write(content)


def save_tag_counts_e6_category(
    output_dir: pathlib.Path, post_list: list[util.PostData]
) -> dict[str, dict[str, int]]:
    """Write out tag counts (split by E6 category) to markdown."""
    # Pass 2: Write out counts of each tag, descending sort, split by E6 category.
    with open(
        output_dir / util.Filepath.tag_counts_e6_category, "wt", encoding="utf-8"
    ) as out_file:
        # Data structure to keep track of each tallied post.
        # Each dict maps a tag to its occurrences in the queried post set
        tag_counts = {
            "artist": defaultdict(int),
            "contributor": defaultdict(int),
            "copyright": defaultdict(int),
            "character": defaultdict(int),
            "species": defaultdict(int),
            "general": defaultdict(int),
            "invalid": defaultdict(int),
            "meta": defaultdict(int),
            "lore": defaultdict(int),
        }
        for row in post_list:
            # Add each tag to the relevant category
            for category, tag_list in row.tags.items():
                for post_tag in tag_list:
                    tag_counts[category][post_tag] += 1
        # Sort data and write tag counts for each category to disk.
        for category, in_dict in tag_counts.items():
            out_file.write(f"### {category[0].upper()}{category[1:]}\n")
            out_file.write(util.print_double_sorted_list(in_dict))

    # Reuse tag_counts to fill out the custom category lists
    return tag_counts


def save_tag_counts_custom_category(
    output_dir: pathlib.Path,
    post_list: list[util.PostData],
    tag_counts: dict[str, dict[str, int]],
) -> None:
    """Write out tag counts (split by user-set custom category) to markdown."""
    # Data structure to keep track of each tallied post.
    # Each dict maps a tag to its occurrences in the queried post set
    custom_tallies = {}
    # custom_tallies's categories will be the custom categories
    for custom_category in util.CustomCategories.categories:
        custom_tallies[custom_category] = {}

    # Iterate over every unique tag found the queried posts
    for category_tally in tag_counts.values():
        for post_tag, tag_tally in category_tally.items():
            # Determine if the tag is in any of the custom categories.
            for (
                custom_category,
                custom_tag_list,
            ) in util.CustomCategories.categories.items():
                if post_tag in custom_tag_list.keys():
                    # Set the tally of that tag's occurrences
                    custom_tallies[custom_category][post_tag] = tag_tally

    # Write out counts of each tag, split by custom category.
    with open(
        output_dir / util.Filepath.tag_counts_custom_category, "wt", encoding="utf-8"
    ) as out_file:
        # Write the general stats to disk at the top of the output file.
        out_str = (
            f"### General Stats:\nTotal Posts:"
            f" {len(post_list)}\nTotal Tags Per Category:\n"
        )
        for custom_category, custom_tag_list in custom_tallies.items():
            total = 0
            for tag_count in custom_tag_list.values():
                total += tag_count
            out_str += (
                f"  {custom_category}:"
                f" {total} ({round(total/len(post_list), 2)} per post)\n"
            )
        out_str += "\n"
        out_file.write(out_str)

        # Sort data and write tag counts for each category to disk.
        for custom_category, custom_tag_list in custom_tallies.items():
            out_file.write(f"### {custom_category}\n")
            out_file.write(util.print_double_sorted_list(custom_tag_list))


def save_bar_charts(
    tag_list: list[str], output_dir: pathlib.Path, post_list: list[util.PostData]
) -> None:
    """Generate bar charts plotting categorical data."""
    # The custom charts are lists of relevant tags.
    # Convert the list to a dict.
    chart_data = {}
    for chart_title, main_chart_tag_list in util.BarCharts.categories.items():
        chart_data[chart_title] = {}
        for chart_tag_list in main_chart_tag_list:
            chart_data[chart_title][" ".join(chart_tag_list)] = 0

    # Iterate over each valid post
    for row in post_list:
        # Flatten the e6 tag category lists into a single list
        post_tag_list = [tag for category in row.tags.values() for tag in category]
        # Scan through each type of bar chart
        for chart_title, main_chart_tag_list in chart_data.items():
            # Scan through all rows of tags in the bar chart
            for chart_tag_list in main_chart_tag_list:
                has_all_tags = True
                for tag in chart_tag_list.split(" "):
                    # Negation tags should not be present
                    if tag[0] == "-":
                        if tag[1:] in post_tag_list:
                            has_all_tags = False
                            break
                    # All other tags should be present
                    elif tag not in post_tag_list:
                        has_all_tags = False
                        break
                if has_all_tags:
                    # Increment the count of this tag.
                    main_chart_tag_list[chart_tag_list] += 1

    # Normalize counts; make each value the ratio of posts with this tag in the query.
    post_list_len = len(post_list)
    for chart_title, main_chart_tag_list in chart_data.items():
        for tag, count in main_chart_tag_list.items():
            main_chart_tag_list[tag] = count / post_list_len

    # Plot and save charts to disk
    for chart_title, main_chart_tag_list in chart_data.items():
        chart.generate_bar_chart(
            f"{chart_title}:\n{" ".join(tag_list)}",
            output_dir / f"Bar {chart_title}.png",
            main_chart_tag_list,
        )


def save_scatter_plot_custom(
    tag_list: list[str], output_dir: pathlib.Path, post_list: list[util.PostData]
) -> None:
    """Generate scatter plot mapping post upload date and custom category score."""
    # X-axis is the upload date, which is shared for every custom category.
    x_data = []
    # The y-axis data for a post depends on the custom category score.
    category_to_y_data = {}
    for category in util.CustomCategories.categories:
        category_to_y_data[category] = []
    # Iterate over each queried post
    for post_index, row in enumerate(post_list):
        # Add the upload date (matplotlib recognizes python's datetime format)
        # as the x data for this post.
        date = row.created_at.split("-")
        x_data.append(
            datetime.date(day=int(date[2]), month=int(date[1]), year=int(date[0]))
        )
        # Initialize this post's y data for all categories to be zero
        for category in category_to_y_data.values():
            category.append(0)

        # Add each general tag to the relevant category
        for post_tag_list in row.tags.values():
            for post_tag in post_tag_list:
                # Determine if the tag is in one of the custom categories
                for (
                    custom_category,
                    custom_tag_list,
                ) in util.CustomCategories.categories.items():
                    if post_tag in custom_tag_list.keys():
                        # Increment the count in the custom category by weight.
                        category_to_y_data[custom_category][
                            post_index
                        ] += custom_tag_list[post_tag]

    # category_to_total_count: calculate the total tally for each category.
    # Used to sort categories based on highest tally,
    # and to add the tally and average per post to chart legend.
    category_to_total_count = {}
    for category in util.CustomCategories.categories:
        category_to_total_count[category] = 0
    # Go through each post in each category and add it's score to the total.
    for custom_category, custom_tag_list in category_to_y_data.items():
        # For each post in this category...
        total = 0
        for post in custom_tag_list:
            # Add the post's tally to the category total
            total += post
        category_to_total_count[custom_category] = total
    # Sort categories in order of most common to least common.
    category_to_total_count = dict(
        sorted(category_to_total_count.items(), key=lambda kv: (kv[1]), reverse=True)
    )

    # Chart legends: capitalized category names, along with category tallies/metrics.
    category_to_chart_legend = {}
    for category, total in category_to_total_count.items():
        category_to_chart_legend[category] = (
            f"{category} {round((total / len(post_list)), 2)} ({total})"
        )

    chart.generate_scatter_plot_all_custom_categories(
        f"Custom Categories:\n{" ".join(tag_list)}",
        # f"Custom Categories:\nArtist B",
        output_dir / util.Filepath.scatter_plot_custom,
        category_to_chart_legend,
        util.CustomCategories.colors,
        category_to_y_data,
        x_data,
    )

    # Plot proportional (ascending/descending score) charts for each custom category
    for category in util.CustomCategories.categories:
        chart.generate_scatter_plot_single_category(
            f"{category}:\n{" ".join(tag_list)}",
            # f"{category}:\nArtist B",
            output_dir / f"Percentile {category}.png",
            category_to_chart_legend[category],
            util.CustomCategories.colors[category],
            category_to_y_data[category],
        )


def save_scatter_plot_upload_date(
    tag_list: list[str], output_dir: pathlib.Path, post_list: list[util.PostData]
) -> None:
    """Generate scatter plot mapping post score against post upload date."""
    # X-axis is the upload date, y-axis is the post score
    x_data = []
    y_data = []
    # Iterate over each queried post
    for post in post_list:
        # Add the upload date (matplotlib recognizes python's datetime format)
        # as the x data for this post.
        date = post.created_at.split("-")
        x_data.append(
            datetime.date(day=int(date[2]), month=int(date[1]), year=int(date[0]))
        )
        score = int(post.rating_str.split(" ")[0])
        # clamp negative scores
        score = max(0, score)
        y_data.append(score)

    chart.generate_scatter_plot_post_score(
        f"Post Score by Upload Date:\n{" ".join(tag_list)}",
        output_dir / util.Filepath.scatter_plot_score_upload_date,
        x_data,
        y_data,
        "Year",
    )


def save_scatter_plot_tag_count(
    tag_list: list[str], output_dir: pathlib.Path, post_list: list[util.PostData]
) -> None:
    """Generate scatter plot mapping post score against post total tag count."""
    # X-axis is the tag count, y-axis is the post score
    x_data = []
    y_data = []
    # Iterate over each queried post
    for post in post_list:
        # Add the upload date (matplotlib recognizes python's datetime format)
        # as the x data for this post.
        tag_count = 0
        for category in post.tags.values():
            tag_count += len(category)

        x_data.append(tag_count)
        score = int(post.rating_str.split(" ")[0])
        # clamp negative scores
        score = max(0, score)
        y_data.append(score)

    chart.generate_scatter_plot_post_score(
        f"Post Score by Tag Count:\n{" ".join(tag_list)}",
        output_dir / util.Filepath.scatter_plot_score_tag_count,
        x_data,
        y_data,
        "Tag Count",
    )


def save_scatter_plot_custom_tag_count(
    tag_list: list[str], output_dir: pathlib.Path, post_list: list[util.PostData]
) -> None:
    """Generate scatter plot mapping post score against post total tag count."""
    # Make one scatter plot per custom category
    for custom_category, custom_tag_list in util.CustomCategories.categories.items():
        # X-axis is the total custom category weight for all tags in the post,
        # y-axis is the post score
        x_data = []
        y_data = []
        # Iterate over each queried post
        for post in post_list:
            # Add the upload date (matplotlib recognizes python's datetime format)
            # as the x data for this post.
            post_weight = 0
            for category in post.tags.values():
                for post_tag in category:
                    if post_tag in custom_tag_list.keys():
                        post_weight += custom_tag_list[post_tag]

            x_data.append(post_weight)
            score = int(post.rating_str.split(" ")[0])
            # clamp negative scores
            score = max(0, score)
            y_data.append(score)

        chart.generate_scatter_plot_post_score(
            f"Post Score by Custom Category Weight:\n{" ".join(tag_list)}",
            output_dir / f"Scatter {custom_category}.png",
            x_data,
            y_data,
            "Category Weight",
        )


def data_analysis_for_single_query(
    tag_list: list[str],
    output_dir: pathlib.Path,
    post_ids: set[int],
    post_list: list[util.PostData],
    query_stats: dict,
) -> None:
    """Process tags for a single input."""
    # We will end up writing to several different files across multiple passes:
    # Per-post data (data split up by post id)
    if util.Options.posts:
        save_post_tags(output_dir, post_list, query_stats)
    if util.Options.source:
        save_post_sources(output_dir, post_ids)
    if util.Options.description:
        save_post_descriptions(output_dir, post_ids)
    if util.Options.duration:
        save_post_durations(output_dir, post_ids)
    # File URLS
    if util.Options.url:
        process_tags_url(output_dir, post_list)
    if util.Options.counts or util.Options.counts_custom:
        # Tag counts split by E6 categories
        tag_counts = save_tag_counts_e6_category(output_dir, post_list)
        if util.Options.counts_custom:
            # Tag counts split by custom categories
            save_tag_counts_custom_category(output_dir, post_list, tag_counts)
    if util.Options.bar_charts:
        # Bar Charts
        save_bar_charts(tag_list, output_dir, post_list)
    if util.Options.charts_custom:
        # Scatter plots
        save_scatter_plot_custom(tag_list, output_dir, post_list)
    if util.Options.score:
        # Scatter plots
        # TODO: change
        save_scatter_plot_upload_date(tag_list, output_dir, post_list)
        # save_scatter_plot_tag_count(tag_list, output_dir, post_list)
        # save_scatter_plot_custom_tag_count(tag_list, output_dir, post_list)

    # Find similar tags, using a ranking approach based on TF-IDF.
    if util.Options.recommended:
        # If the number of posts is small,
        # use a more efficient similarity algorithm that scans the queried posts
        if len(post_list) < 10000:
            list_similar_tags_sparse(output_dir, post_ids, post_list)
        else:
            list_similar_tags_dense(output_dir, post_ids)

    # Create Obsidian Vault
    if len(post_list) < util.Options.graph:
        generate_obsidian_graph(output_dir, post_list)


def list_similar_tags_sparse(
    output_dir: pathlib.Path, post_ids: set[int], post_data: list[util.PostData]
) -> None:
    """Create a text file with similar/recommended tags to the queried tags."""
    # Finds similar tags via a formula derived from TF-IDF.
    # Tags that do not co-occur with the query (similarity score of 0) are omitted.

    # This algorithm's implementation is optimized for sparse (small) queries.
    # It searches for unique tags in the list of queried posts (not the tag database).

    # Assemble a set of all unique tags in all queried posts.
    unique_tags = {}
    for category in util.Options.recommended_tags:
        unique_tags[category] = set()
    for post in post_data:
        # # Only calculate data for tags that are of a certain category
        for category in util.Options.recommended_tags:
            unique_tags[category].update(post.tags[category])

    # Connect to the database of tags to post ids.
    con = sqlite3.connect(util.Filepath.cache_postid_database)
    cur = con.cursor()
    # Store tags and their similarity plus relevant info to output.
    ranked_tags = {}
    for category, tag_set in unique_tags.items():
        ranked_tags[category] = {}
        for tag in tag_set:
            posts = cur.execute("SELECT posts FROM ids WHERE tag = ?", (tag,))
            posts = pickle.loads(posts.fetchone()[0])
            inter = post_ids.intersection(posts)
            inter_len = len(inter)
            # Add posts with this tag that are shared with the queried post set.
            if inter_len > 0:
                post_len = len(posts)
                # This logarithm ends up devaluing extremely niche tags (1-9 posts),
                # while increasing the rank of popular tags.
                # This log's score multiplier is applied to the ratio of queried posts
                # to posts in the database with that tag.
                # The resulting number should be high if the tag
                # 1) applies to many posts in the set (TF) and
                # 2) the tag isn't that numerous in the entire collection (IDF).
                hits = math.log10(inter_len)
                distractor = inter_len / post_len
                ranked_tags[category][tag] = (
                    hits * distractor,
                    inter_len,
                    post_len,
                    distractor,
                )
    con.close()

    # Sort and print each list of tags.
    posts_len = len(post_ids)
    with open(
        output_dir / util.Filepath.similar_tags, mode="wt", encoding="utf-8"
    ) as out_file:
        for category, tag_dict in ranked_tags.items():
            out_file.write(f"### {category}\n")
            out_file.write("#set|#db    %set| tag\n")
            num_skipped_tags = 0
            for tag, val in sorted(
                tag_dict.items(), key=lambda kv: (kv[1][0]), reverse=True
            ):
                set_percentage = int((val[1] / posts_len) * 100)
                # Only write tags at or above the threshold
                if set_percentage >= util.Options.recommended_tag_threshold:
                    out_file.write(
                        f"{str(val[1]).rjust(4)}|{str(val[2]).ljust(7)}"
                        f" {str(set_percentage).rjust(3)}| {tag}\n"
                    )
                else:
                    num_skipped_tags += 1
            if num_skipped_tags > 0:
                out_file.write(
                    f"  (... plus {num_skipped_tags} other tags found in less than"
                    f" {util.Options.recommended_tag_threshold}%"
                    f" of the searched posts)\n"
                )
            out_file.write("\n")


def list_similar_tags_dense(output_dir: pathlib.Path, post_ids: set[int]) -> None:
    """Create a text file with similar/recommended tags to the queried tags."""
    # Finds similar tags via a formula derived from TF-IDF.
    # Tags that do not co-occur with the query (similarity score of 0) are omitted.

    # This algorithm's implementation is optimized for dense (large) queries.
    # It does a linear scan of the tag database, rather than scanning all queried posts.

    # Store tags and their similarity plus relevant info to output.
    ranked_tags = {}
    for category in util.Options.recommended_tags:
        ranked_tags[category] = []

    # Connect to the database of tags to post ids.
    con = sqlite3.connect(util.Filepath.cache_postid_database)
    cur = con.cursor()
    # Compare all other tags.
    cur.execute("SELECT * FROM ids")
    row = cur.fetchone()
    while row is not None:
        tag = row[0]
        # Only calculate data for tags that are of a certain output type.
        category = util.get_category(tag)
        if category in util.Options.recommended_tags:
            posts = pickle.loads(row[1])
            inter = post_ids.intersection(posts)
            inter_len = len(inter)
            # Add posts with this tag that are shared with the queried post set.
            if inter_len > 0:
                post_len = len(posts)
                # This logarithm ends up devaluing extremely niche tags (1-9 posts),
                # while increasing the rank of popular tags.
                # This log's score multiplier is applied to the ratio of queried posts
                # to posts in the database with that tag.
                # The resulting number should be high if the tag
                # 1) applies to many posts in the set (TF) and
                # 2) the tag isn't that numerous in the entire collection (IDF).
                hits = math.log10(inter_len)
                distractor = inter_len / post_len
                ranked_tags[category].append(
                    (hits * distractor, tag, inter_len, post_len, distractor)
                )
        # Prepare to process the next row of data.
        row = cur.fetchone()
    con.close()

    # Sort and print each list of tags.
    posts_len = len(post_ids)
    with open(
        output_dir / util.Filepath.similar_tags, mode="wt", encoding="utf-8"
    ) as out_file:
        for category, tag_list in ranked_tags.items():
            out_file.write(f"### {category}\n")
            out_file.write("#set|#db    %set| tag\n")
            num_skipped_tags = 0
            for item in sorted(tag_list, key=lambda val: (val[0]), reverse=True):
                set_percentage = int((item[2] / posts_len) * 100)
                # Only write tags at or above the threshold
                if set_percentage >= util.Options.recommended_tag_threshold:
                    out_file.write(
                        f"{str(item[2]).rjust(4)}|{str(item[3]).ljust(7)}"
                        f" {str(set_percentage).rjust(3)}| {item[1]}\n"
                    )
                else:
                    num_skipped_tags += 1
            if num_skipped_tags > 0:
                out_file.write(
                    f"  (... plus {num_skipped_tags} other tags found in less than"
                    f" {util.Options.recommended_tag_threshold}%"
                    f" of the searched posts)\n"
                )
            out_file.write("\n")


def generate_obsidian_graph(
    output_dir: pathlib.Path, post_data: list[util.PostData]
) -> None:
    """Plot each question as an Obsidian note with tags."""
    # Performance Note: Obsidian is a text editor first, and graph/visualizer second.
    # This means Obsidian is excellent for diving deeper into individual posts.
    # On the other hand, Obsidian struggles to graph queries with a high post count.

    # Create graph directory
    graph_dir = output_dir / "Obsidian"
    graph_dir.mkdir()

    # Iterate over each valid post
    for post in post_data:
        # Create an Obsidian note for this post
        with open(graph_dir / f"{post.post_id}.md", "wt", encoding="utf-8") as out_file:
            # These tags form links on Obsidian's graph view
            # out_file.write("---\ntags:\n")
            # for tag in post.tags:
            #     out_file.write(f"  - {tag}\n")
            # out_file.write("---\n")

            # The below format gives more information while in the "context" view
            # content += f"#{tag}\n"

            content = ""
            # Print the rating string in full
            content += f"{post.rating_str}\n"
            # Print the date created
            content += f"Posted: {post.created_at}\n"
            # For each non-empty tag category, print a header + list of tags.
            for item in post.tags.items():
                if len(item[1]) > 0:
                    # Print the category.
                    # Special case: plural for artists
                    if item[0] == "artist":
                        content += "Artists\n"
                    else:
                        # General case: first letter becomes uppercase.
                        content += f"{item[0][0].upper()}{item[0][1:]}\n"
                    # Print all the tags
                    for tag in item[1]:
                        content += f"#{tag}\n"
            out_file.write(content)
