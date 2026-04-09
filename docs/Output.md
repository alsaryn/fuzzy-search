# Overview of Output

Fuzzy Search has a variety of analyses it can perform, generating the following output:
- Text
	- Post Data
	- Post Data (URLs)
	- Tag Counts
	- Similar/Recommended Tags
- Charts
	- Bar Charts
	- Percentile
	- Scatter Plots
		- Post Score
		- Custom Category Relevance
- Obsidian Graphs

## Text

**All Output Text Files Use Markdown Formatting**

Use `Ctrl-F` and search for "###" headings to rapidly page through sections!

To access richer markdown functionality (such as outlines and foldable headings), change the file extension from `.txt` to `.md` (`.txt` is the default because some files are large enough that they lag markdown processors).

### Post Data
**Argument:** `--posts`

Contains basic data about individual posts.
Use arguments to add:
- Description (`--description`)
- Duration (`--duration`)
- Source (`--source`)
- URL (for downloading the post) (`--url`)

File begins with a header describing statistics for all posts in the search.

Example header:

```text
#### Search Statistics:
Total Posts: 196
  (Blacklisted: 0)
Avg Score: 171.98 (119 median)
Avg Favs: 286.73 (187 median)
Avg Comments: 3.28 (1 median)
```

Each post is given it's own section, based on the sidebar when viewing an individual post on E6:
- Post ID
- Score, Favs, Comments, Rating (S, Q, or E)
- Upload Date (YYYY-MM-DD)
- Categories with individual tags

Example post:

```text
#### 3318870
37 62 C7 S
Posted: 2019-11-29
Artists
	unknown_artist
Copyright
	hellaverse
	helluva_boss
	mythology
Character
	loona_(helluva_boss)
Species
	canid
	canid_demon
	canine
	demon
	hellhound
	mammal
	mythological_canine
	mythological_creature
General
	anthro
	(...)
```

### Post URLs
**Argument:** `--url`

Use command line arguments to choose between the three available URL formats:
- `--url_mode md5`
- `--url_mode url`
- `--url_mode full`

#### md5
- Outputs the md5 hash
- Probably the most useful if using external downloaders

```text
(...)68a28f
(...)f7137b
(...)5dd36a
```

#### url
- Outputs the static URL with parsed md5 hash

```text
https://static1(...)68a28f.png
https://static1(...)f7137b.png
https://static1(...)5dd36a.webm
```
#### full
- Outputs the E6 post id and file type, the static URL, and filesize (MB)
- Tab-delimited
- Format used by Fuzzy Search's built-in downloader

```text
107432.png   https://static1(...)68a28f.png  0.8
607088.png   https://static1(...)f7137b.png  2.2
1091820.webm https://static1(...)5dd36a.webm 11.2
```

### Tag Counts By E6 Category
**Argument:** `--counts`

A simple count of how many posts in the search contain a given tag.
- Split by E6's categories:
	- Artist
	- Contributor
	- Copyright
	- Character
	- Species
	- General
	- Invalid
	- Meta
	- Lore

Example:

```text
### Character
196 loona_(helluva_boss)
26 octavia_(helluva_boss)
20 blitzo_(helluva_boss)
(...)

### General
196 detailed_background
194 female
192 anthro
(...)
```

### Tag Counts By Custom Category
**Argument:** `--counts_custom`

A simple count (or weight if applicable) of how many posts in the search contain a given tag.
- Split by user-defined custom categories in `Settings/Custom Categories`

File begins with a header describing statistics for all posts in the search, split by custom category:

Example header:

```text
### General Stats:
Total Posts: 196
Total Tags Per Category:
  Emotive: 254 (1.3 per post)
  Horror: 152 (0.78 per post)
  Detailed Background: 346 (1.77 per post)
```

Each category is given it's own section, breaking down the tags and counts/weights that contributed to that category's overall total for the searched posts:

Example category section:

```text
### Emotive
59 smile
48 holding_object
32 narrowed_eyes
25 dialogue
16 angry
16 looking_at_another
15 speech_bubble
11 comic
(...)
```

### Similar Tags
**Argument:** `--recommended`

A ranked list of all unique tags in the searched posts (split by E6 category), ordered chiefly by:
1. being common in the searched posts
2. being niche outside the searched posts

See the [recommendation algorithm design](docs/Design.md) for more details.

**Key:**
- **#set:** Count of posts in the search with this tag.
- **#db:** Count of posts in the database with this tag.
- **%set:** Percentage of posts in the search with this tag.

Example:

```text
### general
#set|#db    %set| tag
 121|32494    61| red_sclera
  18|4055      9| eyebrow_ring
  93|37640    47| spiked_collar
  75|40423    38| white_eyes
  45|21526    22| notched_ear
  38|20755    19| smartphone
 196|236419  100| detailed_background
  42|36991    21| cellphone
  72|72832    36| grey_hair
  22|16958    11| holding_phone
  97|122825   49| spikes
  50|58257    25| phone
(...)
(... plus 9758 other tags found in less than 2% of the searched posts)
```

#### Threshold Argument
The argument `--rec_tag_threshold` will hide tags that only occur in a small portion of the searched posts.

For example, applying `--rec_tag_threshold 40` to the above example will filter out any tags present in less than 40% of the searched posts, resulting in the below output:

```
### general
#set|#db    %set| tag
 121|32494    61| red_sclera
  93|37640    47| spiked_collar
 196|236419  100| detailed_background
  97|122825   49| spikes
(...)
(... plus 21766 other tags found in less than 40% of the searched posts)
```

## Charts

### Bar Chart
**Argument:** `--bar`

**Creation:** One chart per user-defined bar chart tag group in `Settings/Bar Charts`.

**Usage:** Helpful to compare the count of several tags at once (without needing to make additional searches).

Note: Bar charts contain syntax to have a bar correspond with multiple tags and/or to negate tags.

![Bar chart comparing ratios of various number of characters present.](/images/fs/bar_chart_group.png)

### Percentile
**Argument:** `--charts_custom`

**Creation:** One chart per user-defined custom category in `Settings/Custom Categories`.

**Usage:** Helpful to gauge what proportion of posts in a set are highly relevant in regards to some attribute.

**Legend:** Contains the average custom category relevancy per post (1.56 in below example) and total relevancy across all searched posts (7024 in below example).

![Percentile chart showing ratio of posts that are above a custom category relevancy.](/images/fs/percentile.png)

### Scatter Plot Post Score
**Argument:** `--score`

**Visualize:**
- Post frequency over time
- Post score over time
	- Negative scores are clamped to 0 for cleaner visuals

![Scatter plot plotting post upload date and post score.](/images/fs/scatter_score.png)

### Scatter Plot Custom Category Relevancy
**Argument:** `--charts_custom`

**Creation:** Each post gets a colored point based on the user-defined custom categories in `Settings/Custom Categories`.

**Visualize:**
- Post Frequency over time
- Custom Category Relevancy

**Legend:** Contains the average custom category relevancy per post and total across all searched posts.

Categories are ordered by relevancy.
- Lower-scoring categories are plotted last (i.e. on top of all other categories) in order to prevent them from being covered by the higher scoring categories.

![Scatter plot plotting post upload date and custom category relevancy.](/images/fs/scatter_custom.png)

## Obsidian Graphs
### Creating an Obsidian Vault from Fuzzy Search Output
**Argument:** `--graph <num>`

Open [Obsidian](https://obsidian.md/):
1. Manage Vaults -> Open new vault -> navigate to and select the `Obsidian` folder inside the search analyzed by Fuzzy Search
	- If you can't find the `Obsidian` folder, then make sure you ran Fuzzy search using `--graph <num>` with a number higher than the searched post count.
2. Open Graph View (on the left side command bar)
3. Enable Tags (under the Filters tab of the graph view settings)

**Tip:** Viewing Post Details
- When viewing posts linked to a tag node, hold the  `control` key when hovering over posts to view the post's details (such as their tags) without leaving the graph view. Enable the "Show more context" option so that simply hovering over posts shows these details.

### Uses of Obsidian Graphs
- See connections between tags
- Visualize overly-general tags as dense clusters
- Visualize overly-specific tags as dead-end leaf nodes
- Investigate posts of interest
	- Pull up the associated Post Data entry without needing to `Ctrl-F` a text file
- Utilize Obsidian's search filters

Here's a visualization of a tag (`fluffy`, the purple dot) being used as a tag in several posts (white dots):

![Obsidian's graph view, showing a tag linked to several posts.](/images/fs/obsidian_tag.png)

The graph view can also help visualize clusters of related tags. In this case, a post (`5509923`, the purple dot) is showing a link to each of it's tags (green dots).
- The large green dots in the center are tags shared by many posts: `fur anthro male female clothing` and so on.
- The small green dots at the edges of the cluster are only shared by a few posts, indicating they are very niche tags (relative to this search).

![Obsidian's graph view, visualizing a map of posts and shared tags.](/images/fs/obsidian_post.png)

---
[Fuzzy Search](https://github.com/alsaryn/fuzzy-search)