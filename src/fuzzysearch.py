"""Main driver for Fuzzy Search."""

import traceback
import argparse
import sys
import pathlib
import os
import threading

import util
import cache
import search
import postdownloader
from progressbar import progressbar
from utilfilepath import filepath
from utiltext import translate
from utiloptions import options

if __name__ == "__main__":
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Analyze tag-based data.")

    # General Arguments
    parser.add_argument(
        "--data_dir", type=str, default=0, help="Set data/ directory (default: CWD)."
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download posts in --data_dir. Overrides analysis options.",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help="Override old analysis results with new results.",
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
        help="Hide posts with a Blacklist relevancy greater or equal num.",
    )
    parser.add_argument(
        "--order",
        type=str,
        default="",
        help="Order posts by custom category relevancy (default: creation date).",
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
        help="Keep only the first (top) percent of sorted posts.",
    )
    parser.add_argument(
        "--rec_tag_threshold",
        type=float,
        default=2.0,
        help="--recommended: omit the bottom % of tags (default: 2.0%).",
    )

    # argparse will print a message and exit with invalid input or with --help
    args = parser.parse_args()

    # [--- Data Directory ---]
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
    filepath.set_root(root_dir)

    # [--- Output Toggles ---]
    if args.all:
        options.recommended = True
        options.posts = True
        options.counts = True
        options.counts_custom = True
        options.charts_custom = True
        options.bar_charts = True
        options.score = True
        options.url = True
        options.source = True
        options.description = True
        options.duration = True
    else:
        options.recommended = args.recommended
        options.posts = args.posts
        options.counts = args.counts
        options.counts_custom = args.counts_custom
        options.charts_custom = args.charts_custom
        options.bar_charts = args.bar
        options.score = args.score
        options.url = args.url
        options.source = args.source
        options.description = args.description
        options.duration = args.duration

    # [--- Filter/Misc Options ---]
    options.override = args.override
    options.graph = args.graph
    options.rating = str(args.rating).upper()
    options.score_min = args.score_min
    options.score_max = args.score_max
    options.max_query_size = args.max_posts
    options.percent_posts_to_keep = args.top
    options.start_date = args.start_date
    options.end_date = args.end_date
    options.blacklist_score_threshold = args.blacklist
    options.order = args.order
    options.descending = not args.ascending
    options.recommended_tag_threshold = args.rec_tag_threshold

    # Only check for URL options if url output is enabled
    options.url_only = args.url_only
    if args.url_mode:
        if args.url_mode in ["md5", "url", "full"]:
            options.url_mode = args.url_mode
        # Error out if mode is not a valid string
        else:
            print("Error: Unrecognized url_mode argument. Valid modes:")
            print("  md5")
            print("  url")
            print("  full")
            sys.exit(0)

    # Apply the highest level curse specified
    if args.cursedest:
        translate.set_curse_level(3)
    elif args.curseder:
        translate.set_curse_level(2)
    elif args.cursed:
        translate.set_curse_level(1)
    else:
        translate.set_curse_level(0)

    # Start a thread to print progress reports wile program is running
    t = threading.Thread(target=progressbar.start_progress_bar)
    t.start()

    # Perform tag analysis
    try:
        if args.download:
            # postdownloader has its own progress bar
            progressbar.end_progress_bar()

            # offline_test_mode: Enable during testing
            postdownloader.download_posts(offline_test_mode=False)
        else:
            # Ensure cache exists
            cache.generate_missing_cache()
            # Process queries in Tags In/
            search.read_and_process_queries()

    # Handle general errors
    except util.ExportFileNotFound as e:
        print(f"\n{e.message}")
        print(
            " Did you place the following zipped export files into "
            f"{filepath.export_dir}?"
        )
        print("    posts-YYYY-MM-DD.csv.gz")
        print("    tags-YYYY-MM-DD.csv.gz")
        print("    wiki_pages-YYYY-MM-DD.csv.gz")
    except util.CacheFileNotFound as e:
        print(f"\n{e.message}")
        print(" Please re-run the program to generate the missing cache file.")
    except util.FileNotFound as e:
        print(f"\n{e.message}")
        print(" This is most likely a result of missing user-made files.")
        print(" Re-run the program and some sample files will be generated.")
    except util.InvalidCustomCategory as e:
        print(f"\n{e.message}")
        print(" Ensure the category exists in the following files:")
        print(f"   {filepath.custom_categories}")
        print(f"   {filepath.custom_categories_colors}")
        print(
            " You can also delete the Settings folder,"
            " run the program again, then study the sample files."
        )
    except Exception as e:
        print("\n[ERROR - EXITING EXECUTION]")
        print(traceback.format_exc())

    # End the progress bar thread, as we've finished execution.
    progressbar.end_progress_bar()
    t.join()
