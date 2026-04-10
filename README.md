# Fuzzy Search

## Overview
Fuzzy Search is a powerful, customizable alternative to E6's search functionality. It's a collection of search, tag analysis, post sorting, and data visualization tools, accessed through the command line interface (CLI).

To manage server load, E6 is constrained to processing a single page of posts at a time. Meanwhile, Fuzzy Search can leverage your personal machine to sort and analyze millions of posts at a time. That enables a *lot* of pretty cool ways to analyze searches and visualize data.

---
 **What is Fuzzy Search used for?**

Fuzzy Search is designed to easily answer questions such as these:
- How can I find more tags like `this_really_cool_tag`?
- How has a tag's score/posting rate changed over time?
- What were the most popular characters in 2025?
- What artists have drawn the most of `my_favorite_character`?
- What general tags does this `artist` specialize in?
- How can I compare two artists?
- How can I sort posts by number of ~tags?
- How can I sort posts by relevancy to a list of tags I like?
- How can I sort posts by relevancy to a list of tags I *dis*like?
- What if E6 had a "3-strikes" system of blacklisting?
- What if E6 had scuffed charts?

The [Examples](docs/Examples.md) page describes how to use Fuzzy Search to answer these questions and more!

### Features
- Uses tag-based searches as input
	- Similar syntax to searches on E6
- Operates on a local copy of E6's database exports
	- Can process millions of posts at once, rather than a single page (75-300) posts
- Run via command line
	- Works on Windows/Mac/Linux
	- (Step-by-step guide for those new to the command line further below)
- Variety of output formats
	- Text!
	- Charts!
	- Obsidian graphs!
- Customizable
	- Enable/disable particular outputs
	- Customize chart colors and tags
	- Custom categories
		- Let's you define "relevancy" when sorting posts
	- Obligatory UwU mode
- Built-in post downloader
	- This is the only part of Fuzzy Search that requires an internet connection; all other functionality is run offline.

Optimized for processing hundreds of small searches (10,000 or less posts)
- Multi-core processing
- Inverted index caching
- Sparse and Dense Recommendation Algorithms
- Not optimized for large searches (100,000+ posts)
	- Processes thousands of posts in seconds
	- Processes millions of posts in minutes

Transparent
- No AI "blackbox" shenanigans
- Deterministic (no random factors)
- Recommendations provide numerical basis for why tags are ranked in the order they are

### Hardware Requirements
Storage: 10 GB

Minimum RAM: 8 GB
- This lets you safely process searches with up to a million posts at once (should be plenty for most users)

Optimal/Max RAM: 64 GB
- As a rule of thumb, a search containing 1 million posts takes 8 GB of RAM to process
- As of April 2026, there are 5.6 million active E6 posts that Fuzzy Search can parse (leading to about 48 GB RAM max usage).

### Output
Fuzzy Search outputs the results of each search as a folder:
- (the numbers on the end are the total posts and the median post score)

![List of folders.](/images/fs/folder_searches.png)

Each folder contains analysis results for that search:

![Folder containing text and image files.](/images/fs/folder_output.png)

## Basic Usage

### Download Files
1. Download and unzip Fuzzy Search's [latest release](https://github.com/alsaryn/fuzzy-search/releases)
2. Download the latest E6 Database Export (you can easily find it with a browser search, the URL ends with `db_export`)
	- Leave the export files in their compressed state!
3. Place the following export files into Fuzzy Search's `Exports` folder:
	- posts-YYYY-MM-DD.csz.gz
	- tags-YYYY-MM-DD.csz.gz
	- wiki_pages-YYYY-MM-DD.csz.gz

**Suggested File Structure**

To follow along with the tutorial for the command line, please place the FuzzySearch folder into your Downloads folder as seen below:

![Image of folder hierarchy.](/images/fs/folder_suggested_structure.png)

### Install Libraries
1. Download and install [Python](https://www.python.org/downloads/)
	- Fuzzy Search works on Python 3.12 and later
2. Open the command line interface (CLI)
	- This is usually called PowerShell on Windows or Terminal on Mac; just type "terminal" into your computer's search bar and it'll be the first application listed
3. Type the following into the command line:

```bash
pip install numpy matplotlib uwuipy requests
```

If the command `pip` isn't recognized, restart your computer. Restarting helps your computer find Python's installation, and with it `pip`.

Congrats! You've now installed the math, data visualization, text translation, and post downloading software used by Fuzzy Search!

### Run Fuzzy Search
In the command line, type the following:
- (Note: you don't have to type the grayed-out text following the "#" mark; these are comments that explain what each command does)

```bash
# By default, the command prompt starts in your user or home folder.
# Move into the folder containing fuzzysearch.py:
cd Downloads
cd FuzzySearch

# Run Fuzzy Search with the Python interpreter and all analysis outputs enabled
python fuzzysearch.py --all
```

On your first run, Fuzzy Search will parse the database export. It'll also create sample files as references of how to use Fuzzy Search's more complex functionality. Once Fuzzy Search is done with this process (it'll take several minutes!), browse the Tags Out folder for the sample analysis results!

> [!WARNING]
> Fuzzy Search running slowly?
> 
> Don't worry, it happens on everyone's first time...
> - Fuzzy Search pre-generates a cache to *vastly* speed up processing. This cache can take 10+ minutes to generate on your **first** run. Please give it time to finish!

## Documentation
The following documents go into greater detail on the various aspects of Fuzzy Search:

[Examples](docs/Examples.md) - Several use cases for Fuzzy Search
- Lots of images!

---
[Input](docs/Input.md) - How to use and customize Fuzzy Search
- Searches
- Command Line Arguments
- Downloading Posts
- Settings
	- Custom Categories
	- Bar Charts
	- Blacklist

---
[Output](docs/Output.md) - How to read Fuzzy Search's various analyses
- Text
	- Post Data
	- Post Data (URLs)
	- Tag Counts
	- Recommended Tags
- Charts
	- Bar Charts
	- Percentile
	- Scatter Plots
		- Post Score
		- Custom Category Relevance
- [Obsidian](https://obsidian.md/) Graphs

---
[Design](docs/Design.md) - A read on how Fuzzy Search operates
- Why does Fuzzy Search use so much RAM (for large searches)
- How Fuzzy Search ranks recommended tags

---
[Porting](docs/Porting.md) - A read on the potential of porting some of Fuzzy Search's features to E6
- Tag Recommendations ("Tags similar to what you searched")
- ~Tag Sorting (`order:~`)

---
[Architecture](docs/Architecture.md) - A read on the technical details of Fuzzy Search
- Inverted Index Cache
- Recommendation Algorithm: Finding Unique Tags
	- Sparse Implementation
	- Dense Implementation

---
[Fuzzy Search](https://github.com/alsaryn/fuzzy-search)
