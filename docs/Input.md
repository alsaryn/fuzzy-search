# Overview of Input

**Searches** tells Fuzzy search *what* posts to look at.

**Arguments** tell Fuzzy Search *how* to process those posts, and what output to produce.

**Settings** are more complex arguments that involve more setup but offer granular customization.

## Searches
Searching on Fuzzy Search functions similarly to how you search on E6. You give Fuzzy Search a list of tags in order for it to know what posts you want to be analyzed.

**Example Searches**

```text
feline
feline canine
feline -canine
~feline ~canine
```

**Search Syntax**

A search contains one or more space-separated tags, defining what posts are contained in the search.
- Posts must contain all regular tags in the search (boolean AND)
- Posts must contain at least one of the specified ~tags (boolean OR)
- Posts must not contain any -tag (boolean NOT)
- The order of tags is ignored; there is no () operator

**Searches Are Stored As Input Files**

Fuzzy Search reads searches from text files in the `Tags In` folder. This facilitates processing thousands of searches at once (this is a tool for power users, after all). This also makes it easy to download the latest version of E6's Database and re-run the same queries by copy-pasting the text files.
- Fuzzy Search will process all .txt files in `Tags In`.
- Each line of a .txt file is a separate search.

**Making Sure Search Tags are Spelled Correctly**

Fuzzy Search doesn't offer a spell-check feature
- To make sure you've typed in the right tag (and have a sense of the amount of posts associated with it), either use E6's search or take a look at Fuzzy Search's Wiki files
- If Fuzzy Search doesn't recognize a tag, it'll print a message and move onto the next search.

**The All Tag**

Fuzzy Search also has a special tag, `_all_posts_`, which includes all posts in the database.
- It's perfectly fine to use `_all_posts_` with negated (`-`) tags or search filters (see the command line arguments section) to bring down the total search size to something reasonable.
- If your goal is to process the million posts in E6's database all at once, you'll want a machine with around 64 GB of RAM. Fuzzy Search was never optimized to handle that many posts at once.

## Arguments

**Run Fuzzy Search**

```bash
# By default, the command prompt starts in your user or home folder.
# Move into the folder containing fuzzysearch.py:
cd Downloads
cd FuzzySearch

# Run Fuzzy Search's analysis tools (with all output enabled):
python fuzzysearch.py --all

# To run the post downloader (make sure you have URL files in th Posts folder):
python postdownloader.py
```

---
**General**

```bash
# Use the designated folder to store the Cache, Exports, Posts, Settings, Tags In, Tags Out, and Wiki folders
--data_dir /path/to/folder/
```

---
**Toggle Analysis Outputs**

```bash
# Enable all analysis outputs
--all

# Similar Tags.txt
# Enable recommended/similar tags output
--recommended

# Post Data.txt
# Enable text dump of posts
--posts

# Include sources with dumped post data
--source

# Include descriptions with dumped post data
--description

# Include video length (for animated files) with dumped post data
--duration

# Tag Counts By E6 Category.txt
--counts

# Tag Counts By Custom Category.txt
# Also enables --counts.
--counts_custom

# Percentile <...>.png, Scatter Plot Custom.png
--charts_custom

# Bar Chart<...>.png
--bar

# Scatter Plot Post Score.png
--score

# Urls.txt
--url

# Enable Obsidian graphs.
# Only generated for searches with <num> or less posts.
# Warning: Obsidian's graph system struggles to handle high numbers of posts/tags. For safety, avoid going over 1,000 posts.
--graph <num>
# Example: generate Obsidian vaults for searches with 500 or less posts
--max_posts 200000
```

---
**URL Options**

```bash
# Only output URL information (all other analysis is omitted)
--url_only

# Change the format of URL output to be a certain mode.
# "md5": only the md5 hash  
# "url": only the static url  
# "full": post id, static url, and filesize. Default.
--url_mode <mode>
```

---
**Filters**

```bash
# Sets the maximum amount of posts a search can contain.
# This limit is here to prevent users from accidentally processing a search that was way larger than they expected.
--max_posts <num>
# Example: set the search size to the default of 200 thousand:
--max_posts 200000

# Start: excludes all posts before this date
# End: excludes all posts after this date
# Dates are in YYYY-MM-DD
--start_date <date>
--end_date <date>
# Example: look at posts in 2025
--start "2025-01-01" --end "2025-12-31"

# score_min: Excludes all posts with less than this score
# score_max: Excludes all posts with more than this score
--score_min <num>
--score_max <num>
# Example: look at posts between 20 and 40 score
--score_min 20 --score_max 40

# Include posts of the specified rating.
# Default: "SQE", meaning posts of all 3 ratings are included
--rating <string>
# Only include posts with the 'Safe' rating
--rating "S"

# UwU-ifies text.
# Only affects runtime messages and post descriptions (--description).
# Three levels of cursed text, for your pleasure.
--cursed
--curseder
--cursedest

# Filter out posts with a custom category Blacklist relevancy higher than the threshold.
# Note: The traditional strict blacklist is always applied in addition to the Blacklist custom category
--blacklist <threshold>
# Example: hide any post that has a relevancy of 5 or more in the Blacklist category:
--blacklist 5.0

# Sort posts by custom category relevancy.
# Use the name of the category (in quotations, without the ".txt" extension) as the argument.
# Default order is post creation date.
--order <category_name>
# Example: sort posts by their relevancy to the "Detailed Background" category:
--order "Detailed Background"
# This is a special category that sorts posts containing the most to least ~tags.
--order "~"

# Order posts in ascending order (default: descending)
--ascending

# Keep only the top <num> percent of posts.
# Top means the first posts listed, based on how the posts are sorted.
--top <num>
# Example: keep the top 20% of posts, excluding the other 80% of posts in the search
--top 5.0


# --recommended: only rank tags that are present in <threshold> percent of the searched posts.
--rec_tag_threshold <threshold>
# Example: hide all tags containing 2% or less of the searched posts:
--rec_tag_threshold 2
```

## Downloading Posts
Fuzzy Search's built-in post downloader, while configured to work with Fuzzy Search's output, is quite basic compared to dedicated batch downloaders.
- If you are downloading tens of thousands of posts, consider using a dedicated downloader.

URL Format
- The built-in downloader reads text files placed in Fuzzy Search's `Posts` folder.
- The built-in downloader expects the files to be formatted via `--url_only --url_mode full`

To run the downloader:

```bash
# Move into the folder with Fuzzy search's .py files, then run the following:
python postdownloader.py
```

The downloader will read each URL, download the post file, and output the post file (named after the E6 post id) in a folder (named after the URL file).

## Settings
All of the following settings can be found as files inside the `Settings` folder.

Fuzzy Search creates samples of all these settings during your first run for use as references.

### Bar Charts
These determine the output of the `--bar` argument.

Inside the `Settings/Bar Charts` folder, each file corresponds to a single bar chart.
- The filename is the name of the bar chart
- The contents of the file are interpreted as a list of tags, each corresponding to their own bar
	- Within each row, you can group multiple tags together as a single bar, or even negate tags.

**Example**: `Settings/Bar Charts/Group Composition.txt`

```
solo
solo male
solo female
duo
duo -male
duo -female
trio
group
zero_pictured
```

### Custom Categories
Custom categories are collections of related tags. Custom categories are used for a variety of purposes across Fuzzy Search, such as sorting ports based on how many tags from the custom category they contain.

Inside the `Settings/Custom Categories` folder, each file corresponds to a single category.
- The first line is a color
- The remaining lines are all tags and (optionally) a corresponding weight

**Example**: `Settings/Bar Charts/Detailed Background.txt`

```text
tab:green
detailed_background 2.0
day
sky
outside
forest
grass
smartphone 0.5
simple_background -1.0
```

---

**The More, the Merrier!**
The more tags you associate with a category, the smoother the charts will look.
- Tip: use `--recommended` and `--counts` to quickly find relevant tags!

To illustrate the impact the amount of tags makes, compare two analyses of the same search:
- Left chart: about 10 tags tags per custom category
- Right chart: about 1,500 tags per custom category

![Two side-by-side score charts showing impact of custom category size.](/images/fs/custom_category_size_dif.png)

Here's a second example, with a percentile chart:

![Two side-by-side percentile charts showing impact of custom category size.](/images/fs/custom_category_size_dif_percentile.png)

#### Color
The first line of each custom category file specifies the color associated with that category in chart images. Below are some common choices; for the full list of accepted colors, see the MatPlotLib documentation: https://matplotlib.org/stable/users/explain/colors/colors.html
- `tab:blue`
- `tab:orange`
- `tab:green`
- `tab:red`
- `tab:purple`
- `tab:brown`
- `tab:pink`
- `tab:gray`
- `tab:olive`
- `tab:cyan`

#### Weights
The number written after each tag is its weight (you can think of this as a score).
- If you don't specify a weight, it'll default to 1.0
	- A custom category that has a weight of 1 for all tags is referred to as an "all-ones" custom category, and functions as a tag count
- Increase the weight to give more impact to extremely relevant tags
- Decrease the weight to give less impact to slightly related tags
- Use negative weights on tags mutually exclusive with what the custom category is trying to measure

If you are new to Fuzzy Search, it is suggested to leave all the weights at 1. Only use weights when you are familiar with how custom categories function and need to fine-tune results.

### Blacklist
Fuzzy Search uses two blacklists:
- A "hard", E6-style blacklist which hides any post with a given tag
- A "soft", fuzzy-style blacklist which hides posts that are "too relevant" to the Blacklist custom category

#### Hard, E6-style Blacklist:
Specified by a file called "E6_Blacklist.txt" in the `Settings` folder
- Each tag goes on its own line.
- Any post with such a tag will be hidden.
- This blacklist is always applied to search results.
- Use the hard blacklist for tags that, under no circumstances, should be visible.

#### Soft, Fuzzy-style Blacklist
1. Specified by a custom category file named "Blacklist.txt" in the `Settings/Custom Categories` folder
	- Each tag and (optionally) corresponding weight goes on its own line
2. Use the `--blacklist <threshold>` argument to apply the soft blacklist when processing searches. This argument is not applied by default. The hard, E6-style blacklist is always applied, whether or not the soft blacklist is used.

Any post that has a *cumulative* blacklist relevancy above the specified threshold will be hidden. In other words:
- Posts with little to no soft blacklisted tags will remain visible.
- Posts with too many soft blacklisted tags will be hidden.

Use the soft blacklist for tags that you dislike, but would be okay seeing if the rest of the post is relatively free of other blacklisted content.

---
[Fuzzy Search](https://github.com/alsaryn/fuzzy-search)