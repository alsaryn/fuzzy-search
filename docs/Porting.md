## Porting

This page discusses the viability (or lack thereof) of adding some of Fuzzy Search's functionality to E6.

Note: I am not experienced with E6's internals nor is my background in web database systems. Nonetheless, while the development of Fuzzy Search is still fresh in my mind, I felt like giving my perspective.

### Porting Tag Recommendations to E6
> Q: Would it be possible to implement some version of Fuzzy Search's `--recommended` tags on E6?
> A: Almost certainly not.

#### **Issue 1: Accuracy**
To keep computation on the server side low, E6 can only serve a single page of posts at a time. Fuzzy Search's tag recommendations needs post data (specifically the tags) to run it's algorithm, so an E6 version would be limited to processing a single page of posts. That causes Fuzzy Search to base it's recommendations on a subset of the full set of posts, so now sampling errors can muck up the accuracy of the results. The distribution of tags within posts of a search introduces a new point of failure for the algorithm.

Niche (and unevenly distributed) tags may be absent from several pages of a search, while present in disproportionately high numbers on other pages. For example, `order:artist` would completely mess up the accuracy of recommended artist tags regarding to the search. Meanwhile, common (and uniformly distributed) tags such as `anthro` will be relatively unaffected by the sampling and so likely rise in visibility on most pages. Common tags being more visible and niche tags is the problem that Fuzzy Search was trying to address in the first place.

The good news is that recommendations are fuzzy in the first place, so some small discrepancies aren't a problem. But there is potential for large discrepancies/sampling issues, which could render Fuzzy Search-style recommended tags a monumentally inefficient method of outputting a list of common tags.

#### Issue 2: **Syncing the Cache:**
Fuzzy Search's approach relies on a cached map of tag to posts (specifically the post ids) with that tag. Syncing a cache across multiple servers sounds awful, but the nice thing is that small errors are totally fine--the recommendations are a heuristic in the first place. While sampling errors (discussed above) could have grievous results, I expect caches being out of date to be a negligible problem. Even updating the cache once a week should be fine; only hyper-specific tags (<10 posts total) are going to change much in the course of a week, and Fuzzy Search actively hides these if they weren't already buried in the rankings.

#### **Issue 3: Computational cost**
How much more computation would Fuzzy Search-style tags require?

**Smaller Searches, Less Time to Process, Less Accuracy:**
E6 only provides a single page of posts to process at a time. This brings the max searched posts down from millions to 300 posts. However, we now have to process these posts lightning fast on cheap servers linked by the internet, ideally without querying a internal database/cache too much or needing to send too much additional internet traffic over to clients.

**Finding Tags to Rank:**
People searching for `popular_tag order:score` is probably pretty common, so we'll use this as a representative example. A search for `3d_animation`, ordered by score (`--min_score 4500` on Fuzzy Search), has the first page hold 300 posts with around 150 tags per post (image below). Searching 300 posts with 150 tags each leads to 300 x 150 = 45k iterations of a loop. This returns 6,300 unique tags (`--counts` on Fuzzy Search) in the `3d_animation` search.
![Chart plotting the tag count and score for the highest-scoring 3D animation tags.](/images/fs/score_to_tag_count_3d.png)

To cut down the number of tags we need to consider, we apply the `--rec_tag_threshold` argument. Let's say any tag with 10% or less of the search's posts is hidden. A brief skim of the tag counts reveals that at least 60% of the unique tags could be immediately removed, leaving just 2,500 of the original 6,300 unique tags. That assumes we can find a quick way to deduce if a tag has a low post count in the searched tags. Perhaps keeping a tally while iterating the loop, or comparing set intersections of post ids when calculating ranks?

**Calculating and Sorting Ranks:**
To be ranked, each tag has to:
1. Query the tags_to_post-ids cache/database
	- We need post ids to ultimately figure out how much the posts with this tag "overlap" with the search's posts. This is different from a simple post count of the tag (which is the number E6 provides whenever it lists a tag in the sidebar).
2. Take the intersection of two sets of ints (post ids)
3. Apply a logarithm
4. Do some other elementary math
This is a distressingly parallel task, so loading it onto a GPU is an obvious fix for the individual rank calculations. That still leaves querying the database as an open issue.

Once we have all the tags and their respective rank (a float), we have to sort all the ranks. Continuing with the `3d_animation` example, that means sorting a list of 2,500 floats.
	To reduce processing demand, E6 could display only the top 25 or so of these 2,500 tags. Furthermore, the final list doesn't need to be 100% accurate. That means it may be possible to use a heuristic to guess what the 100 or so top-ranked tags might be, and only calculate and compare ranking for those 100 tags (rather than the 2,500 pruned unique tags) to get the final 25.

**Fuzzy Search's Computational Cost Compared to E6:**
I'm not aware of E6's internals (if the above guesswork didn't already make that obvious), so I'm going to continue to blindly throw out numbers of what I think it takes for E6 to currently serve a page of posts to a user.

In order to get (up to) 300 posts ordered by score:
- there's probably a handful of database accesses to find all the posts brought up by the search, order them by score, and get some other miscellaneous info.
- There's then 300 database accesses to get the post info for all 300 posts.

Altogether, E6 probably isn't using more than 400 accesses to the database to process any single page of search results. Meanwhile, Fuzzy Search's similar tags is looking at 2,500 additional accesses--one for each unique tag that is being ranked. Even a "small" example like the 36 posts of `propane_tank` has 400 (1,100 unique tags, 60% of which are pruned) additional database accesses. 

**It Won't Fit!**
In conclusion, adding Fuzzy Search-style similar tags to E6 search results adds too much load on the servers to be feasible. The computational cost is still too high even when being optimistic about the average search being small and heuristics/optimizations being found to solve individual steps of the process. These are the main obstacles that stick out to me:
1. Iterating over every tag in every searched post to find the unique tags
2. Applying `rec_tag_threshold` to reduce the set of unique tags
3. Additional database accesses to determine "tag-search overlap" via lists of post ids when ranking the tags
4. Sorting tags by numerical rank
Even if all these steps are solved, that doesn't resolve concerns about the diminished accuracy of recommended tags when applied to subsets (individual pages) of searched posts.

### Porting ~Tag Sorting to E6
> Q: Would there be a way to order posts from most ~tags to least ~tags? 
> A: Probably not, but it seems close.

**While E6 could most likely offer the ability to sort posts by ~tags per-page, it's inconsistent with the rest of the `order:` functions.**
The logic for the `--order ~` argument is relatively simple; it's a single scan of all tags of all posts (which is pretty quick with only 100 or so posts). Since the client already has all the posts + their tags for that single page, E6 can offload the sorting process entirely to the client's browser, leaving E6's servers unaffected.

However, as far as I'm aware, all of E6's `order:` sorts apply to all posts (regardless of how many posts there are related to the client's search). Introducing a per-page sort clashes with the rest of E6's design. For consistency, we'd only consider a `order:~` sort that applied to all posts in the search, not just a single page.

**Sorting posts in a search by ~tags is search-dependent, which makes sorting all posts in a search impractical.**
I'm not familiar with E6's backend, but I would guess a sort such as `order:score` is feasible because a server can calculate the sorted list once then just copy the relevant bit of the results when serving requests. This works because the score of a post is a value independent of what the client searched for.

Unfortunately, the same approach is not possible with sorting by ~tags. The number of ~tags a post has is dependent on the tags used in the search, so you'd never be able to re-use the results of one search to speed up another search.

**There may yet be hope!**
Unlike other sorts, a sort by ~tags is really just splitting tags into a couple big groups--the order within those groups is arbitrary.

For example, the search `~day ~night ~sky` has 3 subsets:
1. Posts with 3 total ~tags
	- `day night sky`
2. Posts with 2 total ~tags
	- `day night`
	- `day sky`
	- `night sky`
3. Posts with 1 total ~tag
	- `day`
	- `night`
	- `sky`
We don't care where posts are within a subset are ordered, only which posts are in which subset. Once we know the posts in subset, it'd be easy enough to page through those posts (and perhaps even sort posts in the subset, such as `order:score`).

Someone who enjoys set math could try to come up with a creative use of a tag to post-id map to figure out a constant-time O(1) function for this. If an O(1) sort seems impossibly quick to you, remember we're more sorting a couple of lists, not thousands of individual posts.
	This isn't really a post sorting function--the order of posts within a subset is irrelevant. We're retrieving a few big lists of post ids (one list for each ~tag), and figuring out how to union/intersect them such that each post id appears exactly once in the final, flattened list of results. The logic for this is probably similar to how Fuzzy Search (and perhaps E6) first figures out what posts are containing within a search, well before we actually start pulling up the tags found on any individual post.

If such an algorithm was discovered, it'd also have to handle these circumstances:
1. The search contained tags that weren't OR'd together (e.g. `forest -cloud ~day ~night ~sky)
2. Doesn't break other sorting methods used with the search

---
[Fuzzy Search](https://github.com/alsaryn/fuzzy-search)