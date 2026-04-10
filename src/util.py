"""Options and Utilities that are used throughout the program."""

import pickle
import os
import json
import math

from utilfilepath import filepath


# [--- Utility Functions ---]
def print_double_sorted_list(in_dict: dict[str, int]) -> str:
    """Return a printable string of sorted key-value pairs.

    PARAMETERS
        in_dict:
            key = tag (str)
            value = post count (int)
    """
    out_str = ""
    if len(in_dict) > 0:
        # Sorted first by post count (descending).
        # If post count is identical, the sort keys alphabetically.
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


# [--- Custom Exceptions ---]
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


# [--- PostData Object ---]
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


# [--- TAG COUNTS ---]
class _TagToPostCount:
    """Maps tags to the count of posts with that tag."""

    def __init__(self):
        """Initialize tag to post id map."""
        self.tags = {}

    def init_tag_to_post_count(self) -> None:
        """Load into memory a map of tags to the count of posts with that tag."""
        with open(filepath.cache_tag_counts, "rt", encoding="utf-8") as in_file:
            self.tags = json.loads(in_file.read())

    def get_post_count(self, tag: str) -> int:
        """Get the count of posts with the input tag."""
        if tag in self.tags:
            return self.tags[tag]
        return 0


# Shared instance of class
tag_to_post_count = _TagToPostCount()


# [--- TAG TO CATEGORY MAP ---]
class _TagToCategory:
    """Maps tags to the owning E6 category."""

    def __init__(self):
        """Initialize tag to category map."""
        self.tags = {}

    def init_tag_to_category(self) -> None:
        """Load into memory a map of tags to the owning E6 category."""
        with open(filepath.cache_tag_to_category, "rt", encoding="utf-8") as in_file:
            self.tags = json.loads(in_file.read())

    def get_category(self, tag: str, print_missing_tag=True):
        """Get the E6 category of the input tag."""
        if tag in self.tags:
            return self.tags[tag]
        if print_missing_tag:
            print(
                f"Warning: Tag {tag} not found in tag to category cache."
                f" Attempting to ignore tag..."
            )
        return None


# Shared instance of class
tag_to_category = _TagToCategory()


def is_tag_valid(tag: str) -> bool:
    """Return true if the tag exists."""
    return tag in tag_to_category.tags


# [--- Bar Charts ---]
class _BarCharts:
    """List of bar chart names and tags."""

    def __init__(self):
        """Initialize bar chart object."""
        # Key: Category/file name
        # Value: list of tags
        self.charts = {}

    def init_bar_charts(self) -> None:
        """Load bar chart info."""
        filenames = os.listdir(filepath.settings_bar_dir)
        # If bar charts were found, check that all the tags are valid
        for file in filenames:
            with open(
                filepath.settings_bar_dir / file, "rt", encoding="utf-8"
            ) as in_file:
                category_name = file.partition(".")[0]
                # Tags
                self.charts[category_name] = []
                for line in in_file:
                    tag_list = []
                    for tag in line.strip().split(" "):
                        # When checking if the tag is valid, remove the negation
                        tag_base = tag[1:] if tag[0] == "-" else tag
                        if is_tag_valid(tag_base):
                            tag_list.append(tag)
                        else:
                            print(
                                f"Warning: [Bar Chart: "
                                f"{filepath.settings_bar_dir / file}]"
                                f" Tag {tag} was not found in the database."
                                f" Skipping tag."
                            )
                    if len(tag_list) > 0:
                        self.charts[category_name].append(tag_list)


# Shared instance of class
bar = _BarCharts()


# [--- Custom Category Tags ---]
class _CustomCategories:
    """List of custom categories with names, colors, and tags."""

    def __init__(self):
        """Initialize custom category object."""
        # Key: Category/file name
        # Value: dict, mapping tag (str) to weight (float)
        self.categories = {}

        # Key: Category/file name
        # Value: MatPlotLib color (str)
        self.colors = {}

    def init_custom_categories(self) -> None:
        """Load a custom category info."""
        filenames = os.listdir(filepath.settings_category_dir)
        # If custom categories were found, check that all the tags are valid
        for file in filenames:
            with open(
                filepath.settings_category_dir / file, "rt", encoding="utf-8"
            ) as in_file:
                category_name = file.partition(".")[0]
                # Color
                color = next(in_file).strip()
                self.colors[category_name] = color
                # Tags
                self.categories[category_name] = {}
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
                        try:
                            float(weight)
                            self.categories[category_name][tag] = float(weight)
                        except ValueError:
                            # Comes up when the weight can't be parsed as a number
                            print(
                                f"Warning: [Custom Category:"
                                f" {filepath.settings_category_dir / file}]"
                                f" {line} contains an invalid weight."
                                f" Skipping tag."
                            )
                            continue
                    else:
                        print(
                            f"Warning: [Custom Category:"
                            f" {filepath.settings_category_dir / file}]"
                            f" Tag {tag} was not found in the database."
                            f" Skipping tag."
                        )


# Shared instance of class
custom = _CustomCategories()


# [--- BLACKLISTED TAGS  ---]
class _BlacklistedTags:
    """List of blacklisted tags."""

    def __init__(self):
        """Initialize blacklist object."""
        self.tags = []

    def init_blacklist(self) -> None:
        """Load a list of blacklisted tags."""
        with open(filepath.blacklisted_tags, "rt", encoding="utf-8") as in_file:
            for tag in in_file:
                tag = tag.strip()
                if tag != "":
                    # Check that the tag exists
                    if is_tag_valid(tag):
                        self.tags.append(tag)
                    else:
                        print(
                            f"Warning: [E6_Blacklist.txt]"
                            f" Tag {tag} was not found in the database."
                            f" Skipping tag."
                        )

    def contains_post(self, post: PostData) -> bool:
        """Return true if post contains any blacklist tags."""
        for category in post.tags.values():
            for tag in category:
                if tag in self.tags:
                    return True
        return False


# Shared instance of class
blacklist = _BlacklistedTags()


# [--- Sample Settings ---]
def generate_sample_searches() -> list:
    """Ensure query files exist."""
    query_list = [
        ["domestic_cat", "slit_pupils"],
        ["loona_(helluva_boss)", "detailed_background"],
        ["~uwu", "-fluffy"],
        ["~uwu", "~heart_gesture"],
    ]
    return query_list


def generate_sample_bar_charts() -> None:
    """Ensure bar chart files exist."""
    # If no bar charts were found, generate some sample bar charts
    filenames = os.listdir(filepath.settings_bar_dir)
    if len(filenames) == 0:
        with open(
            filepath.settings_bar_dir / "Species.txt", "wt", encoding="utf-8"
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
            filepath.settings_bar_dir / "TWYS Gender.txt", "wt", encoding="utf-8"
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
            filepath.settings_bar_dir / "Format.txt", "wt", encoding="utf-8"
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
            filepath.settings_bar_dir / "Group Composition.txt",
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


def generate_sample_custom_categories() -> None:
    """Ensure custom category files exist."""
    # If no custom categories were found, generate some sample categories
    filenames = os.listdir(filepath.settings_category_dir)
    if len(filenames) == 0:
        with open(
            filepath.settings_category_dir / "Detailed Background.txt",
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
            filepath.settings_category_dir / "Furry.txt", "wt", encoding="utf-8"
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
            filepath.settings_category_dir / "Blacklist.txt",
            "wt",
            encoding="utf-8",
        ) as out_file:
            tag_list = [
                "uwu",
            ]
            out_file.write(f"tab:gray\n{"\n".join(tag_list)}\n")


def generate_sample_e6_blacklist() -> None:
    """Ensure E6-style blacklist file exists."""
    if not filepath.blacklisted_tags.exists():
        filepath.blacklisted_tags.touch()
