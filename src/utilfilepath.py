"""Provide access to pathlib Paths for all file I/O locations."""

import pathlib
import os


class _Filepath:
    """Provide access to pathlib Paths for all file I/O locations."""

    def __init__(self):
        """Initialize default paths."""
        # Directories
        self.root = pathlib.Path(os.getcwd())
        self.cache_dir = self.root / "Cache"
        self.export_dir = self.root / "Exports"
        self.tags_in_dir = self.root / "Tags In"
        self.tags_out_dir = self.root / "Tags Out"
        self.wiki_dir = self.root / "Wiki"
        self.settings_dir = self.root / "Settings"
        self.settings_bar_dir = self.settings_dir / "Bar Charts"
        self.settings_category_dir = self.settings_dir / "Custom Categories"
        self.downloads_dir = self.root / "Posts"

        # Cache
        self.cache_tag_to_category = self.cache_dir / "tag_to_category.json"
        self.cache_tag_counts = self.cache_dir / "tag_counts.json"
        self.cache_post_data_database = self.cache_dir / "post_data.db"
        self.cache_post_data_sources = self.cache_dir / "post_data_sources.db"
        self.cache_post_data_descriptions = self.cache_dir / "post_data_descriptions.db"
        self.cache_post_data_durations = self.cache_dir / "post_data_durations.db"
        self.cache_postid_database = self.cache_dir / "postid.db"
        self.cache_info = self.cache_dir / "cache_info.json"

        # Wiki
        self.output_wiki_pages = self.wiki_dir / "Wiki.txt"

        # Custom Categories
        self.custom_categories = self.settings_dir / "Custom Categories.json"
        self.custom_categories_colors = (
            self.settings_dir / "Custom Categories Colors.json"
        )
        self.custom_charts = self.settings_dir / "Custom Charts.json"
        self.blacklisted_tags = self.settings_dir / "E6_Blacklist.txt"

        # Misc Filenames
        self.similar_tags = "Recommended Tags.txt"
        self.per_post_data = "Post Data.txt"
        self.per_post_sources = "Post Data (Sources).txt"
        self.per_post_descriptions = "Post Data (Descriptions).txt"
        self.per_post_durations = "Post Data (Durations).txt"
        self.sample_queries = "Sample Searches.txt"
        self.urls_filename = "Post Data (URLs).txt"
        self.tag_counts_e6_category = "Tag Counts By E6 Category.txt"
        self.tag_counts_custom_category = "Tag Counts By Custom Category.txt"
        self.scatter_plot_custom = "Scatter Plot Custom.png"
        self.scatter_plot_score_upload_date = "Scatter Plot Score.png"
        self.scatter_plot_score_tag_count = "Scatter Plot Tag Count.png"

    def set_root(self, root: pathlib.Path):
        """Initialize paths from root directory."""
        # Directories
        # (also make sure directories exist)
        self.root = root
        self.cache_dir = self.root / "Cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir = self.root / "Exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.tags_in_dir = self.root / "Tags In"
        self.tags_in_dir.mkdir(parents=True, exist_ok=True)
        self.tags_out_dir = self.root / "Tags Out"
        self.tags_out_dir.mkdir(parents=True, exist_ok=True)
        self.wiki_dir = self.root / "Wiki"
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
        self.settings_dir = self.root / "Settings"
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.settings_bar_dir = self.settings_dir / "Bar Charts"
        self.settings_bar_dir.mkdir(parents=True, exist_ok=True)
        self.settings_category_dir = self.settings_dir / "Custom Categories"
        self.settings_category_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_dir = self.root / "Posts"
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

        # Cache
        self.cache_tag_to_category = self.cache_dir / "tag_to_category.json"
        self.cache_tag_counts = self.cache_dir / "tag_counts.json"
        self.cache_post_data_database = self.cache_dir / "post_data.db"
        self.cache_post_data_sources = self.cache_dir / "post_data_sources.db"
        self.cache_post_data_descriptions = self.cache_dir / "post_data_descriptions.db"
        self.cache_post_data_durations = self.cache_dir / "post_data_durations.db"
        self.cache_postid_database = self.cache_dir / "postid.db"
        self.cache_info = self.cache_dir / "cache_info.json"

        # Wiki
        self.output_wiki_pages = self.wiki_dir / "Wiki.txt"

        # Custom Categories
        self.custom_categories = self.settings_dir / "Custom Categories.json"
        self.custom_categories_colors = (
            self.settings_dir / "Custom Categories Colors.json"
        )
        self.custom_charts = self.settings_dir / "Custom Charts.json"
        self.blacklisted_tags = self.settings_dir / "E6_Blacklist.txt"


# Shared instance of class
filepath = _Filepath()
