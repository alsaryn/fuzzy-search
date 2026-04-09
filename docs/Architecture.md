## Architecture Overview

This page goes into the big-picture technical details behind what enables Fuzzy Search to get results relatively quickly. In particular, it covers the two most critical components of Fuzzy Search's recommendation algorithm:
1. The Cache: Converting E6's tag database into an Inverted Index
2. Recommendation Algorithm: Two Approaches to Finding Unique Tags In a Set of Posts

> [!WARNING]
> Stats for  nerds  ahead :)

### Glossary
Let:
- P = number of posts in the database
- T = number of (unique) tags in the database
- P<sub>q</sub> = number of posts matching search
- T<sub>q</sub> = number of (unique) tags matching search

Searches are bounded by the size of the database:
- P<sub>q</sub>  <= P
- T<sub>q</sub>  <= T.
- In the worst case (a search matches the entire database), P<sub>q</sub>  == P and T<sub>q</sub>  == T.
- In practice, a search's posts and tags (P<sub>q</sub>, T<sub>q</sub>) will be several factors smaller than the database's posts and tags (P, T).
	- This is the case Fuzzy Search is optimized for; empirically meaning searches with < 10,000 posts.

### Cache/Database Design
Fuzzy Search has a lot of tools, but when it comes time to retrieve data from E6's database on the disk, there's two types of database accesses:
1. We have a post id, and we want to get the list of tags on that post.
2. We have a tag, and we want to get post ids of every post with that tag.

---

**The 1st type of data access is simple.**

Fuzzy Search elected to use Python's SQLite 3 library to re-format E6's database to work with Python, enabling speedy constant time O(1) access to any post we have the id for.

While reformatting the database, we:
- Prune all deleted posts (which is about 12% of posts)
- Within the remaining posts, we condensed and removed post info currently unused by Fuzzy Search

When we're accessing millions of posts, every little bit adds up!

---

**The 2nd type of data access is more tricky.**

E6's export doesn't come with a tag-to-post-ids download. So we have to make our own--hence the lengthy caching process.

Doing a O(P) scan of all the tags in all the posts is simply too lengthy a process to repeat for every search. So, we do this process once, and store the results in what's commonly called an Inverted Index. It's a data structure that maps each tag to posts with that tag. Once the cache is built, we've got O(1) access to go from a tag to the list of all post ids with that post--quite a bit better than O(P)!

SQL is used to implement and store this cache. A built-in Python dict, while offering a slightly faster version of O(1) access, would end up holding gigabytes of data in memory at once. Furthermore, most searches only access a few rows of the ~800,000 unique tags currently on E6. Even `--recommended`, the heaviest user of this cache, is only accessing a couple thousand rows for most searches. Thus, storing the map on disk and retrieving only the desired rows with a database query saves a significant amount of memory with minimal slowdown.

### Recommendation Algorithm: Sparse vs Dense Optimization
The recommendation algorithm needs a list of unique tags, based on all the tags in all the searched posts. Fuzzy Search chooses between two approaches to find the set of unique tags in a list of posts:

#### Dense Algorithm
Approach: scan each of the T tags in the database.

**Runtime Performance**: O(T)
- Search-independent
- This is the optimal approach for densely-connected datasets (where we'd need to rank most of the tags anyways).

#### Sparse Algorithm
Approach: scan each tag of each post in the search to form a set of unique tags.

**Runtime Performance**: O(P<sub>q</sub>T<sub>q</sub>)
- Search-dependent
	- Heavily influenced by sparseness/density of searched posts
- At the cost of some overhead, this algorithm can calculate similarity for T<sub>q</sub> rather than T tags--skipping calculating similarity for any tag that would have a rank of 0. This takes advantage of the observation that, for most searches, T<sub>q</sub> <<< T.
	- As an example, the decently large search (29,000 posts) of `loona_(helluva_boss)` contains 30,000 unique tags. That is about 1/30th of the 800,000 unique tags stored across E6.

#### Which is better: Dense or Sparse?
The performance of the sparse version of the algorithm greatly depends on the search, whereas the dense algorithm runs at a large but constant time independent of searched posts size (the overall execution time change is from other sources). Empirical usage of the sparse algorithm has O(log(P<sub>q</sub>)) performance, but can be as low as O(1) for very sparse networks and as high as ⚠️ O(PT) ⚠️ for very dense networks!

![Chart of performance of dense vs sparse algorithm.](/images/fs/chart_finding_tags.png)

Looking at the above chart, it's pretty easy to guess when one algorithm outpaces another. To find out the threshold (number of posts in the search) where one algorithm becomes better than the other, we use an approach as stated below:
1. Make a test suite of searches with 10 posts, 100 posts, 1000 posts, etc...
2. Run the searches through only the sparse algorithm, noting the times for each search. Then do the same for dense algorithm.
3. The sparse algorithm should perform better on small searches, but eventually the dense algorithm will start to perform better as searches get larger. Figure out the number of posts where both algorithms have the same performance--this will be the threshold.
4. Within Fuzzy Search's code, compare the number of posts in the search to the empirical threshold and choose the appropriate algorithm:

```python
# Threshold of 10000 found through empirical testing
if len(searched_posts) < 10000:
	reccomended_tags = list_similar_tags_sparse(...)
else:
	reccomended_tags = list_similar_tags_dense(...)
```

---
Both Approaches Have Their Place!

The E6 database is dominated by densely-connected tags that involve millions of posts (e.g. `anthro`).

However, most (but not all) searches involve relatively niche, sparsely-connected tags. For example, the vast majority of the ~230k artist tags each involve less than 800 posts. This means over a quarter of the 800,000 unique tags on E6 involve less than 0.1% of the database's posts.

As such, it's worth the overhead to pre-process a search and determine if the sparse or dense recommendation algorithm is appropriate.

---
[Fuzzy Search](https://github.com/alsaryn/fuzzy-search)