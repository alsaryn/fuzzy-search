## Example Uses of Fuzzy Search

The core tool and name sake of Fuzzy Search is the `--recommended` tool. All it does is print out a list of tags deemed similar to your original search. Half the examples on this page are different ways to interpret that particular list of tags.

Many of Fuzzy Search's other tools supplement `--recommended` to ultimately help users go from "my favorite tag that I've searched to exhaustion" to "a bunch of artists/tags/posts similar to my favorite tag."

---
### Example 1: Finding tags similar to your search
> **Q**: "How can I find more tags like `this_really_cool_tag`?"
>
> **A**: Fuzzy Search's `--recommended` tool makes it easy to find other tags that are highly related to your favorite tags!

**Searched Tags:**  `domestic_cat slit_pupils`

**Arguments:** `--recommended`

**Time to Process:** 15.49 seconds

**Results:**
- **E6 (left):** A little catty
- **Fuzzy Search (right):** Much more catty

![Fuzzy Search's list of recommended tags for a cat-related search.](/images/fs/cat_recc.png)

---
Here's a second example:

**Searched Tags:**  `propane_tank`

**Arguments:** `--recommended`

**Time to Process:** 5.93 seconds

**Results:**
- **E6 (left):** "Alright champ, let's get you back into the furry section."
- **Fuzzy Search (right):** *actually has propane*

![uzzy Search's list of recommended tags for a propane-related search.](/images/fs/prop_comb.png)

**Perks of Fuzzy Search's tag output:**
**Highly relevant to what you searched for:**
- E6's list of tags is consistently dominated by the same few tags (e.g. `fur anthro clothing female male hi_res`), regardless of what you put in the search bar.
- Fuzzy Search's list of tags are *closely* related to what you searched for.
	- Curious what is meant by "closely related"? Consider reading the [Design](Design.md) write-up for a description of how Fuzzy Search's rather simplistic recommendation algorithm works!

**Tags split by category:**
- Makes it easy to find tags of a particular category (such as characters or artists).

**More than 25 tags:**
- Fuzzy Search outputs all tags (compared to the 25 total E6 gives), so you can browse as many tags as you want.

**Considers ALL posts in a search:**
- For performance reasons, E6 only lists tags relevant to the current page of posts--this is usually 75-300 posts.
- Meanwhile, Fuzzy Search can process millions of posts at a time!

---
### Example 2: What's the distribution of genders in `tag`?
>**Q**: "I'm interested in yoked-up characters, but it depends on the gender..."
>
> **A**: "Sounds like you're interested in these yoked-up `--bar` charts!"

Fuzzy Search's customizable `--bar` charts visualize the ratio of posts in your search that contain various tags.

**Searched Tags:**  `athletic`

**Arguments:** `--bar`

**Time to Process:** 13.26 seconds

`athletic` has a *somewhat* comparable representation of males and females:

![Bar chart showing ratio of genders for the athletic tag.](/images/fs/athletic_2.png)

---
**Searched Tags:**  `muscular`

**Arguments:** `--bar`

**Time to Process:** 78.86 seconds

As for `muscular`... you'll either love it or hate it:

![Bar chart showing ratio of genders for the muscular tag.](/images/fs/muscular_3.png)

---
Bar charts also have syntax for a single bar corresponding to multiple tags (`solo female`) and negated tags (`duo -male`).

**Searched Tags:**  `athletic`

**Arguments:** `--bar`

**Time to Process:** 13.26 seconds

![Bar chart showing ratio of group composition for the uwu tag.](/images/fs/bar_chart_group.png)

To get the same data on E6, each one of these bars represents a unique search. Meanwhile, Fuzzy Search needs only a single command and even visualizes all those numbers with a bar chart!

---
### Example 3: How has the score/posting rate of `tag` changed over time?
> **Q**: "When did 3D animation pop off?"
>
> **A**: "Goodness gracious, look at the score popping off on these `--score` charts!"

`--score` visualizes the score and upload date trends of any tag.

**Searched Tags:** `3d_animation`

**Arguments:** `--score`

**Time to Process:** 7.96 seconds

Score go up, just like the polygon counts:

![Chart of the scores over time for posts with 3D animation.](/images/fs/score_plot_3d.png)

---
**Searched Tags:** `loona_(helluva_boss)`

**Arguments:** `--score`

**Time to Process:** 1.53 seconds

Unlike her character, Loona's score has been pretty stable:

![Chart of the scores over time for posts with Loona.](/images/fs/score_plot_loona.png)

---
**Searched Tags:** `fur`

**Arguments:** `--score`

**Time to Process:** 228.92 seconds

This chart represents about a third of all posts on E6, as of April 2026:

![A plot of 2 million posts on E6.](/images/fs/scatter_score_2mil.png)

*It seems like post scores have been inflated over time! For more information, look up "E6 inf--*

---
### Example 4: What were the most popular characters in `year`?
>**Q**: "What were the most popular characters in 2025?"
>
>**A**: "Fuzzy Search can help you get those `--counts`!"

Fuzzy Search comes with basic filters, including upload date ranges. `--counts` returns all the tags in a search, ordered by the number of searched posts with that tag.

**Searched Tags:** `_all_posts_`

**Arguments:** `--counts --start_date "2025-01-01" --end_date "2025-12-31" --max_posts 6000000`

**Time to Process:** 139.5 seconds

```text
### Character
15952 fan_character
5797 loona_(helluva_boss)
4817 rouge_the_bat
3980 sonic_the_hedgehog
3887 amy_rose
3772 hornet_(hollow_knight)
3574 toriel
3233 judy_hopps
2632 miles_prower
2214 twilight_sparkle_(mlp)
2184 krystal_(star_fox)
2115 isabelle_(animal_crossing)
2066 susie_(deltarune)
2062 scp-1471-a
2060 blaze_the_cat
2005 ralsei
1886 nick_wilde
1851 kris_dreemurr
1847 ankha_(animal_crossing)
```

---
To get the most common character tags from all *safe-rated* posts in 2025, add the `--rating` argument:

**Searched Tags:** `_all_posts_`

**Arguments:** `--counts --start_date "2025-01-01" --end_date "2025-12-31 --max_posts 6000000 --rating "s"`

**Time to Process:** 110.31 seconds

```text
### Character
3481 fan_character
1267 sonic_the_hedgehog
901 hornet_(hollow_knight)
828 kris_dreemurr
754 loona_(helluva_boss)
753 susie_(deltarune)
727 twilight_sparkle_(mlp)
698 noelle_holiday
664 the_knight_(hollow_knight)
594 amy_rose
587 judy_hopps
585 rouge_the_bat
572 ralsei
501 shadow_the_hedgehog
```

Note: `_all_posts_`
- This is a special tag that includes all posts. You can combine it with other tags, such as `_all_posts_ -my_little_pony`.

Note: `max_posts 6000000`
- Fuzzy Search has a post limit that will yell at you if you give it massive searches (more than 200 thousand posts). This helps users avoid accidentally using more computational resources than expected. The checks for this limit are over-zealous, and currently don't factor in filtering posts by score or upload date. If you use these filters and predict that a large amount of the posts would be filtered out, you can safely increase the `max_posts` limit even if your computer has relatively low specs.

---
### Example 5: What artists have drawn the most of `my_favorite_character`?
>**Q**: "What artists have drawn the most of my favorite character?"
>
>**A**: "Take a look at the `--counts` of those artist tags!"

Wait a moment--you didn't say who your favorite character is! Eh, let me guess...

**Searched Tags:**  `loona_(helluva_boss)`

**Arguments:** `--counts`

**Time to Process:** 1.29 seconds

```text
### Artist
1405 conditional_dnp
357 artist_1
282 artist_2
213 artist_3
210 artist_4
199 artist_5
(...and 7,500 more artists...)
(Gee, loona really gets around!)
```

The number before each tag is the amount of searched posts with that tag. In this case, that's the number of posts the artists has with `loona_(helluva_boss)`.

---
If you want to find artists who have *specialized* in posts with Loona (meaning relatively few non-Loona posts), then `--recommended` can do that! Recommended will try to steer you to tags that
1. have lots of posts with what you searched, and
2. have few posts outside of your search.

**Searched Tags:**  `loona_(helluva_boss)`

**Arguments:** `--recommended --rec_tag_threshold 0`

**Time to Process:** 14.12 seconds

```
### artist
#set|#db    %set| tag
 357|417       1| artist_1
 163|165       0| artist_2
 149|185       0| artist_3
 199|278       0| artist_4
  61|67        0| artist_5
  40|45        0| artist_6
  23|24        0| artist_7
 213|386       0| artist_8
```
The recommended tags output always gives you the raw data it used to make its decisions. So even if you don't care for the ranked order of tags, you can use the parsed data to help get a sense for each tag. In the below example:
- `#set`: Count of posts in the search tagged with the artist.
- `#db`: Count of posts in the database tagged with the artist.
- `%set`: Percentage of posts in the search tagged with the artist.

**What's `rec_tag_threshold 0` doing?**

This threshold hides any tag that is only present in less than the specified percent of the searched posts.
- This is helpful for categories such as general, species, and copyright. Without it, the list of recommended tags would be filled with super specific tags. These tags often get a high ranking in Fuzzy Search because they happen to have all of their posts in whatever you searched for--which also means these tags are redundant because all their posts showed up in your original search. So, it's usually convenient to hide such tags by applying this threshold.
- However, this same threshold ends up being a little too aggressive to tags that simply aren't as populated--like most artist and character tags--and hides them.

Because we want to find similar artist tags, we set the threshold to 0, effectively disabling it. This ensures that all artist tags are listed in the output of `--recommended`.

---
### Example 6: What general tags does this `artist` specialize in?
> **Q**: "I have a list of artists, and I want to figure out what their niche is." 
>
> **A**: "Fuzzy Search is all about helping you discover `--recommended` niches!"

There's two aspects that turn any old tag into a relevant, highly-recommended niche:
1. That tag is used on many of the posts that came up in your search.
2. That same tag is rarely used on posts outside of your search.

`--recommended` weighs both of these properties to display the most relevant tagging niche that artist occupies.

**Searched Tags:** `sound_warning`

**Arguments:** `--recommended`

**Time to Process:** 15.66 seconds

As may be expected, the "artist" with sound and video has a niche in tags relating to music and camera movement.

```text
### general
#set|#db    %set| tag
 590|1057      3| synced_to_music
3767|12189    19| music
1431|4547      7| consistent_pov
 396|1144      2| music_video
3119|14109    15| multiple_angles
 998|5131      5| anthro_pov
 747|6393      3| blinking
1410|22259     7| faceless_human
 584|9114      2| faceless_anthro
```

---
**Recommended != Popular/Common**

Tags such as `anthro`, while taking up a whopping 73% of `sound_warning` posts, aren't even close to the top of the tags listed by Fuzzy Search. Why?
This is because Fuzzy Search's `--recommended` is aimed at exploring what's *unique* to that search--and thus less likely to occur with any other search.
- **Why the distinction matters**: if you want to find more stuff like `sound_warning` then what tag seems more reasonable to search for next: `synced_to_music` or `anthro`?

---
If you want a list of the most popular/common tags for that artist, use the `--counts` argument. This is going to be very similar to what you see on E6's tag sidebar.

**Searched Tags:** `sound_warning`

**Arguments:** `--counts`

**Time to Process:** 1.03 seconds

```text
### General
40898 anthro
39608 male
33404 female
33269 duo
18329 fur
16811 clothing
16382 tail
16032 hair
15696 solo
8893 clothed
8567 smile
8258 looking_at_viewer
```

---
### Example 7: What other artists are similar to `artist`?
> **Q**: "I used Fuzzy Search hoping to find other artists similar to my favorite artist. However, no other artist tags are listed with `-recommended`!"
> 
> **A**: "Fuzzy Search can find similar artists, but you'll need to use two consecutive `--recommended` searches to go from artist-to-artist."

**Why isn't Fuzzy Search *immediately* showing artist tags in the list of recommended tags:**

Fuzzy Search considers *only* the posts that came up in your search. This helps keep the recommended tags, y'know, *relevant* to what you searched.

When you search for an artist tag, you'll typically get 100% of the posts from that artist and zero posts from other artists:

```text
### artist
#set|#db    %set| tag
343|343   100| example_artist
... and no other artists D:
```

**Solution:** We need to give Fuzzy Search something to search that includes posts with other artists, yet with similar content to the original artist's posts.
- "Similar content", eh? Sounds like a job for `--recommended` tags!

---
**The First Search:**
Begin by feeding in your artist as a search:

**Searched Tags:** `sound_warning`

**Arguments:** `--recommended`

**Time to Process:** 15.66 seconds

```text
### general
#set|#db    %set| tag
 590|1057      3| synced_to_music
3767|12189    19| music
1431|4547      7| consistent_pov
 396|1144      2| music_video
3119|14109    15| multiple_angles
 998|5131      5| anthro_pov
 747|6393      3| blinking
1410|22259     7| faceless_human
 584|9114      2| faceless_anthro
```

Look at that glorious list of highly-relevant tags! Take your favorite ones and string them together with the `~` operator as a second search!

---
**The Second Search**

**Searched Tags:** `~synced_to_music ~music ~consistent_pov ~music_video`

**Arguments:** `--recommended --rec_tag_threshold 0`

**Time to Process:** 14.61 seconds

This example generated a list of 4,700 artists, with 19,000 posts between them. *Quite a lot!*
- The `--recommended` tags are ranked by relevancy to the tags you're searched, so you can start at the top of your list and work your way down.

**What's `rec_tag_threshold 0` doing, and why wasn't it used in the arguments of the first search?**

This threshold hides any tag that is only present in less than the specified percent of the searched posts.
- This is helpful for categories such as general, species, and copyright. Without it, the list of recommended tags would be filled with super specific tags. They often get a high ranking in Fuzzy Search because they happen to have all of their posts in whatever you searched for--which also means these tags are redundant because all their posts showed up in your original search. So, it's usually convenient to hide such tags by applying this threshold.
- However, this same threshold ends up being a little too aggressive to tags that simply aren't as populated--like most artist and character tags--and hides them.

Because we want to find similar artist tags, we set the threshold to 0, effectively disabling it. This ensures that all artist tags are listed in the output of `--recommended`.

---
### Example 8: Sort posts by number of ~tags
> **Q**: "I want to search `~fluffy ~uwu ~heart_gesture` and find the posts with ***MAXIMUM CUTENESS!***"
> 
> **A**: "Here's how to `--order` posts from most ~tags to least ~tags!"

**Searched Tags:** `~fluffy ~uwu ~heart_gesture`

**Arguments:** `--order "~"`

Posts will be ordered from most ~tags to least ~tags. For posts with the same number of ~tags, their relative order is arbitrary.

---
**Hiding the least relevant posts:**

~tags tend to lead to balloon the amount of posts in a search, which can be tiresome to trawl through. Use a command such as `--order "~" --top 20.0` to keep the first 20% of posts (the posts with the most ~tags) while hiding the remaining 80% of posts (the posts with the least ~tags).

---
Let's use `--order "~"` with `--recommended` to find tags similar to those we used in our search!

**Searched Tags:** `~fluffy ~uwu ~heart_gesture`

**Arguments:** `--order "~" --top 20.0 --recommended`

**Time to Process:** 22.96 seconds

```
### general
#set|#db    %set| tag
2420|6108      6| fluffy_chest
36594|182994   98| fluffy
25749|129413   69| fluffy_tail
1705|6571      4| fluffy_hair
 916|4230      2| fuzzy
1400|9132      3| fluffy_ears
1262|10294     3| white_sclera
4981|74662    13| neck_tuft
2400|37123     6| big_tail
6084|108768   16| cheek_tuft
6302|116278   16| facial_tuft
```

*Hmm... something's not quite right.*

Even though we searched for three different tags, it seems all the results are only looking at `fluffy`.

The reason? Take a look at this `--bar` chart:

![Bar chart showing ratio of fluffy, uwu, and heart gesture tags in a search.](/images/fs/bar_cuteness.png)

`fluffy` contains 200,000 posts, compared to the couple thousand of `uwu` and `heart_gesture`. Even using `--top 20.0`  to only keep the top 20% of posts means we still have 40,000 posts. Basic probability says most of those 40,000 posts will contain only one tag that we searched for: `fluffy` (and not `uwu` or `heart_gesture`). The solution is to narrow our search to just the very top of of this list (just the posts with 2 or 3 ~tags, meaning the post must have at least one of `uwu` or `heart_gesture`).

**Searched Tags:** `~fluffy ~uwu ~heart_gesture`

**Arguments:** `--order "~" --top 0.2 --recommended`

**Time to Process:** 11.01 seconds

```
### general
#set|#db    %set| tag
  76|843      20| uwu
 106|1804     28| heart_gesture
   8|617       2| toony_eyes
  11|1469      2| owo
  24|6108      6| fluffy_chest
 367|182994   99| fluffy
 244|129413   65| fluffy_tail
  19|6571      5| fluffy_hair
  21|9132      5| fluffy_ears
   9|2905      2| spiky_hair
   9|3011      2| pink_highlights
 119|91348    32| gesture
  76|74662    20| neck_tuft
  23|20706     6| :3
```

That's more like it! Plenty of tags related to fluffy and non-fluffy cuteness :3

---
### Example 9: Order (and download) posts ranked by relevancy to tags I like
>**Q**: "I want to find the posts with Loona that have the most gloriously-detailed backgrounds."
>
>**A**: "Since you're so interested in the detailed walls behind Loona, you're sure to enjoy this heckin' detailed wall of text!"

**Searched Tags:**  `loona_(helluva_boss)`

**Arguments:** `--order "Detailed Background" --top 20.0 --url_only `

**Time to Process:** 1.18 seconds

This command first finds all the posts with `loona_(helluva_boss)` and sorts each post by the amount of background-related tags. It then grabs the top 20% of sorted posts (meaning the ones with the most background-related tags) and generates a file of URLs. This file (except below) is ready to be processed Fuzzy Search's `postdownloader.py`.

```text
107432.png   https://static1(...)68a28f.png  0.8
607088.png   https://static1(...)f7137b.png  2.2
1091820.webm https://static1(...)5dd36a.webm 11.2
(and a bunch more posts)
````

---
**How does sorting by "Detailed Background" work?**

Most post sorting functions on Fuzzy Search use an object called a custom category... which is just a text file. For an example of one, Fuzzy Search comes with a "Detailed Background" custom category. It has color on the first line (which is used for data visualization purposes), followed by a list of tags:

```text
tab:blue
detailed_background
day
sky
outside
forest
grass
tree
cloud
night
plant
water
flower
book
moon
window
```

When we give Fuzzy Search the `--order "Detailed Background"` argument, we're telling Fuzzy Search to order posts by the amount of tags listed in that custom category.

The filename (minus the .txt part) is used as the name you give in the argument. To make your own custom category, copy this file and fill it with tags related to whatever you're interested in (perhaps use `--recommended` to find similar tags *wink-wink nudge-nudge*).

See [Input](Input.md) for more detail on how custom categories work.

---
**Why don't you add `detailed_background` to filter the posts?** 

Searching for `loona_(helluva_boss) detailed_background` does indeed filter the pool from from 30,000 to a more manageable 1,000 posts. We've skipped making a custom category, but there are some issues with this approach.

 **Issue 1: Under-tagging**
 
Example: Someone might tag a post with `day outside grass` but forget to tag `detailed_background`.

Despite having other background-related tags (and thus image content that qualifies as a detailed background), this post would be excluded with a search for `loona_(helluva_boss) detailed_background`. This type of issue is a symptom of under-tagging. Given that E6 is a volunteer-run site with millions of posts, under-tagging is pretty common. This issue is especially noticeable on smaller/niche tags (there's no way `uwu` is only present on 1,000 posts), which is the type of content/tags Fuzzy Search was designed to help discover.

Thanks to Fuzzy Search's ability to process large amounts of posts at once and sort posts by custom categories, issues like under-tagging can be somewhat mitigated. In the above example, even though a tagger missed one particular background tag, they were still tagged several other background-related tags. Fussing about if a post has an *exact combination* of tags is how we miss out on hidden gems! Custom categories consider the *cumulative weight* of those background-related tags.

**Issue 2: Pruning Posts by Relevancy**

Lets say you want to prune that list of 1,000 posts a little more. You recognize that `night` and `day` are common tags related to the background, but you aren't sure how to filter your search with them.
- Adding `night` will filter out most posts with `day`, even though both of these tags are relevant to the background
- Adding `~night ~day`  excludes indoors scenes.
- Adding `night ~day ~indoors` and other ~tags ultimately leads right back to the original list of 1,000 posts.
	- If you're doing this on E6, you're boned.
	- If you're doing this on Fuzzy Search, you can at least order posts by number of ~tags (`--order "~"`)... which is actually a custom category under the hood. So you may as well bite the pillow and make a proper "Detailed Background" custom category filled with the ~tags you used.

---
### Example 10: How many posts should I download with `--top`?
> **Q**: "I set up a custom category in Fuzzy Search and sorted a bunch of posts (using `--order`) , but I can't decide how many of those posts to download!"
> 
> **A**: "Download as many post as you have the time to appreciate! If you're still unsure, you may also appreciate these charts :)"

**Searched Tags:**  `loona_(helluva_boss)`

**Arguments:** `--charts_custom`

**Time to Process:** 3.37 seconds

If you're unfamiliar with reading percentile charts, they visualize what percentage of posts have some attribute (in this example it's the number of tags in the "Detailed Background" custom category).

Here's a terse interpretation of Loona's posts, according to the below chart:
- 5% yes detail
- 15% maybe detail
- 80% no detail

![Chart depicting percentile of Loona posts with detailed background elements.](/images/fs/percentile_annotated.png)

If you want to get the most relevant posts in a search, use `--top` to gather the posts before the curve dives down a cliff. Based on the above chart, use `--top 5.0` to download the top 5% of posts that are jam-packed with background-related tags.

**Relevancy:** This value is based on the number of times a post contains a tag related to a given custom category. The exact value depends on how you set up the custom category and what it's trying to measure. But the logic of bigger number = better usually holds.

---
Here's another percentile chart with a smoother curve. In this case there's no obvious cliff and the average relevancy is quite high. Based on that, you may elect to simply download all the posts in this search.

![Chart depicting percentile of Loona posts with detailed background elements.](/images/fs/percentile_alt.png)

---
### Example 11: A 3-strikes blacklist
>**Q**: "E6's blacklist hides too many posts, and keeping track of all the different logic/operators is complicated! There are tags that I *generally dislike* but that aren't that big a deal on their own."
>
>**A**: "It's `current_year` and high time for... the non-binary blacklist!"

**E6's Blacklist**

Those familiar with E6 will understand the blacklist as a "1-strike" policy: if a post contains ANY single blacklisted tag, then the post is hidden. This logic is binary, as either the post is hidden, or it's visible.
- Fuzzy Search provides this in the form of `E6_Blacklist.txt` in the Settings folder (see [Input](Input.md) for more details).

**Fuzzy Search's Blacklist**

Fuzzy Search also offers an additional "soft" blacklist to further filter posts; think of it as a "3-strikes" policy, where a single blacklisted tag won't hide a post, but multiple blacklisted tags will result in that post being hidden.

Fuzzy Search's soft blacklist is really just a custom category with a special name--meaning you can use it like you would any other custom category. This let's us do things such as:
- Sort posts from least to most blacklisted tags: `--order "Blacklist"`
- Compare how "blacklist-heavy" one tag is compared to another: `--charts_custom`
- Provide an alternative to E6's grouped tags as a way to factor in context.
	- Example: `skull sketch` vs `skull realistic`
	- You may be fine viewing the former while wishing to hide posts with the latter. Blacklisting `skull` is going to exclude both the light-hearted posts with skulls, while not blacklisting `skull` is going to show you posts you'd rather not see.
		- While you can use grouped tags to catch this particular case on E6, it quickly becomes a headache to repeat grouped tags for for `bones`, `skeleton`, etc. Then you have to set up grouped tags again for all the different art styles, humorous versus serious contexts, and so on.
		- In Fuzzy Search, you can specify a tag (and optionally a weight), and the custom category logic will apply to all cases of that tag.

To use the soft blacklist, use the argument `--blacklist <threshold>`. Think of the threshold as the number of strikes a post needs before it is hidden. A 3-strikes policy is set by `--blacklist 3.0`.

Here's an example Blacklist custom category, using weights to distinguish context:

```
skull
bones
skeleton
sketch -1.0
humor -1.0
halloween -1.0
```

The default weight is 1.0, so the below custom category is identical:

```
skull 1.0
bones 1.0
skeleton 1.0
sketch -1.0
humor -1.0
halloween -1.0
```

With this custom category, a post with `skull realistic` will end up with a total weight of 1, and thus be hidden by `--blacklist 1.0`. Meanwhile, a post with `skull skeleton humor halloween` has it's weights add up to 0 , so it remains visible in the searched posts.

---
### Example 12: How can I compare two artists?
> **Q**: "I have two or more artists I'm interested in, but only have the time to download and sift through the posts of one of them. Which artist should I look at first?"
> 
> **A**: "To help inform your decision, run Fuzzy Search with `-all` and skim whatever outputs catch your eye."

---
**Score and Upload Trends**

If you prefer artists who have high post scores or have uploaded recently, you can visualize that with `--score`:

![Chart comparing score and upload trends for two artists.](/images/fs/compare_score.png)

---
**Individual Custom Categories**

Rather than immediately hiding high-relevancy blacklist posts (`--blacklist`), we generate the below charts with `--charts_custom`. This works because the soft blacklist is just a custom category with a special name.

![Chart comparing blacklist percentiles for two artists.](/images/fs/compare_one.png)

**Reading the chart legend:**
"Blacklist 0.59 (397)" states the custom category name, the average custom category relevancy per post, and total relevancy across all posts.

**Interpreting the percentile curves:**

- 20% of Artist A's posts have some relevancy to the blacklist.
- 40% of Artist's B's posts have some relevancy to the blacklist.

Overall, Artist A has the lower blacklist relevancy.

---
**Grouped Custom Categories**

Looking at the legend of the custom categories score scatter plot (below), we can see that Artist B has a higher "Really Cool Stuff" relevancy--alongside a higher "Blacklist" relevancy. That poses a conundrum, as we'd like to maximize "Really Cool Stuff" and minimize "Blacklist."

![Chart comparing custom category scores for two artists.](/images/fs/compare_all.png)

---
Here's some other tools Fuzzy Search provides:
- `--recommended`
	- Compare what niche each artist occupies
- `--blacklist`
	- Hide high-relevancy blacklist posts.
- `--order "Really Cool Stuff" --top 20.0`
	- Only look at the top 20% of posts, sorted by relevancy to "Really Cool Stuff" (most useful when generating URLs for posts to download).
	- Can be combined with `--blacklist`!

If you're ready to download posts, use `--url_only` to generate URLs to download. Make sure to add any desired `--blacklist/order/top` arguments at the same time you generate the URLs!

---
### Example 13: Interactive Graphs: Obsidian
> **Q**: "Fuzzy Search doesn't come with enough charts, I need more!"
> 
> **A**: "For a text editor, [Obsidian](https://obsidian.md/) makes rather neat interactive graphs! Nice for the more visually inclined folks :3"

**Searched Tags:**  `loona_(helluva_boss) fluffy heart_symbol`

**Arguments:** `--graph 500`

**Time to Process:** 0.07 seconds

**Note:** `--graph 500`
- This tells Fuzzy Search to generate graphs for searches with 500 or less posts. For performance reasons, try to limit Obsidian graphs to searches with no more than 1,000 posts. See the [Input](Input.md) page for how to set up an Obsidian Vault from Fuzzy Search's output.

---
Obsidian's graph view can help visualize the "sweet spot" for tags (green dots) to further analyze:
- **Too General:** Basically every post has these tags (e.g. `fur anthro male female clothing`)--they don't help filter down the results or move you towards a neat niche.
- **Niche:** An ideal amount of posts have these tags--enough data to study, but not so general as to apply to the entire set.
- **Too Specific:** Only a couple of posts have these tags; probably not enough data to be worth looking into.

![Obsidian's graph view, visualizing a map of posts and shared tags.](/images/fs/obsidian_post_annotated.png)

**Visualize Related Areas**

Looking at the lower right corner of the above image, you'll note that a lot of those green dots are associated with a single post. This is a pretty clear example of how Obsidian will try to move related tags/posts nearby each other. Hence why common tags like `anthro` are found in that center green blob (close to lots of posts), and the tags used only in 1-2 posts are found in a ring around the graph (close to very few posts).

Here's a visualization of a tag (`fluffy`, the purple dot) being used as a tag in several posts (bright white dots). So if you want to find tags or posts similar to `fluffy`, try poking the dots around it.

![Obsidian's graph view, showing a tag linked to several posts.](/images/fs/obsidian_tag.png)

---
[Fuzzy Search](https://github.com/alsaryn/fuzzy-search)