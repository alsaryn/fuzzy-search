"""Provide various modes to analyze a search."""

import math
import datetime
import sqlite3
import pickle
import pathlib
from collections import defaultdict

import util
import chart
from utilfilepath import filepath
from utiltext import translate
from utiloptions import options
from util import bar, custom, tag_to_category


def analyze_single_query(
    tag_list: list[str],
    output_dir: pathlib.Path,
    post_ids: set[int],
    post_list: list[util.PostData],
    query_stats: dict,
) -> None:
    """Process tags for a single input."""
    # We will end up writing to several different files across multiple passes:
    # Per-post data (data split up by post id)
    if options.posts:
        save_post_tags(output_dir, post_list, query_stats)
    if options.source:
        save_post_sources(output_dir, post_list)
    if options.description:
        save_post_descriptions(output_dir, post_list)
    if options.duration:
        save_post_durations(output_dir, post_list)
    # File URLS
    if options.url:
        process_tags_url(output_dir, post_list)
    if options.counts or options.counts_custom:
        # Tag counts split by E6 categories
        tag_counts = save_tag_counts_e6_category(output_dir, post_list)
        if options.counts_custom:
            # Tag counts split by custom categories
            save_tag_counts_custom_category(output_dir, post_list, tag_counts)
    if options.bar_charts:
        # Bar Charts
        save_bar_charts(tag_list, output_dir, post_list)
    if options.charts_custom:
        # Scatter plots
        save_scatter_plot_custom(tag_list, output_dir, post_list)
    if options.score:
        # Scatter plots
        save_scatter_plot_upload_date(tag_list, output_dir, post_list)
        # save_scatter_plot_tag_count(tag_list, output_dir, post_list)
        # save_scatter_plot_custom_tag_count(tag_list, output_dir, post_list)

    # Find individual tags similar to posts in the query.
    if options.recommended:
        # If the number of posts is small,
        # use a more efficient similarity algorithm that scans the queried posts
        if len(post_list) < 10000:
            list_similar_tags_sparse(output_dir, post_ids, post_list)
        else:
            list_similar_tags_dense(output_dir, post_ids)

    # Create Obsidian Vault
    if len(post_list) < options.graph:
        generate_obsidian_graph(output_dir, post_list)


def save_post_tags(
    output_dir: pathlib.Path, post_list: list[util.PostData], query_stats: dict
) -> None:
    """Write out individual/per-post data (primarily tags) to markdown."""
    with open(output_dir / filepath.per_post_data, "wt", encoding="utf-8") as out_file:
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


def save_post_sources(output_dir: pathlib.Path, post_list: list[util.PostData]):
    """Write out individual/per-post data (primarily sources) to markdown."""
    if not filepath.cache_post_data_sources.exists():
        raise (
            util.CacheFileNotFound(
                message=f"File Not Found: {filepath.cache_post_data_sources}"
            )
        )
    # Connect to the database.
    con = sqlite3.connect(filepath.cache_post_data_sources)
    # Create the cursor.
    cur = con.cursor()

    with open(
        output_dir / filepath.per_post_sources, "wt", encoding="utf-8"
    ) as out_file:
        for post in post_list:
            cur.execute(  "SELECT source FROM posts WHERE postid = ?",(post.post_id,))
            # Sources are stored as a newline-delimited string
            content = f"#### {post.post_id}\n"
            for source in cur.fetchone()[0].split("\n"):
                content += f"{source}\n"
            content += "\n"
            out_file.write(content)


def save_post_descriptions(output_dir: pathlib.Path, post_list: list[util.PostData]):
    """Write out individual/per-post data (primarily descriptions) to markdown."""
    if not filepath.cache_post_data_descriptions.exists():
        raise (
            util.CacheFileNotFound(
                message=f"File Not Found: {filepath.cache_post_data_descriptions}"
            )
        )
    # Connect to the database.
    con = sqlite3.connect(filepath.cache_post_data_descriptions)
    # Create the cursor.
    cur = con.cursor()

    with open(
        output_dir / filepath.per_post_descriptions, "wt", encoding="utf-8"
    ) as out_file:
        for post in post_list:
            cur.execute("SELECT description FROM posts WHERE postid = ?",
                        (post.post_id,))
            # Descriptions are stored as a single string
            content = f"#### {post.post_id}\n{cur.fetchone()[0]}\n\n"
            out_file.write(translate.text(content))


def save_post_durations(output_dir: pathlib.Path, post_list: list[util.PostData]):
    """Write out individual/per-post data (primarily durations) to markdown."""
    if not filepath.cache_post_data_durations.exists():
        raise (
            util.CacheFileNotFound(
                message=f"File Not Found: {filepath.cache_post_data_durations}"
            )
        )
    # Connect to the database.
    con = sqlite3.connect(filepath.cache_post_data_durations)
    # Create the cursor.
    cur = con.cursor()

    with open(
        output_dir / filepath.per_post_durations, "wt", encoding="utf-8"
    ) as out_file:
        for post in post_list:
            cur.execute("SELECT duration FROM posts WHERE postid = ?", (post.post_id,))
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
                    out_file.write(f"#### {post.post_id}\n {minutes}:{seconds}\n")
                else:
                    seconds = str(seconds).rjust(5, " ")
                    out_file.write(f"#### {post.post_id}\n {seconds}\n")


def process_tags_url(output_dir: pathlib.Path, post_list: list[util.PostData]) -> None:
    """Print post URLs."""
    if not options.url and not options.url_only:
        return

    # If we're only outputting URLs, then:
    # 1. change the filename to be the query tags
    # 2. Save the file in the Posts directory
    if options.url_only:
        print(translate.text(str(output_dir)))
        urls_filename = output_dir.stem + ".txt"
        output_dir = filepath.downloads_dir
    else:
        urls_filename = filepath.urls_filename
    # Write each posts' URL to disk
    with open(output_dir / urls_filename, "wt", encoding="utf-8") as out_file:
        # Iterate over each valid post
        for row in post_list:
            if options.url_mode == "md5":
                out_file.write(f"{row.md5}\n")
            elif options.url_mode == "url":
                url = (
                    f"https://static1.e621.net/data/{row.md5[0:2]}"
                    f"/{row.md5[2:4]}/{row.md5}.{row.file_ext}"
                )
                out_file.write(f"{url}\n")
            elif options.url_mode == "full":
                filename = f"{row.post_id}.{row.file_ext}"
                # All URLs begin with 'https://static1.e621.net/data/'
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


def save_tag_counts_e6_category(
    output_dir: pathlib.Path, post_list: list[util.PostData]
) -> dict[str, dict[str, int]]:
    """Write out tag counts (split by E6 category) to markdown."""
    # Pass 2: Write out counts of each tag, descending sort, split by E6 category.
    with open(
        output_dir / filepath.tag_counts_e6_category, "wt", encoding="utf-8"
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
    for custom_category in custom.categories:
        custom_tallies[custom_category] = {}

    # Iterate over every unique tag found the queried posts
    for category_tally in tag_counts.values():
        for post_tag, tag_tally in category_tally.items():
            # Determine if the tag is in any of the custom categories.
            for (
                custom_category,
                custom_tag_list,
            ) in custom.categories.items():
                if post_tag in custom_tag_list.keys():
                    # Set the tally of that tag's occurrences
                    custom_tallies[custom_category][post_tag] = tag_tally

    # Write out counts of each tag, split by custom category.
    with open(
        output_dir / filepath.tag_counts_custom_category, "wt", encoding="utf-8"
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
    for chart_title, main_chart_tag_list in bar.charts.items():
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
        chart.bar_chart(
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
    for category in custom.categories:
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
                ) in custom.categories.items():
                    if post_tag in custom_tag_list.keys():
                        # Increment the count in the custom category by weight.
                        category_to_y_data[custom_category][
                            post_index
                        ] += custom_tag_list[post_tag]

    # category_to_total_count: calculate the total tally for each category.
    # Used to sort categories based on highest tally,
    # and to add the tally and average per post to chart legend.
    category_to_total_count = {}
    for category in custom.categories:
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

    chart.scatter_custom_categories(
        f"Custom Categories:\n{" ".join(tag_list)}",
        # f"Custom Categories:\nArtist B",
        output_dir / filepath.scatter_plot_custom,
        category_to_chart_legend,
        custom.colors,
        category_to_y_data,
        x_data,
    )

    # Plot proportional (ascending/descending score) charts for each custom category
    for category in custom.categories:
        chart.scatter_custom_category(
            f"{category}:\n{" ".join(tag_list)}",
            # f"{category}:\nArtist B",
            output_dir / f"Percentile {category}.png",
            category_to_chart_legend[category],
            custom.colors[category],
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

    chart.scatter_post_score(
        f"Post Score by Upload Date:\n{" ".join(tag_list)}",
        output_dir / filepath.scatter_plot_score_upload_date,
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

    chart.scatter_post_score(
        f"Post Score by Tag Count:\n{" ".join(tag_list)}",
        output_dir / filepath.scatter_plot_score_tag_count,
        x_data,
        y_data,
        "Tag Count",
    )


def save_scatter_plot_custom_tag_count(
    tag_list: list[str], output_dir: pathlib.Path, post_list: list[util.PostData]
) -> None:
    """Generate scatter plot mapping post score against post total tag count."""
    # Make one scatter plot per custom category
    for custom_category, custom_tag_list in custom.categories.items():
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

        chart.scatter_post_score(
            f"Post Score by Custom Category Weight:\n{" ".join(tag_list)}",
            output_dir / f"Scatter {custom_category}.png",
            x_data,
            y_data,
            "Category Weight",
        )


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
    for category in options.recommended_tags:
        unique_tags[category] = set()
    for post in post_data:
        # # Only calculate data for tags that are of a certain category
        for category in options.recommended_tags:
            unique_tags[category].update(post.tags[category])

    # Connect to the database of tags to post ids.
    con = sqlite3.connect(filepath.cache_postid_database)
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
        output_dir / filepath.similar_tags, mode="wt", encoding="utf-8"
    ) as out_file:
        for category, tag_dict in ranked_tags.items():
            out_file.write(f"### {category}\n")
            out_file.write("#set|#db    %set| tag\n")
            num_skipped_tags = 0
            for tag, val in sorted(
                tag_dict.items(), key=lambda kv: (kv[1][0]), reverse=True
            ):
                set_percentage = (val[1] / posts_len) * 100
                # Only write tags at or above the threshold
                if set_percentage >= options.recommended_tag_threshold:
                    out_file.write(
                        f"{str(val[1]).rjust(4)}|{str(val[2]).ljust(7)}"
                        f" {str(int(set_percentage)).rjust(3)}| {tag}\n"
                    )
                else:
                    num_skipped_tags += 1
            if num_skipped_tags > 0:
                out_file.write(
                    f"  (... plus {num_skipped_tags} other tags found in less than"
                    f" {options.recommended_tag_threshold}%"
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
    for category in options.recommended_tags:
        ranked_tags[category] = []

    # Connect to the database of tags to post ids.
    con = sqlite3.connect(filepath.cache_postid_database)
    cur = con.cursor()
    # Compare all other tags.
    cur.execute("SELECT * FROM ids")
    row = cur.fetchone()
    while row is not None:
        tag = row[0]
        # Only calculate data for tags that are of a certain output type.
        category = tag_to_category.get_category(tag)
        if category in options.recommended_tags:
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
        output_dir / filepath.similar_tags, mode="wt", encoding="utf-8"
    ) as out_file:
        for category, tag_list in ranked_tags.items():
            out_file.write(f"### {category}\n")
            out_file.write("#set|#db    %set| tag\n")
            num_skipped_tags = 0
            for item in sorted(tag_list, key=lambda val: (val[0]), reverse=True):
                set_percentage = int((item[2] / posts_len) * 100)
                # Only write tags at or above the threshold
                if set_percentage >= options.recommended_tag_threshold:
                    out_file.write(
                        f"{str(item[2]).rjust(4)}|{str(item[3]).ljust(7)}"
                        f" {str(set_percentage).rjust(3)}| {item[1]}\n"
                    )
                else:
                    num_skipped_tags += 1
            if num_skipped_tags > 0:
                out_file.write(
                    f"  (... plus {num_skipped_tags} other tags found in less than"
                    f" {options.recommended_tag_threshold}%"
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
