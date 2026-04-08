"""Main driver for Fuzzy Search. By Keerek."""

import traceback
import argparse
import sys
import pathlib
import os
import threading

import util
import cache
import tag
import progressbar

if __name__ == "__main__":
    # Start a progress bar on a separate thread from the main program

    # Initialize the parser
    parser = argparse.ArgumentParser(description="Analyze tag-based data.")

    # General Arguments
    parser.add_argument(
        "--data_dir", type=str, default=0, help="Set data/ directory (default: CWD)."
    )

    # Toggle Analysis Output
    parser.add_argument(
        "--all",
        action="store_true",
        help="Enable all analysis outputs.",
    )
    parser.add_argument(
        "--recommended",
        action="store_true",
        help="Enable recommended/similar tags output.",
    )
    parser.add_argument(
        "--posts",
        action="store_true",
        help="Enable text dump of posts.",
    )
    parser.add_argument(
        "--counts",
        action="store_true",
        help="Enable tag counts (E6 category).",
    )
    parser.add_argument(
        "--counts_custom",
        action="store_true",
        help="Enable tag counts (custom category). Also enables --counts.",
    )
    parser.add_argument(
        "--charts_custom",
        action="store_true",
        help="Enable custom score scatter plot output.",
    )
    parser.add_argument(
        "--bar",
        action="store_true",
        help="Enable custom bar chart output.",
    )
    parser.add_argument(
        "--score",
        action="store_true",
        help="Enable E6 score scatter plot output.",
    )
    parser.add_argument(
        "--url",
        action="store_true",
        help="Enable URL output.",
    )
    parser.add_argument(
        "--source",
        action="store_true",
        help="Enable source output.",
    )
    parser.add_argument(
        "--description",
        action="store_true",
        help="Enable description output.",
    )
    parser.add_argument(
        "--duration",
        action="store_true",
        help="Enable duration output.",
    )
    parser.add_argument(
        "--graph",
        type=int,
        default=0,
        help="Enable Obsidian Vaults for searches with fewer than (num) posts.",
    )

    # URL
    parser.add_argument(
        "--url_only",
        action="store_true",
        help="Only output URL information (default: disabled).",
    )
    parser.add_argument(
        "--url_mode",
        type=str,
        default="full",
        help="Format of URLs (mode = md5, url, or full).",
    )

    # Filters
    parser.add_argument(
        "--max_posts",
        type=int,
        default=200000,
        help="Skip searches with more posts than this (default: 200,000).",
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default=None,
        help="Excludes all posts before this date.",
    )
    parser.add_argument(
        "--end_date", type=str, default=None, help="Excludes all posts after this date."
    )
    parser.add_argument(
        "--score_min",
        type=int,
        default=-999999,
        help="Excludes all posts with less than this score.",
    )
    parser.add_argument(
        "--score_max",
        type=int,
        default=999999,
        help="Excludes all posts with more than this score.",
    )
    parser.add_argument(
        "--rating",
        type=str,
        default="SQE",
        help="Only search through posts with the specified rating (default: SQE).",
    )
    parser.add_argument(
        "--cursed",
        action="store_true",
        help="Uwu-ifies text.",
    )
    parser.add_argument(
        "--curseder",
        action="store_true",
        help="You have been warned.",
    )
    parser.add_argument(
        "--cursedest",
        action="store_true",
        help="There is no helping you, not anymore.",
    )
    parser.add_argument(
        "--blacklist",
        type=float,
        default=0.0,
        help="Filter out posts with a custom category Blacklist score higher than num.",
    )
    parser.add_argument(
        "--order",
        type=str,
        default="",
        help="Order posts by custom category score (default: creation date).",
    )
    parser.add_argument(
        "--ascending",
        action="store_true",
        help="Order posts in ascending order.",
    )
    parser.add_argument(
        "--top",
        type=float,
        default=100.0,
        help="Keep only the first (top) percent posts.",
    )
    parser.add_argument(
        "--rec_tag_threshold",
        type=int,
        default=2,
        help="Similar Tags: omit the bottom % of tags (values: 0-100) (default: 2%).",
    )

    # argparse will print a message and exit with invalid input or with --help
    args = parser.parse_args()

    # Determine /data/ directory.
    # Prefer "data_dir" argument. Defaults to CWD
    if args.data_dir:
        try:
            root_dir = pathlib.Path(args.data_dir)
        except Exception as e:
            print("Error: Unable to parse data directory filepath.")
            sys.exit(0)
        if not root_dir.exists():
            print(f"Error: Unable to find data directory {args.data_dir}")
            sys.exit(0)
    else:
        root_dir = pathlib.Path(os.getcwd())
    # Find (and set up, if needed) the data directory.
    util.set_root(root_dir)
    util.ensure_dirs_exist()

    # Handle valid posts
    util.Options.rating = str(args.rating).upper()
    util.Options.score_min = args.score_min
    util.Options.score_max = args.score_max

    # Toggle Output
    if args.all:
        util.Options.recommended = True
        util.Options.posts = True
        util.Options.counts = True
        util.Options.counts_custom = True
        util.Options.charts_custom = True
        util.Options.bar_charts = True
        util.Options.score = True
        util.Options.url = True
        util.Options.source = True
        util.Options.description = True
        util.Options.duration = True
    else:
        util.Options.recommended = args.recommended
        util.Options.posts = args.posts
        util.Options.counts = args.counts
        util.Options.counts_custom = args.counts_custom
        util.Options.charts_custom = args.charts_custom
        util.Options.bar_charts = args.bar
        util.Options.score = args.score
        util.Options.url = args.url
        util.Options.source = args.source
        util.Options.description = args.description
        util.Options.duration = args.duration
    # Some options override 'all'
    util.Options.graph = args.graph

    util.Options.max_query_size = args.max_posts
    util.Options.percent_posts_to_keep = args.top

    # Only check for URL options if url output is enabled
    # if not util.Options.url:
    util.Options.url_only = args.url_only
    if args.url_mode:
        if args.url_mode in ["md5", "url", "full"]:
            util.Options.url_mode = args.url_mode
        # Error out if mode is not a valid string
        else:
            print("Error: Unrecognized url_mode argument. Valid modes:")
            print("  md5")
            print("  url")
            print("  full")
            sys.exit(0)

    util.Options.start_date = args.start_date
    util.Options.end_date = args.end_date

    util.Options.blacklist_score_threshold = args.blacklist
    util.Options.order = args.order
    util.Options.descending = not args.ascending

    util.Options.recommended_tag_threshold = args.rec_tag_threshold

    # Apply the highest level curse specified
    if args.cursedest:
        util.set_curse_level(3)
    elif args.curseder:
        util.set_curse_level(2)
    elif args.cursed:
        util.set_curse_level(1)
    else:
        util.set_curse_level(0)

    # Start a thread to print progress reports wile program is running
    t = threading.Thread(target=progressbar.start_progress_bar)
    t.start()

    # Perform tag analysis
    try:
        # Ensure cache exists
        cache.generate_missing_cache()
        # Process queries in input/
        tag.read_in_query_list()

    except util.ExportFileNotFound as e:
        print(f"\n{e.message}")
        print(
            " Did you place the following zipped export files into "
            f"{util.Filepath.export_dir}?"
        )
        print("    posts-YYYY-MM-DD.csv.gz")
        print("    tags-YYYY-MM-DD.csv.gz")
        print("    wiki_pages-YYYY-MM-DD.csv.gz")
    except util.CacheFileNotFound as e:
        print(f"\n{e.message}")
        print(" Please re-run the program to generate the missing cache file")
    except util.FileNotFound as e:
        print(f"\n{e.message}")
        print(" This is most likely a result of missing user-made files.")
        print(" Re-run the program and some sample files will be generated.")
    except util.InvalidCustomCategory as e:
        print(f"\n{e.message}")
        print(" Ensure the category exists in the following files:")
        print(f"   {util.Filepath.custom_categories}")
        print(f"   {util.Filepath.custom_categories_colors}")
        print(
            " You can also delete the custom_settings folder,"
            " run the program again, then study the sample files."
        )
    except Exception as e:
        print("\n[ERROR - EXITING EXECUTION]")
        print(traceback.format_exc())

    # End the progress bar thread, as we've finished execution.
    progressbar.end_progress_bar()
    t.join()
