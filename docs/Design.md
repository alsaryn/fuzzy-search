## Design

This is a collection of write-ups on how Fuzzy Search operates under the hood.

### How Fuzzy Search Recommends Tags
This pertains to Fuzzy Search's `--recommended` tool, which returns a list of tags deemed relevant to what someone searched for.

There's 3 attributes of a tag which determine it's placement in the ranked list of tags output by Fuzzy Search:
1. Hits (shares a lot of posts with the search)
2. Distractors (omitting too general tags)
3. Threshold (omitting hyper-specific tags)
	- Threshold is an optional argument applied after ranking tags, so it's not covered in this section.

**Altogether, the recommendation algorithm favors mid-size tags** (10-10,000 posts) above common (10,000+ posts) tags or hyper-specific (1-9 posts) tags.
	Why favor mid-size tags? They're large enough to contain a decent amount posts to study, without being so large as to inevitably have posts unrelated to the original search.

**The Algorithm**
To begin, assemble a list of every unique tag from all the posts that were associated with the search. We then calculate a rank for each tag, and finally sort each tag by that rank before displaying the results.

For reference, here are some common terms:
	P<sub>q</sub>: The set of posts matching the search
	P<sub>t</sub>: The set of posts containing the tag being ranked

For each unique tag, their rank is simply two components multiplied together. Here's the relevant Python code:
```python
post_ids = # P_q; the posts in the search
posts = # P_t; the posts with the tag to be ranked

# Get the number of posts shared between the search and ranked tag
inter_len = len(post_ids.intersection(posts))
# If there's no posts shared between the two sets, then the rank is 0
if inter_len > 0:
	hits = math.log10(inter_len)
	distractor_ratio = inter_len / len(posts)
	rank = hits * distractor_ratio

# Now sort each tag by their rank--higher ranks go to the top of the recommended tags list.
```

Both the hits and distractor components end up using the same variable in their calculations: the number of posts shared between the search and ranked tag (i.e. the cardinality of a set intersection of P<sub>q</sub> and P<sub>t</sub>).

When the components are multiplied together, you can think of the resulting value as a how much the search's and tag's posts overlap, with that tag's rank reduced if there's a lot of off-topic (non-search related) posts in that tag.

**Component 1: Hits**
Hits gauges how many posts contain both the search and ranked tag. This is calculated from the number of posts shared between the search and ranked tag. Hits will be low if there's few shared posts, and high if there's lots of shared posts. The logarithm (base 10) is applied in order to plateau the value given to extremely common tags (e.e. `anthro`)--so having more shared posts still increases the tag's rank, just with diminishing returns.

**Component 2: Distractors**
Distractors gauges how many of a ranked tag's posts occur with the search. In the code, this is the number of posts that contain both the search and the ranked tag, divided by the total posts containing the ranked tag. Distractors will be high if almost all the tag's posts are shared with the search, and low if almost none of the posts are shared.

**Thoughts**
This recommendation algorithm is the result of trying to get TF-IDF (the only recommendation algorithm I was familiar with at the time) to work with binary tag data on E6. Hits and Distractors are somewhat similar to Term Frequency and Inverse Document Frequency (and the log and ratio even normalize those components), meanwhile Threshold has no matching feature on TF-IDF. Fuzzy Search's approach seemingly gets the job done, but it's most certainly not TF-IDF, nor does it resemble any other recommendation algorithm I've come across.

### Recommended Tag Threshold
This pertains to the `rec_tag_threshold` argument when running the `--recommended` tool.

**Goal:** The goal of this argument is to prune hyper-specific tags from the list of recommended tags. This is motivated by the observation that hyper-specific tags contain too few posts (often <10) to be worth studying compared to more populated tags.

**Approaches**
There's two approaches for what makes a tag hyper-specific:
1. The tag is used on a low amount of posts in the *database*
2. The tag is used on a low amount of posts in the *search*

For example, consider the below excerpt of `--recommended` tags generated from the search `propane_tank`:
```
#set|#db    %set| tag
  36|36      100| propane_tank
   6|8        16| propane
   2|21        5| welding_tool
   3|59        8| welding_torch
   5|653      13| grill
  29|4145965  80| anthro
```

**Approach 1**
If we remove tags based on being rare in in the database, we would remove tags in in order of the `#db` column:
```
#set|#db    %set| tag
  29|4145965  80| anthro
   5|653      13| grill
   3|59        8| welding_torch
  36|36      100| propane_tank
   2|21        5| welding_tool
   6|8        16| propane
```
*Oh hey, `anthro` is back on the top of rankings!*
This is practically a reverse order of what we want! Whenever our search is something niche--such as when we're trying to find tags similar to a tag that only has 30 posts--we'd end up removing the tag we used as the search almost immediately! In this `propane_tank` example, `propane_tank` would be removed within the first 15 of the 800 total general tags.
	Furthermore, the order in which we remove tags is based on what the database looks like, which is entirely unrelated to how much that tag resembled what we searched for.

**Approach 2**
If we instead remove tags based on being rare in the search, we would remove tags in in order of the `%set` column:
```
#set|#db    %set| tag
  36|36      100| propane_tank
  29|4145965  80| anthro
   6|8        16| propane
   5|653      13| grill
   2|21        5| welding_tool
   3|59        8| welding_torch
```
This is close to the order we want! This approach guarantees tags used in the search are removed last.

**Conclusion**
Approach 2 is used by Fuzzy Search.
- When hyper-specific tags are removed, they're removed based on closeness to the search--not the more arbitrary-feeling criteria of closeness to the entire database.
- Common tags such as `anthro` are unlikely to be removed by either approach, but other parts of the algorithm already devalue common tags.

### Why Does Fuzzy Search Use So Much Memory?
**Fuzzy Search is optimized for small searches (<10,000 posts)**
Fuzzy Search is optimized for simultaneously processing hundreds of small searches run with multiple modes of analysis.
Fuzzy Search is NOT optimized for a single, large search run with only one mode of analysis.

For ease of development and users being able to customize output, Fuzzy Search's data is object-oriented (rather than data-orientated) and output is assembled is several passes. The pass-based system of the output means that we need to fetch or reuse the object holding a post's data for each pass. Reusing an object held in memory is far faster than fetching the same from disk multiple times. For memory usage, this means that:
- Every post associated with the search will be loaded at once
- With multi-core processing, posts for multiple searches will be loaded at once

---
[Fuzzy Search](https://github.com/alsaryn/fuzzy-search)