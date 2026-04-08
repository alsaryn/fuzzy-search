"""Options/Utilities that are used throughout the program."""

import pathlib
import pickle
import os
import json
import math

from uwuipy import Uwuipy


def print_tr(text: str) -> None:
    """Print a string, with optional translation."""
    # TODO: When python 3.15 is more stable, will be updated to use the lazy keyword.
    #  Lazy import is nice to simplify instructions for basic usage of Fuzzy Search.
    if Options.uwu:
        print(Options.uwu.uwuify(text))
    else:
        print(text)


def get_tr(text: str) -> str:
    """Translate a string."""
    if Options.uwu:
        return Options.uwu.uwuify(text)
    return text


def set_curse_level(level: int) -> None:
    """Set level of uwu-ified text."""
    if level == 0:
        # no change
        Options.uwu = None
    elif level == 1:
        # Just text translation
        Options.uwu = Uwuipy(None, 0.0, 0.0, 0.0, 0, False, 1)
    elif level == 2:
        # more nya-nya, faces, stutters, actions
        Options.uwu = Uwuipy(None, 0.1, 0.05, 0.075, 0.5, False, 2)
    else:
        # Awful
        Options.uwu = Uwuipy(None, 0.3, 0.3, 0.3, 1, True, 4)
        Options.uwu = Uwuipy()


def print_double_sorted_list(in_dict: dict[str, int]) -> str:
    """Return a printable string of sorted key-value pairs."""
    # in_dict: key = tag (str), value = post count (int)
    # Sorted first by post count (descending)
    # If post count is identical, the sort keys alphabetically.

    out_str = ""
    if len(in_dict) > 0:
        srt = sorted(in_dict.items(), key=lambda kv: (kv[0]), reverse=False)
        srt = sorted(srt, key=lambda kv: (kv[1]), reverse=True)
        for tag_count in srt:
            out_str += f"{str(tag_count[1])} {str(tag_count[0])}\n"
        out_str += "\n"
    return out_str


def get_average(in_list: list) -> float:
    """Calculate the average value of a list."""
    avg = 0
    for val in in_list:
        avg += val
    return round(avg / len(in_list), 2)


def get_median(in_list: list) -> float:
    """Calculate the median value of a list."""
    if len(in_list) == 0:
        return 0.0
    if len(in_list) % 2 == 0:
        # In the case the in_list has an even number of elements,
        # pick the average of the 2 middle elements.
        srt = sorted(in_list)
        middle_index = int(len(in_list) / 2)
        return int((srt[middle_index - 1] + srt[middle_index]) / 2)
    # In the case in_list has an odd number of elements, pick the middle element
    srt = sorted(in_list)
    return srt[math.floor(len(in_list) / 2)]


class Filepath:
    """Provide access to pathlib Paths for all I/O file locations."""

    # Initialize filepaths with set_root()

    # Directories
    root = None
    cache_dir = None
    export_dir = None
    tags_in_dir = None
    tags_out_dir = None
    wiki_dir = None
    settings_dir = None
    settings_bar_dir = None
    settings_category_dir = None
    downloads_dir = None

    # Cache
    cache_tag_to_category = None
    cache_tag_counts = None
    cache_post_data_database = None
    cache_post_data_sources = None
    cache_post_data_descriptions = None
    cache_post_data_durations = None
    cache_postid_database = None
    cache_info = None

    # Wiki
    output_wiki_pages = None

    # Custom Categories
    custom_categories = None
    custom_categories_colors = None
    custom_charts = None
    blacklisted_tags = None

    # Misc Filenames
    similar_tags = "Similar Tags.txt"
    per_post_data = "Post Data.txt"
    per_post_sources = "Post Data (Sources).txt"
    per_post_descriptions = "Post Data (Descriptions).txt"
    per_post_durations = "Post Data (Durations).txt"
    sample_queries = "Sample Searches.txt"
    urls_filename = "Post Data (URLs).txt"
    tag_counts_e6_category = "Tag Counts By E6 Category.txt"
    tag_counts_custom_category = "Tag Counts By Custom Category.txt"
    scatter_plot_custom = "Scatter Plot Custom.png"
    scatter_plot_score_upload_date = "Scatter Score-Upload.png"
    scatter_plot_score_tag_count = "Scatter Score-Tag Count.png"


def set_root(root: pathlib.Path) -> None:
    """Set the root folder and update Paths for all I/O file locations."""
    # Directories
    Filepath.root = root
    Filepath.cache_dir = root / "Cache"
    Filepath.export_dir = root / "Exports"
    Filepath.tags_in_dir = root / "Tags In"
    Filepath.tags_out_dir = root / "Tags Out"
    Filepath.wiki_dir = root / "Wiki"
    Filepath.settings_dir = root / "Settings"
    Filepath.settings_bar_dir = Filepath.settings_dir / "Bar Charts"
    Filepath.settings_category_dir = Filepath.settings_dir / "Custom Categories"
    Filepath.downloads_dir = root / "Posts"

    # Cache
    Filepath.cache_tag_to_category = Filepath.cache_dir / "tag_to_category.json"
    Filepath.cache_tag_counts = Filepath.cache_dir / "tag_counts.json"
    Filepath.cache_post_data_database = Filepath.cache_dir / "post_data.db"
    Filepath.cache_post_data_sources = Filepath.cache_dir / "post_data_sources.db"
    Filepath.cache_post_data_descriptions = (
        Filepath.cache_dir / "post_data_descriptions.db"
    )
    Filepath.cache_post_data_durations = Filepath.cache_dir / "post_data_durations.db"
    Filepath.cache_postid_database = Filepath.cache_dir / "postid.db"
    Filepath.cache_info = Filepath.cache_dir / "cache_info.json"

    # Wiki
    Filepath.output_wiki_pages = Filepath.wiki_dir / "Wiki.txt"

    # Custom Categories
    Filepath.custom_categories = Filepath.settings_dir / "Custom Categories.json"
    Filepath.custom_categories_colors = (
        Filepath.settings_dir / "Custom Categories Colors.json"
    )
    Filepath.custom_charts = Filepath.settings_dir / "Custom Charts.json"
    Filepath.blacklisted_tags = Filepath.settings_dir / "E6_Blacklist.txt"


def ensure_dirs_exist() -> None:
    """Ensure directories exist."""
    Filepath.cache_dir.mkdir(parents=True, exist_ok=True)
    Filepath.export_dir.mkdir(parents=True, exist_ok=True)
    Filepath.tags_in_dir.mkdir(parents=True, exist_ok=True)
    Filepath.tags_out_dir.mkdir(parents=True, exist_ok=True)
    Filepath.wiki_dir.mkdir(parents=True, exist_ok=True)
    Filepath.settings_dir.mkdir(parents=True, exist_ok=True)
    Filepath.settings_bar_dir.mkdir(parents=True, exist_ok=True)
    Filepath.settings_category_dir.mkdir(parents=True, exist_ok=True)
    Filepath.downloads_dir.mkdir(parents=True, exist_ok=True)


class Options:
    """Get and set options referenced across the program."""

    # Special include tag invoking ALL posts in the database
    all_posts = "_all_posts_"
    # Special custom category, representing an all-ones tally of the or tags in query
    or_category = "~"

    # Queries above this size are not processed
    max_query_size = 200000

    # Filter the bottom percent of posts
    percent_posts_to_keep = 100.0

    # Filter posts to only include the specified ratings
    rating = "SQE"

    score_min = None
    score_max = None

    # Only generate text files with lists of urls of the given query
    url_only = False
    # Mode determines the format of each url and additional info
    # "md5": only the md5 hash
    # "url": only the static url
    # "full": full static url, post id, and filesize
    url_mode = "full"

    # Magic Numbers
    # TODO: use the read_last_line function
    num_posts = 6074395
    num_tags = 786525

    # Total queries; set at runtime.
    # This number is used to determine how to utilize multiple cores.
    # If queries < cores, then each query is sequentially processed,
    # with the recommendation algorithm processed via a MapReduce framework.
    # If queries >= cores, then each query is processed by a different core.
    parallelize_query_subtask = False

    # Toggle portions of output
    # similar_tags.txt
    recommended = False
    # tags.txt
    posts = False
    # tag_counts_by_E6_category.txt
    counts = False
    # tag_counts_by_custom_category.txt
    counts_custom = False
    # Percentile <...>.png, Scatter Plot Custom Categories.png
    charts_custom = False
    # Bar Chart<...>.png
    bar_charts = False
    # Scatter Plot Score.png
    score = False
    # urls.txt
    url = False
    # Add sources/descriptions/durations to post data output
    source = False
    description = False
    duration = False
    # Don't generate Obsidian graphs with more than this amount of posts (0 to disable)
    graph = 0

    # Whether to generate and display tags similar to the query
    find_recommended_tags = True
    # Only recommend tags of the following E6 categories:
    # recommended_tags = ["general", "artist", "character"]
    recommended_tags = [
        "artist",
        "contributor",
        "copyright",
        "character",
        "species",
        "general",
        "invalid",
        "meta",
        "lore",
    ]

    # Only recommend tags that occupy more than <threshold>% of the set
    recommended_tag_threshold = 2
    # Omit posts that score higher than this threshold in the Blacklist custom category
    blacklist_score_threshold = 0.0
    # Order to display posts
    order = ""
    descending = True

    # Set start/end ranges of data
    start_date = None
    end_date = None

    # Uwu-ify text
    uwu = None

    # Store info on if the cache warning message has been printed already
    has_printed_cache_warning_message = False


class FileNotFound(Exception):
    """Custom Exception, for use when a file was not found."""

    def __init__(self, message="File Not Found", value=None):
        """Produce an error message."""
        self.message = message
        self.value = value
        super().__init__(self.message)


class ExportFileNotFound(Exception):
    """Custom Exception, for use when an export was not found."""

    def __init__(self, message="Export File Not Found", value=None):
        """Produce an error message."""
        self.message = message
        self.value = value
        super().__init__(self.message)


class CacheFileNotFound(Exception):
    """Custom Exception, for use when a cache file was not found."""

    def __init__(self, message="Cache File Not Found", value=None):
        """Produce an error message."""
        self.message = message
        self.value = value
        super().__init__(self.message)


class InvalidCustomCategory(Exception):
    """Custom Exception, for use when a custom category has an error."""

    def __init__(self, message="Custom Category Invalid", value=None):
        """Produce an error message."""
        self.message = message
        self.value = value
        super().__init__(self.message)


class TagCategoryNotFound(Exception):
    """Custom Exception, for use when a tag has no E6 category."""

    def __init__(self, message="Tag Category Not Found", value=None):
        """Produce an error message."""
        self.message = message
        self.value = value
        super().__init__(self.message)


class InvalidTag(Exception):
    """Custom Exception, for use when a tag is not found in the database."""

    def __init__(self, message="Invalid Tag", value=None):
        """Produce an error message."""
        self.message = message
        self.value = value
        super().__init__(self.message)


class PostData:
    """Provides convenient access to members of a pre-processed post in the database."""

    def __init__(self, data):
        """Initialize members from a table row."""
        # Data is all members from a query to the post database.
        self.post_id = data[0]
        # The rating string mimics E6's current format:
        # rating = f"({score} {favs} C{comments_counts} {rating_char(E, Q, or S)}"
        self.rating_str = f"{data[1]} {data[2]} C{data[3]} {data[4]}"
        self.created_at = data[5]
        self.md5 = data[6]
        self.file_size = data[7]
        self.file_ext = data[8]
        self.tags = pickle.loads(data[9])


# [--- Bar Charts ---]
class BarCharts:
    """List of bar chart names and tags."""

    # Key: Category/file name
    # Value: list of tags (str)
    categories = {}


def init_bar_charts() -> None:
    """Load bar chart info."""
    filenames = os.listdir(Filepath.settings_bar_dir)
    # If bar charts were found, check that all the tags are valid
    for file in filenames:
        with open(Filepath.settings_bar_dir / file, "rt", encoding="utf-8") as in_file:
            category_name = file.partition(".")[0]
            # Tags
            BarCharts.categories[category_name] = []
            for line in in_file:
                tag_list = []
                for tag in line.strip().split(" "):
                    # When checking if the tag is valid, remove the negation
                    tag_base = tag[1:] if tag[0] == "-" else tag
                    if is_tag_valid(tag_base):
                        tag_list.append(tag)
                    else:
                        print(
                            f"Warning: [Bar Chart: {Filepath.settings_bar_dir / file}]"
                            f" Tag {tag} was not found in the database."
                            f" Skipping tag."
                        )
                if len(tag_list) > 0:
                    BarCharts.categories[category_name].append(tag_list)


# [--- Custom Category Tags ---]
class CustomCategories:
    """List of custom categories with names, colors, and tags."""

    # Key: Category/file name
    # Value: dict, mapping tag (str) to weight (float)
    categories = {}

    # Key: Category/file name
    # Value: MatPlotLib color (str)
    colors = {}


def init_custom_categories() -> None:
    """Load a custom category info."""
    filenames = os.listdir(Filepath.settings_category_dir)
    # If custom categories were found, check that all the tags are valid
    for file in filenames:
        with open(
            Filepath.settings_category_dir / file, "rt", encoding="utf-8"
        ) as in_file:
            category_name = file.partition(".")[0]
            # Color
            color = next(in_file).strip()
            CustomCategories.colors[category_name] = color
            # Tags
            CustomCategories.categories[category_name] = {}
            for line in in_file:
                line = line.strip()
                # Default weight of 1.0
                if len(line.split(" ")) == 1:
                    tag = line
                    weight = 1.0
                # If specified, use the weight in the file
                else:
                    tag, weight = line.strip().split(" ")

                if is_tag_valid(tag):
                    CustomCategories.categories[category_name][tag] = float(weight)
                else:
                    print(
                        f"Warning: [Custom Category:"
                        f" {Filepath.settings_category_dir / file}]"
                        f" Tag {tag} was not found in the database."
                        f" Skipping tag."
                    )


# [--- BLACKLISTED TAGS  ---]
class BlacklistedTags:
    """List of blacklisted tags."""

    tags = []


def init_blacklist() -> None:
    """Load a list of blacklisted tags."""
    with open(Filepath.blacklisted_tags, "rt", encoding="utf-8") as in_file:
        for tag in in_file:
            tag = tag.strip()
            if tag != "":
                # Check that the tag exists
                if get_category(tag) is None:
                    print(f"  Blacklist: tag {tag} is invalid, skipping tag.")
                else:
                    BlacklistedTags.tags.append(tag)


def post_blacklisted(post: PostData) -> bool:
    """Return true if post contain any blacklist tags."""
    for category in post.tags.values():
        for tag in category:
            if tag in BlacklistedTags.tags:
                return True
    return False


# [--- TAG COUNTS ---]
class TagToPostCount:
    """Maps tags to the count of posts with that tag."""

    tags = {}


def init_tag_to_post_count() -> None:
    """Load into memory a map of tags to the count of posts with that tag."""
    with open(Filepath.cache_tag_counts, "rt", encoding="utf-8") as in_file:
        TagToPostCount.tags = json.loads(in_file.read())


def get_post_count(tag: str) -> int:
    """Get the count of posts with the input tag."""
    if tag in TagToPostCount.tags:
        return TagToPostCount.tags[tag]
    return 0


# [--- TAG TO CATEGORY MAP ---]
class TagToCategory:
    """Maps tags to the owning E6 category."""

    tags = {}


def init_tag_to_category() -> None:
    """Load into memory a map of tags to the owning E6 category."""
    with open(Filepath.cache_tag_to_category, "rt", encoding="utf-8") as in_file:
        TagToCategory.tags = json.loads(in_file.read())


def get_category(tag: str, print_missing_tag=True):
    """Get the E6 category of the input tag."""
    if tag in TagToCategory.tags:
        return TagToCategory.tags[tag]
    if print_missing_tag:
        print(
            f"Warning: Tag {tag} not found in tag to category cache."
            f" Attempting to ignore tag..."
        )
    return None


def is_tag_valid(tag: str) -> bool:
    """Return true if the tag exists."""
    return tag in TagToCategory.tags
