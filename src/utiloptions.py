"""Provide options used throughout Fuzzy Search.."""


class _Options:
    """Provide options used throughout Fuzzy Search."""

    def __init__(self):
        """Initialize progress bar."""
        # [--- GENERAL ---]
        # Magic Numbers
        self.num_posts = 6474395
        self.num_tags = 786525
        # Special include tag invoking ALL posts in the database
        self.all_posts = "_all_posts_"
        # Special custom category, representing an all-ones tally of the ~tags in query
        self.or_category = "~"
        # Store info on if the cache warning message has been printed already
        self.has_printed_cache_warning_message = False
        # Enable new analysis on existing output folders
        self.override = False

        # [--- Toggle Analysis Outputs ---]
        # similar_tags.txt
        self.recommended = False
        # Only recommend tags of the following E6 categories:
        # recommended_tags = ["general", "artist", "character"]
        self.recommended_tags = [
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
        # tags.txt
        self.posts = False
        # Add sources/descriptions/durations to post data output
        self.source = False
        self.description = False
        self.duration = False
        # urls.txt
        self.url = False
        # tag_counts_by_E6_category.txt
        self.counts = False
        # tag_counts_by_custom_category.txt
        self.counts_custom = False
        # Percentile <...>.png, Scatter Plot Custom Categories.png
        self.charts_custom = False
        # Bar Chart<...>.png
        self.bar_charts = False
        # Scatter Plot Score.png
        self.score = False
        # Don't generate Obsidian graphs with more than this amount of posts
        self.graph = 0

        # [--- URL ---]
        # Only generate text files with lists of urls of the given query
        self.url_only = False
        # Mode determines the format of each url and additional info
        # "md5": only the md5 hash
        # "url": only the static url
        # "full": full static url, post id, and filesize
        self.url_mode = "full"

        # [--- Filters ---]
        # Queries above this size are not processed
        self.max_query_size = 200000
        # Set start/end ranges of data
        self.start_date = None
        self.end_date = None
        # Filter post outside a score range
        self.score_min = None
        self.score_max = None
        # Filter posts to only include the specified ratings
        self.rating = "SQE"
        # Omit posts that score higher than this in the Blacklist custom category
        self.blacklist_score_threshold = 0.0
        # Order to display posts
        self.order = ""
        self.descending = True
        # Filter the bottom percent of posts
        self.percent_posts_to_keep = 100.0
        # Only recommend tags that occupy more than <threshold>% of the set
        self.recommended_tag_threshold = 2.0


# Shared instance of class
options = _Options()
