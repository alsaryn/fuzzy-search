"""Generate and use a cache for speedier processing.

Contains functions for reading /exports/ and outputting cached files in /cache/.
"""

import csv
import os
import json
import re
import pickle
import sqlite3
import gzip
import sys
from collections import defaultdict

import util
import progressbar


def print_cache_warning_message() -> None:
    """Print an informative message about the ETA of caching missing files."""
    # Only print the message once per execution
    if not util.Options.has_printed_cache_warning_message:
        util.Options.has_printed_cache_warning_message = True
        print("\n\n[---Generating missing cache files---]")
        print("NOTE: This one-time process may take 10+ minutes.")
        print("  Stage 1: Pre-processing")
        print("  Stage 2: Post Database (Tags, core info)")
        print("    Takes up about 80% of the entire caching process.")
        print("  Stage 3: Tag-to-Posts Map")
        print("    Uses a little under 1 GB of RAM per 1 million posts.")
        print("  Stage 4: Cleanup")
        print("  Stage 5: Post Database (Additional info)")
        print(" Your request will be processed after the cache is generated.\n\n")


def check_custom_categories() -> None:
    """Ensure custom category files exist."""
    # Search for at least one of the form "tags-YYYY-MM-DD.csv.gz".
    filenames = os.listdir(util.Filepath.settings_category_dir)
    # If no custom categories were found, generate some sample categories
    if len(filenames) == 0:
        with open(
            util.Filepath.settings_category_dir / "Detailed Background.txt",
            "wt",
            encoding="utf-8",
        ) as out_file:
            tag_list = [
                "detailed_background",
                "day",
                "sky",
                "outside",
                "forest",
                "grass",
                "tree",
                "cloud",
                "night",
                "plant",
                "water",
                "flower",
                "book",
                "moon",
                "window",
            ]
            out_file.write(f"tab:green\n{"\n".join(tag_list)}\n")
        with open(
            util.Filepath.settings_category_dir / "Furry.txt", "wt", encoding="utf-8"
        ) as out_file:
            tag_list = [
                "furgonomics",
                "wings",
                "claws",
                "two_tone_body",
                "fin",
                "scales",
                "tuft",
                "multicolored_body",
                "fur",
                "feathers",
                "digitigrade",
                "countershading",
                "mane",
            ]
            out_file.write(f"tab:blue\n{"\n".join(tag_list)}\n")
        with open(
            util.Filepath.settings_category_dir / "Blacklist.txt",
            "wt",
            encoding="utf-8",
        ) as out_file:
            tag_list = [
                "uwu",
            ]
            out_file.write(f"tab:gray\n{"\n".join(tag_list)}\n")


def check_bar_charts() -> None:
    """Ensure custom category files exist."""
    # Search for at least one of the form "tags-YYYY-MM-DD.csv.gz".
    filenames = os.listdir(util.Filepath.settings_bar_dir)
    # If no bar charts were found, generate some sample bar charts
    if len(filenames) == 0:
        with open(
            util.Filepath.settings_bar_dir / "Species.txt", "wt", encoding="utf-8"
        ) as out_file:
            tag_list = [
                "canine",
                "feline",
                "bovine",
                "avian",
                "shark",
                "insect",
                "mythological_creature",
            ]
            out_file.write("\n".join(tag_list))
        with open(
            util.Filepath.settings_bar_dir / "TWYS Gender.txt", "wt", encoding="utf-8"
        ) as out_file:
            tag_list = [
                "female",
                "gynomorph",
                "ambiguous_gender",
                "andromorph",
                "male",
            ]
            out_file.write("\n".join(tag_list))
        with open(
            util.Filepath.settings_bar_dir / "Format.txt", "wt", encoding="utf-8"
        ) as out_file:
            tag_list = [
                "traditional_media_(artwork)",
                "digital_media_(artwork)",
                "3d_(artwork)",
                "comic",
                "animated",
                "sound",
            ]
            out_file.write("\n".join(tag_list))
        with open(
            util.Filepath.settings_bar_dir / "Group Composition.txt",
            "wt",
            encoding="utf-8",
        ) as out_file:
            tag_list = [
                "solo",
                "solo male",
                "solo female",
                "duo",
                "duo -male",
                "duo -female",
                "trio",
                "group",
                "zero_pictured",
            ]
            out_file.write("\n".join(tag_list))


def check_e6_blacklist() -> None:
    """Ensure E6-style blacklist file exists."""
    if not util.Filepath.blacklisted_tags.exists():
        util.Filepath.blacklisted_tags.touch()


def generate_missing_cache() -> None:
    """Check for and generate missing cache files."""
    # Retrieve values from the cache info file, or generate a new one if missing.
    if util.Filepath.cache_info.exists():
        with open(util.Filepath.cache_info, "rt", encoding="utf-8") as in_file:
            cache_info = json.loads(in_file.read())
    else:
        # If the info file is missing, generate a default one
        print_cache_warning_message()
        cache_info = {
            "cached_tag_counts": False,
            "cached_tag_categories": False,
            "cached_post_database": False,
            "cached_post_additional_info": False,
            "cached_postid_database": False,
            "fuzzy_search_version": 1,
            "change_list": 1,
            "num_tags": 0,
            "num_valid_posts": 0,
            "num_deleted_posts": 0,
        }
        update_cache_info(cache_info)

    # Detect if any cache files are missing and regenerate them as necessary.
    # Stages 1-2: Initialize post database, tag count map, and tag category map
    if (
        cache_info["cached_tag_counts"]
        and cache_info["cached_tag_categories"]
        and cache_info["cached_post_database"]
        and util.Filepath.cache_tag_to_category.exists()
        and util.Filepath.cache_tag_counts.exists()
        and util.Filepath.cache_post_data_database.exists()
    ):
        # Found all cache files for stages 1-2, move on
        pass
    # Else, cache files for stages 1-2 were missing and need to be regenerated
    else:
        print_cache_warning_message()
        # Delete any leftover files (they may contain incomplete data)
        if util.Filepath.cache_tag_to_category.exists():
            os.remove(util.Filepath.cache_tag_to_category)
        if util.Filepath.cache_tag_counts.exists():
            os.remove(util.Filepath.cache_tag_counts)
        if util.Filepath.cache_post_data_database.exists():
            os.remove(util.Filepath.cache_post_data_database)

        # Stage 1:
        # Temporary tag to category map (util.TagToCategory; not saved to disk)
        cache_categories_initial()

        # Stage 2:
        # For speed, we generate the following data structures in a single pass:
        #  Post database
        #  Tag-to-Post_Count map
        #  Tag-to-Category map
        # Therefore, if one of these cache files is missing,
        # then we must regenerate the others as well.
        cache_posts(cache_info)
        cache_info["cached_tag_counts"] = True
        cache_info["cached_tag_categories"] = True
        cache_info["cached_post_database"] = True
        update_cache_info(cache_info)

    # Load maps into memory
    util.init_tag_to_category()
    util.init_tag_to_post_count()

    # Stages 3-4: Create inverted-index map of tag to posts (ids) with that tag
    if (
        cache_info["cached_postid_database"]
        and util.Filepath.cache_postid_database.exists()
    ):
        # Found all cache files for stages 3-4, move on
        pass
    # Else, cache files for stages 3-4 were missing and need to be regenerated
    else:
        print_cache_warning_message()
        # Delete any leftover files (they may contain incomplete data)
        if util.Filepath.cache_postid_database.exists():
            os.remove(util.Filepath.cache_postid_database)

        # Stages 3-4: Create the post id cache
        cache_tag_to_postid()
        cache_info["cached_postid_database"] = True
        update_cache_info(cache_info)

    # Stage 5: Additional post info
    if (
        cache_info["cached_post_additional_info"]
        and util.Filepath.cache_post_data_sources.exists()
        and util.Filepath.cache_post_data_descriptions.exists()
        and util.Filepath.cache_post_data_durations.exists()
    ):
        pass
    else:
        if util.Filepath.cache_post_data_sources.exists():
            os.remove(util.Filepath.cache_post_data_sources)
        if util.Filepath.cache_post_data_descriptions.exists():
            os.remove(util.Filepath.cache_post_data_descriptions)
        if util.Filepath.cache_post_data_durations.exists():
            os.remove(util.Filepath.cache_post_data_durations)
        cache_posts_sources_descriptions_durations()
        cache_info["cached_post_additional_info"] = True
        update_cache_info(cache_info)

    # Ensure wiki page files exist files (also doubles as human-readable tag counts)
    generate_wiki_pages()

    # Load blacklist
    check_e6_blacklist()
    util.init_blacklist()

    # Generate sample custom category files (if none were found)
    check_custom_categories()
    util.init_custom_categories()
    check_bar_charts()
    util.init_bar_charts()


def cache_categories_initial() -> None:
    """Process tags export file into a tag to category json dict."""
    # Note: this is a temporary map, as later we will prune tags with a post count of 0.

    # Search for an export of the form "tags-YYYY-MM-DD.csv.gz".
    tags_export_file = None
    for file in os.listdir(util.Filepath.export_dir):
        if re.match(r"^tags-\d\d\d\d-\d\d-\d\d\.csv\.gz$", file):
            tags_export_file = util.Filepath.export_dir / file
            break
    # Exit if the file was not found
    if not tags_export_file:
        raise (
            util.ExportFileNotFound(
                message=f"File Not Found:"
                f" {util.Filepath.export_dir}/tags-YYYY-MM-DD.csv.gz"
            )
        )

    # Progress bar:
    # TODO: Ideally, we scan the id of the last line of the file and use that.
    # This stage should only take a few seconds, so we use an estimated value.
    progressbar.start_new_stage("Cache Stage 1/5", 3 * util.Options.num_tags)

    # Create a mapping of every tag to it's E6 category
    # Read in the Tags file.
    with gzip.open(tags_export_file, mode="rt", encoding="utf-8") as in_file:
        # Create a csv.reader object
        csv_reader = csv.reader(in_file, delimiter=",", quotechar='"')

        # Skip the header row:
        # id,name,category,post_count
        next(csv_reader, None)

        # Iterate over each row in the CSV file.
        # Map tag to its category (E6 stores this as an int, we use the full string).
        # Category:
        # 	0: general
        # 	1: artist
        # 	2: contributor
        # 	3: copyright
        # 	4: character
        # 	5: species
        # 	6: invalid
        # 	7: meta
        # 	8: lore
        for row in csv_reader:
            progressbar.update_step(row[0])
            match int(row[2]):
                case 0:
                    util.TagToCategory.tags[row[1]] = "general"
                case 1:
                    util.TagToCategory.tags[row[1]] = "artist"
                case 2:
                    util.TagToCategory.tags[row[1]] = "contributor"
                case 3:
                    util.TagToCategory.tags[row[1]] = "copyright"
                case 4:
                    util.TagToCategory.tags[row[1]] = "character"
                case 5:
                    util.TagToCategory.tags[row[1]] = "species"
                case 6:
                    util.TagToCategory.tags[row[1]] = "invalid"
                case 7:
                    util.TagToCategory.tags[row[1]] = "meta"
                case 8:
                    util.TagToCategory.tags[row[1]] = "lore"
                case _:
                    raise (
                        util.TagCategoryNotFound(
                            message=f"Tag Category Not Found {row[1]}"
                        )
                    )


def cache_posts(cache_info: dict) -> None:
    """Parse posts export file into relevant data structures."""
    # For speed, we generate the following data structures in a single pass:
    #  Post database
    #  Tag-to-Post_Count map
    #  Tag-to-Category map
    # Therefore, if one of these cache files is missing,
    # then we must regenerate the others as well.

    # Search for an export of the form "posts-YYYY-MM-DD.csv.gz".
    posts_export_file = None
    for file in os.listdir(util.Filepath.export_dir):
        if re.match(r"^posts-\d\d\d\d-\d\d-\d\d\.csv\.gz$", file):
            posts_export_file = util.Filepath.export_dir / file
            break
    # Exit if the file was not found
    if not posts_export_file:
        raise (
            util.ExportFileNotFound(
                message=f"File Not Found:"
                f" {util.Filepath.export_dir}/posts-YYYY-MM-DD.csv.gz"
            )
        )

    progressbar.start_new_stage("Cache Stage 2/5", util.Options.num_posts)

    # Increase the maximum csv field size
    # to handle some rather /girthy/ post descriptions.
    # In awe of the size of this lad :3
    csv.field_size_limit(262144)

    # Connect to the database.
    # If the database file doesn't exist, it will be created here.
    con = sqlite3.connect(util.Filepath.cache_post_data_database)
    cur = con.cursor()

    # Initialize the post_data table.
    cur.execute(
        "CREATE TABLE posts(postid INTEGER PRIMARY KEY, score INTEGER, favs INTEGER,"
        " comments INTEGER, rating TEXT, created_at TEXT, md5_hash TEXT,"
        " file_size INTEGER, file_ext TEXT, tags BLOB)"
    )

    # Mapping of every tag to the count of (valid) posts with that tag
    tag_tally = defaultdict(int)

    # Read in the Posts file and fill out relevant data structures
    with gzip.open(posts_export_file, "rt", encoding="utf-8") as in_file:
        csv_reader = csv.reader(in_file, delimiter=",", quotechar='"')
        # Skip the header row
        next(csv_reader, None)

        # Each row is a list of strings.
        # Numerical values need to be converted.
        # booleans are stored as "t" or "f".

        # index - value
        # 0 id
        # 1 uploader_id
        # 2 created_at
        # 3 md5
        # 4 source (these are external links, not the static E6 url for the post image)
        # 5 rating
        # 6 image_width
        # 7 image_height
        # 8 tag_string
        # 9 locked_tags
        # 10 fav_count
        # 11 file_ext
        # 12 parent_id
        # 13 change_seq
        # 14 approver_id
        # 15 file_size
        # 16 comment_count
        # 17 description
        # 18 duration
        # 19 updated_at
        # 20 is_deleted
        # 21 is_pending
        # 22 is_flagged
        # 23 score
        # 24 up_score
        # 25 down_score
        # 26 is_rating_locked
        # 27 is_status_locked
        # 28 is_note_locked

        # Statistics
        num_deleted_posts = 0
        num_valid_posts = 0

        # Iterate over each row in the CSV file
        for row in csv_reader:
            progressbar.update_step(row[0])

            # Omit posts that are deleted.
            if row[20] == "t":
                num_deleted_posts += 1
                continue
            # Else, the post is valid
            num_valid_posts += 1

            # [--- Assemble data in the output format ---]
            # created_at: str. Just the date (year-month-day), no time.
            # Hyphens for partitioning.
            created_at = f"{row[2][0:4]}-{row[2][5:7]}-{row[2][8:10]}"

            # Tags: We split up tags by category, ordered as they appear on E6
            tags = {
                "artist": [],
                "contributor": [],
                "copyright": [],
                "character": [],
                "species": [],
                "general": [],
                "invalid": [],
                "lore": [],
                "meta": [],
            }
            for tag in row[8].split(" "):
                if not util.get_category(tag):
                    print(f"[ERROR] {tag} was not found in any E6 category.")
                    print("  This is likely a result of a corrupted posts.csv.gz file.")
                    print(
                        "  Try deleting the cache and"
                        " redownloading the posts export file."
                    )
                    print("Exiting...\n")
                    sys.exit(1)

                tags[util.get_category(tag)].append(tag)

                # Increment the post_count for the given tag
                tag_tally[tag] += 1

            # Write the row to the post database
            data = (
                int(row[0]),
                int(row[23]),
                int(row[10]),
                row[16],
                row[5].upper(),
                created_at,
                row[3],
                int(row[15]),
                row[11],
                pickle.dumps(tags),
            )
            cur.execute("INSERT INTO posts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

    # Commit changes to database.
    con.commit()
    con.close()

    # Save the map of tags to post counts to disk as a json dict.
    with open(util.Filepath.cache_tag_counts, "wt", encoding="utf-8") as out_file:
        # We sort the map from the most common to the least common tags.
        # In addition to being prettier to print out,
        # this leads to more "cache hits" (performance boost),
        # especially with the dense recommendation algorithm.
        tag_tally = dict(
            sorted(tag_tally.items(), key=lambda kv: (kv[1]), reverse=True)
        )
        out_file.write(json.dumps(tag_tally, separators=(",", ":")))

    # Save the map of tags to E6 category to disk as a json dict.
    tag_to_category = {}
    for tag in tag_tally.keys():
        tag_to_category[tag] = util.get_category(tag)
    with open(util.Filepath.cache_tag_to_category, "wt", encoding="utf-8") as out_file:
        # Sort by category.
        tag_to_category = dict(
            sorted(tag_to_category.items(), key=lambda kv: (kv[1]), reverse=False)
        )
        out_file.write(json.dumps(tag_to_category, separators=(",", ":")))

    # Update statistics
    cache_info["num_tags"] = len(tag_tally.keys())
    cache_info["num_valid_posts"] = num_valid_posts
    cache_info["num_deleted_posts"] = num_deleted_posts


def cache_posts_sources_descriptions_durations() -> None:
    """Parse posts export file into a additional post info tables."""
    # Search for an export of the form "posts-YYYY-MM-DD.csv.gz".
    posts_export_file = None
    for file in os.listdir(util.Filepath.export_dir):
        if re.match(r"^posts-\d\d\d\d-\d\d-\d\d\.csv\.gz$", file):
            posts_export_file = util.Filepath.export_dir / file
            break
    # Exit if the file was not found
    if not posts_export_file:
        raise (
            util.ExportFileNotFound(
                message=f"File Not Found:"
                f" {util.Filepath.export_dir}/posts-YYYY-MM-DD.csv.gz"
            )
        )

    progressbar.start_new_stage("Cache Stage 5/5", util.Options.num_posts)

    # Increase the maximum csv field size
    # to handle some rather girthy post descriptions.
    # In awe of the size of this lad :3
    csv.field_size_limit(262144)

    # Connect to the database.
    # If the database file doesn't exist, it will be created here.
    con_sources = sqlite3.connect(util.Filepath.cache_post_data_sources)
    cur_sources = con_sources.cursor()
    con_descs = sqlite3.connect(util.Filepath.cache_post_data_descriptions)
    cur_descs = con_descs.cursor()
    con_durations = sqlite3.connect(util.Filepath.cache_post_data_durations)
    cur_durations = con_durations.cursor()

    # Initialize the post data tables
    cur_sources.execute("CREATE TABLE posts(postid INTEGER PRIMARY KEY, source TEXT)")
    cur_descs.execute(
        "CREATE TABLE posts(postid INTEGER PRIMARY KEY, description TEXT)"
    )
    cur_durations.execute(
        "CREATE TABLE posts(postid INTEGER PRIMARY KEY, duration TEXT)"
    )

    # Read in the Posts file and fill out relevant data structures
    with gzip.open(posts_export_file, "rt", encoding="utf-8") as in_file:
        csv_reader = csv.reader(in_file, delimiter=",", quotechar='"')
        # Skip the header row
        next(csv_reader, None)
        # Iterate over each row in the CSV file
        for row in csv_reader:
            progressbar.update_step(row[0])
            # Omit posts that are deleted.
            if row[20] == "t":
                continue

            # Write the row to the post database
            # Row 0: post id
            # Row 4: source
            # Row 17: description
            # Row 18: duration
            #  If post is not a video: is the empty string
            #  If post is a video: is a float, representing seconds (ex: 15.0)
            cur_sources.execute("INSERT INTO posts VALUES(?, ?)", (int(row[0]), row[4]))
            cur_descs.execute("INSERT INTO posts VALUES(?, ?)", (int(row[0]), row[17]))
            if row[18] != "":
                cur_durations.execute(
                    "INSERT INTO posts VALUES(?, ?)", (int(row[0]), float(row[18]))
                )

    # Commit Changes
    con_sources.commit()
    con_sources.close()
    con_descs.commit()
    con_descs.close()
    con_durations.commit()
    con_durations.close()


def cache_tag_to_postid() -> None:
    """Create a database mapping tags to posts with that tag."""
    # This version should only take a few minutes to run,
    # but will use a couple gigabytes of memory.

    tag_to_ids = defaultdict(list)

    # Open the database with all the posts.
    con = sqlite3.connect(util.Filepath.cache_post_data_database)
    cur = con.cursor()
    cur.execute("SELECT postid, tags FROM posts")
    progressbar.start_new_stage("Cache Stage 3/5", util.Options.num_posts)
    count = 1
    # Iterate over each row in post database
    row = cur.fetchone()
    while row is not None:
        post_id = row[0]
        tags = pickle.loads(row[1])

        # Append the post id to the "all" tag
        tag_to_ids[util.Options.all_posts].append(post_id)

        # Scan through all tags this post has.
        for tag_list in tags.values():
            for row_tag in tag_list:
                # Add the postid to the associated tag in the map.
                tag_to_ids[row_tag].append(post_id)

        # Prepare to process the next row of data.
        row = cur.fetchone()
        progressbar.update_step(count)
        count += 1
    con.close()

    # Save the post id data to disk
    progressbar.start_new_stage("Cache Stage 4/5", len(tag_to_ids.keys()))
    # Connect to the database.
    con = sqlite3.connect(util.Filepath.cache_postid_database)
    cur = con.cursor()

    # Initialize the table.
    # posts BLOB: the post_ids as a python list of ints
    cur.execute("CREATE TABLE ids(tag TEXT PRIMARY KEY, posts BLOB)")

    for i, item in enumerate(tag_to_ids.items()):
        progressbar.update_step(i)
        cur.execute("INSERT INTO ids VALUES(?, ?)", (item[0], pickle.dumps(item[1])))

    # Commit changes to database.
    con.commit()
    con.close()


def generate_wiki_pages(include_tags_without_wiki_pages: bool = True) -> None:
    """Parse wiki export file into human-readable tag counts and wiki pages."""
    # Only generate the wiki pages if they don't already exist
    if not (util.Filepath.wiki_dir / "Wiki.txt").exists():
        # Store the tag, post_count, and wiki page body (if it exists) as a tuple.
        tag_tuples = []
        wiki_headers = {
            "general": {},
            "artist": {},
            "contributor": {},
            "copyright": {},
            "character": {},
            "species": {},
            "invalid": {},
            "meta": {},
            "lore": {},
            "other": {},
        }

        # Search for an export of the form "wiki_pages-YYYY-MM-DD.csv.gz".
        export_file = None
        for file in os.listdir(util.Filepath.export_dir):
            if re.match(r"^wiki_pages-\d\d\d\d-\d\d-\d\d\.csv\.gz$", file):
                export_file = util.Filepath.export_dir / file
                break
        # If the wiki export file was not found, skip generating the wiki
        if not export_file:
            print("Skipping generating wiki pages. Reason:")
            print(
                f"  File Not Found: "
                f"{util.Filepath.export_dir}/wiki_pages-YYYY-MM-DD.csv.gz"
            )
            return

        progressbar.start_new_stage(
            "Generate Wiki Pages", len(util.TagToPostCount.tags.keys())
        )
        # Read in the export file
        with gzip.open(export_file, "rt", encoding="utf-8") as in_file:
            csv_reader = csv.reader(in_file, delimiter=",", quotechar='"')
            # Header row
            next(csv_reader, None)

            # Iterate over each row in the CSV file
            current_row = 0
            for row in csv_reader:
                progressbar.update_step(current_row)
                current_row += 1

                # 0 id
                # 3 title
                # 4 body

                # Treat empty wiki pages as nonexistent
                body = row[4]
                if len(body) == 0:
                    continue

                tag = row[3]
                # Prints the total times this tag appears in the collection.
                # Note that some tags don't exactly match their wiki titles,
                # and may display a count of 0 of here.
                count = util.get_post_count(tag)

                # Add the tag body to the structure for printing it.
                tag_tuples.append((tag, count, body))

                # Add the tag to the appropriate header category.
                category = util.get_category(tag, print_missing_tag=False)
                if category:
                    wiki_headers[category][tag] = (tag, count, len(body))
                # If the category was not found, then place it in the N/A category.
                else:
                    wiki_headers["other"][tag] = (tag, count, len(body))

        # Save the wiki page bodies to disk.
        with open(util.Filepath.output_wiki_pages, "wt", encoding="utf-8") as out_file:
            out_file.write("\n")
            tag_tuples = sorted(tag_tuples, key=lambda v: (v[1]), reverse=True)
            for tag, count, body in tag_tuples:
                # Justify text so the columns are even:
                # The highest post count is 7 digits,
                # while the largest wiki page character count is 5 digits.
                out_file.write(
                    f"### {str(count).ljust(7)} {str(len(body)).rjust(5)}"
                    f" {tag}\n {body}\n\n\n"
                )
            out_file.write("\n")

        if include_tags_without_wiki_pages:
            # We've already added all tags with wiki pages to the headers,
            # so now add tags without wiki pages.
            for tag, category in util.TagToCategory.tags.items():
                # If we haven't already found the tag,
                # add the tag, it's count, and a sign it has no wiki page.
                if tag not in wiki_headers[category].keys():
                    count = util.get_post_count(tag)
                    wiki_headers[category][tag] = (tag, count, 0)

        # Save the headers to disk.
        for category, header_tuple_list in wiki_headers.items():
            # Sort the headers, so the tags with most posts are at the top of the file.
            # When multiple tags have the same count, sort them alphabetically.
            header_tuple_list = sorted(
                header_tuple_list.values(), key=lambda v: (v[0]), reverse=False
            )
            # Sort the headers, so the tags with most posts are at the top of the file.
            header_tuple_list = sorted(
                header_tuple_list, key=lambda v: (v[1]), reverse=True
            )
            # Save each category as a separate file.
            with open(
                util.Filepath.wiki_dir / f"Wiki {category}.txt", "wt", encoding="utf-8"
            ) as out_file:
                out_file.write(f"### {category}\npost_count wiki_page_length tag\n")
                # Justify text so the columns are even:
                # The highest post count is 7 digits,
                # while the largest wiki page character count is 5 digits.
                for tag, count, wiki_page in header_tuple_list:
                    # Omit the page length if it is zero
                    if wiki_page == 0:
                        out_file.write(f"{str(count).ljust(7)}       {tag}\n")
                    else:
                        out_file.write(
                            f"{str(count).ljust(7)} {str(wiki_page).rjust(5)} {tag}\n"
                        )
                out_file.write("\n")


def update_cache_info(cache_info: dict):
    """Store current state of caching process."""
    # It's possible for a database to be created but missing data
    # (such as interrupting the caching process).
    # This file is necessary to detect if a cache file exists but has incomplete data.
    with open(util.Filepath.cache_info, "wt", encoding="utf-8") as out_file:
        # Use larger indent for pretty-printing
        out_file.write(json.dumps(cache_info, indent=4))
