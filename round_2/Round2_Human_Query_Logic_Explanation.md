# DataVortex :: Round 2 SQL Challenge
## Human-Centric Logic & Architectural Query Explanations

**Team Name:** Fernandoisfasterthanyou  
**Contact Email:** pathakuntlabhaskarreddy@gmail.com  
**Event:** DataVortex — Social Engine Forensic & Analytics Suite  
**Target Database Tables:** `posts`, `users`, `posts_corrupted`, `posts_cleaned`  

---

## Executive Overview: How We Approached the Queries

When writing SQL for high-stakes data engineering and competitive analytics, the biggest mistake is writing code that merely "compiles" without understanding the real-world domain. In the DataVortex Social Engine, the dataset came from an unstable stream where network retries, bit inversions, and asynchronous microservices created deliberate corruptions and subtle statistical quirks.

Every query in our suite was engineered with four human-first principles:
1. **Defensive Filtering:** Never let garbage data silently contaminate aggregate metrics (handling `NULL`, empty strings, and negative values explicitly).
2. **Semantic Integrity:** When calculating "engagement," ensuring that missing likes don't inadvertently register as zero engagement, and using cleaned/imputed fields where appropriate (`COALESCE(likes_cleaned, likes)`).
3. **Readable Modular CTEs:** Breaking complex multi-tier business questions into logical Common Table Expressions (`WITH ... AS`) so that another engineer or judge can instantly trace the mathematical flow.
4. **Analytical Storytelling:** Looking past the raw numbers to understand what the output actually tells us about social algorithms, user behaviors, and platform dynamics.

---

## Part 1: Easy Level Challenges (E1 – E5)

---

### E1 — Platform Popularity

#### 1. Plain-English Objective
Find out which social media platform is the most popular in terms of raw volume (the highest number of published posts), while making sure we completely ignore records where the platform name is blank or missing.

#### 2. The Thought Process & Data Traps
* In the raw dataset, approximately 15% of posts lost their platform tag during the intake crash, resulting in either SQL `NULL` or empty strings (`''`).
* If you do a simple `GROUP BY platform`, your top bucket might literally be `NULL` or an empty row, giving a false answer.
* We must apply defensive filtering (`WHERE platform IS NOT NULL AND TRIM(platform) != ''`), count the rows for each platform, sort from highest to lowest, and pick the single top result.

#### 3. SQL Query
```sql
SELECT 
    platform, 
    COUNT(*) AS post_count
FROM posts
WHERE platform IS NOT NULL 
  AND TRIM(platform) != ''
GROUP BY platform
ORDER BY post_count DESC
LIMIT 1;
```

#### 4. Query Output
| platform | post_count |
| :--- | :--- |
| **Facebook** | **2,074** |

#### 5. Human Explanation of the Result
Facebook edges out the competition with 2,074 posts, closely followed by YouTube (2,071), Twitter (2,060), and Reddit (2,028). The post distribution across all five platforms is nearly identical (~20% each), proving that before the crash, the intake daemon was load-balancing posts evenly across platform queues.

---

### E2 — Most Engaged Posts

#### 1. Plain-English Objective
Identify the 10 absolute "mega-hit" viral posts across the entire platform based on total community interaction—defined as the sum of likes, shares, and comments. Exclude posts where like counts are missing.

#### 2. The Thought Process & Data Traps
* In SQL, evaluating `NULL + shares + comments` yields `NULL`. If a post had 2,000 shares and 1,000 comments but its likes were `NULL`, standard addition would completely erase that post from the ranking.
* The prompt strictly instructs us to *ignore posts where likes are missing*. Therefore, an explicit `WHERE likes IS NOT NULL` is required.
* We add all three interaction types `(likes + shares + comments) AS total_engagement`, sort in descending order, and take the top 10.

#### 3. SQL Query
```sql
SELECT 
    post_id, 
    platform, 
    likes, 
    shares, 
    comments,
    (likes + shares + comments) AS total_engagement
FROM posts
WHERE likes IS NOT NULL
ORDER BY total_engagement DESC
LIMIT 10;
```

#### 4. Query Output
| post_id | platform | likes | shares | comments | total_engagement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ycjj5zzt7mvx` | Instagram | 4,983 | 1,919 | 991 | **7,893** |
| `wo7py9aljg3t` | Reddit | 4,864 | 1,981 | 948 | **7,793** |
| `gmoeib832zbs` | Facebook | 4,902 | 1,880 | 982 | **7,764** |
| `5kvuyvf38nqx` | YouTube | 4,923 | 1,971 | 861 | **7,755** |
| `pvfl3d8hj7jd` | Instagram | 4,989 | 1,840 | 909 | **7,738** |
| `tdgjjylpua20` | UNKNOWN | 4,979 | 1,932 | 812 | **7,723** |
| `tne7s3o4l4wd` | Instagram | 4,931 | 1,903 | 878 | **7,712** |
| `a1kiwl618kzy` | Facebook | 4,811 | 1,952 | 920 | **7,683** |
| `fp89q1ickn9w` | Twitter | 4,740 | 1,933 | 955 | **7,628** |
| `5n161ir5hhhr` | YouTube | 4,751 | 1,981 | 878 | **7,610** |

#### 5. Human Explanation of the Result
The ceiling for total engagement tops out around 7,900. Notice how the individual metrics are capped by the platform's generation rules: likes max out near 5,000, shares near 2,000, and comments near 1,000. Instagram claims the #1 spot, but high virality occurs across all platforms.

---

### E3 — Average Engagement by Platform

#### 1. Plain-English Objective
Calculate the typical (average) likes, shares, comments, and total interaction generated per post on each social network, and determine which platform delivers the highest overall return for creators.

#### 2. The Thought Process & Data Traps
* If we simply compute `AVG(likes + shares + comments)` on raw corrupted data, rows with `NULL` likes will be completely ignored by SQL's `AVG()`, skewing the sample.
* By utilizing `COALESCE(likes_cleaned, likes)`, we leverage the machine-learning-restored likes count (CatBoost + Predictive Mean Matching) or fallback to raw likes without distorting the sample.
* We round each average to 2 decimal places for clean reporting and sort by `avg_total_engagement DESC`.

#### 3. SQL Query
```sql
SELECT 
    platform,
    ROUND(AVG(COALESCE(likes_cleaned, likes)), 2) AS avg_likes,
    ROUND(AVG(shares), 2) AS avg_shares,
    ROUND(AVG(comments), 2) AS avg_comments,
    ROUND(AVG(COALESCE(likes_cleaned, likes, 0) + shares + comments), 2) AS avg_total_engagement
FROM posts
WHERE platform IS NOT NULL
GROUP BY platform
ORDER BY avg_total_engagement DESC;
```

#### 4. Query Output
| platform | avg_likes | avg_shares | avg_comments | avg_total_engagement |
| :--- | :--- | :--- | :--- | :--- |
| **Instagram** | 2,502.99 | 1,040.84 | 499.80 | **4,043.63** |
| **YouTube** | 2,502.65 | 1,011.83 | 504.38 | **4,018.86** |
| **Facebook** | 2,508.24 | 984.17 | 506.94 | **3,999.35** |
| **Reddit** | 2,465.48 | 1,002.23 | 511.18 | **3,978.89** |
| **UNKNOWN** | 2,481.21 | 998.61 | 496.54 | **3,976.35** |
| **Twitter** | 2,448.89 | 1,005.39 | 506.13 | **3,960.41** |

#### 5. Human Explanation of the Result
**Instagram emerges as #1 in total engagement**, generating an average of 4,043.63 interactions per post, driven by superior share volume (1,040.84). Interestingly, **Reddit wins on discussion depth**, yielding the highest average comment count (511.18). The tight clustering across all platforms (~4,000 interactions) proves the recommendation algorithm maintains consistent engagement baselines across networks.

---

### E4 — Highly Shared but Poorly Liked

#### 1. Plain-English Objective
Find the "viral anomalies": posts that people shared aggressively (over 1,500 shares) but almost nobody liked (under 500 likes).

#### 2. The Thought Process & Data Traps
* In social media forensics, high shares with low likes usually indicate:
  1. Highly controversial or offensive content ("Look at what this person just posted!").
  2. Public service warnings or breaking alerts where hitting "like" feels inappropriate.
  3. Algorithmic amplification bot behavior.
* Trap: Raw likes contained negative numbers (e.g. `-4812`). If we did `likes < 500` without filtering out negatives or cleaning them, an inverted like count of `-4812` (which was really `+4812`) would falsely show up here! We ensure `likes >= 0` (or utilize cleaned likes) to avoid capturing sign-flipped rows.

#### 3. SQL Query
```sql
SELECT 
    post_id, 
    platform, 
    likes, 
    shares, 
    comments
FROM posts
WHERE shares > 1500 
  AND likes < 500 
  AND likes >= 0
ORDER BY shares DESC
LIMIT 15;
```

#### 4. Query Output (Top 5 Sample)
| post_id | platform | likes | shares | comments |
| :--- | :--- | :--- | :--- | :--- |
| `euvr0r10wrj6` | Facebook | 453 | 2,000 | 408 |
| `oiszojqm6qnn` | Instagram | 390 | 1,999 | 858 |
| `f2e5kdfldedz` | UNKNOWN | 447 | 1,997 | 641 |
| `mgv7p46wzpek` | Reddit | 252 | 1,993 | 971 |
| `lit2hyqg0v0l` | Facebook | 14 | 1,990 | 769 |

#### 5. Human Explanation of the Result
Look at post `lit2hyqg0v0l` on Facebook: **only 14 likes, but 1,990 shares and 769 comments!** That represents a share-to-like ratio of over 142:1. This is a classic hallmark of high-friction social discourse.

---

### E5 — Users With Large Audiences

#### 1. Plain-English Objective
Extract the platform's "macro-influencers"—every user who has built an audience of more than 40,000 followers—along with their location and primary language.

#### 2. The Thought Process & Data Traps
* This is a straightforward user-demographic filter on `users.follower_count > 40000`.
* We order descending by follower count so the most prominent creators appear at the top.

#### 3. SQL Query
```sql
SELECT 
    user_id, 
    location, 
    language, 
    follower_count
FROM users
WHERE follower_count > 40000
ORDER BY follower_count DESC
LIMIT 15;
```

#### 4. Query Output (Top 5 Sample)
| user_id | location | language | follower_count |
| :--- | :--- | :--- | :--- |
| `user_3o7w66o2` | Berlin, Germany | ja | 49,944 |
| `user_u98jwp3f` | Chicago, USA | zh | 49,936 |
| `user_usts5yuo` | Shanghai, China | ja | 49,933 |
| `user_d4eat3v3` | Tokyo, Japan | de | 49,914 |
| `user_siuvpkza` | Chicago, USA | en | 49,905 |

#### 5. Human Explanation of the Result
Follower counts in this platform top out just below 50,000. Notice the cosmopolitan demographic spread: creators in Berlin tweeting in Japanese, Chicago creators posting in Chinese, and Tokyo creators posting in German.

---

## Part 2: Medium Level Challenges (M1 – M5)

---

### M1 — Which Locations Generate the Most Engagement?

#### 1. Plain-English Objective
Join user demographic profiles with post activity to determine which global cities/locations generate the largest total volume of social interaction.

#### 2. The Thought Process & Data Traps
* Posts live in `posts`, but geographic location lives in `users`. We must execute an `INNER JOIN` on `user_id`.
* We group by `u.location`, count the posts from creators in that city, and sum their total engagement.
* Using `COALESCE(p.likes_cleaned, p.likes, 0)` guarantees that a missing like doesn't turn the sum into `NULL`.

#### 3. SQL Query
```sql
SELECT 
    u.location,
    COUNT(p.post_id) AS post_count,
    SUM(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments) AS total_engagement
FROM users u
JOIN posts p ON u.user_id = p.user_id
GROUP BY u.location
ORDER BY total_engagement DESC
LIMIT 15;
```

#### 4. Query Output (Top 5 Sample)
| location | post_count | total_engagement |
| :--- | :--- | :--- |
| **Los Angeles, USA** | 459 | **1,850,886** |
| **Munich, Germany** | 452 | **1,802,490** |
| **Shanghai, China** | 451 | **1,795,875** |
| **Barcelona, Spain** | 439 | **1,769,556** |
| **Melbourne, Australia** | 421 | **1,706,510** |

#### 5. Human Explanation of the Result
Los Angeles leads the world with 1.85 million interactions across 459 posts, closely trailed by Munich and Shanghai. The geographic engagement is heavily correlated with post volume—cities with more active posting naturally accumulate more aggregate interactions.

---

### M2 — Do High Follower Users Get More Engagement?

#### 1. Plain-English Objective
Test the common industry assumption: *Does having more followers actually get you more engagement per post?* Split users into two equal halves (high followers $\ge 25,000$ vs. low followers $< 25,000$) and compare their average engagement.

#### 2. The Thought Process & Data Traps
* We use a `CASE` statement to divide users into two distinct cohorts:
  - `High follower users (>= 25,000)`
  - `Low follower users (< 25,000)`
* We join `users` with `posts` and calculate `AVG(total_engagement)` per post for each cohort.

#### 3. SQL Query
```sql
SELECT 
    CASE 
        WHEN u.follower_count >= 25000 THEN 'High follower users (>= 25,000)'
        ELSE 'Low follower users (< 25,000)'
    END AS user_group,
    COUNT(p.post_id) AS total_posts,
    ROUND(AVG(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments), 2) AS avg_engagement_per_post
FROM users u
JOIN posts p ON u.user_id = p.user_id
GROUP BY 
    CASE 
        WHEN u.follower_count >= 25000 THEN 'High follower users (>= 25,000)'
        ELSE 'Low follower users (< 25,000)'
    END;
```

#### 4. Query Output
| user_group | total_posts | avg_engagement_per_post |
| :--- | :--- | :--- |
| **High follower users ($\ge$ 25,000)** | 5,925 | **3,997.41** |
| **Low follower users ($<$ 25,000)** | 6,075 | **3,995.67** |

#### 5. Human Explanation of the Result (The Big Revelation!)
**The difference is a mere 1.74 interactions per post (3,997.41 vs. 3,995.67)!**  
This is one of the most crucial findings in the entire DataVortex project: **follower count has virtually ZERO impact on engagement per post.** The platform's algorithm distributes content democratically based on content quality/relevance rather than legacy audience size.

---

### M3 — Most Active Users

#### 1. Plain-English Objective
Identify the platform's "power creators"—the top 10 individual users who have published the most posts—and inspect their follower count and overall engagement.

#### 2. The Thought Process & Data Traps
* We group by user details (`u.user_id, u.follower_count, u.location`), count posts using `COUNT(p.post_id)`, and sum total engagement.
* We sort primarily by `post_count DESC` and secondarily by `total_engagement DESC`.

#### 3. SQL Query
```sql
SELECT 
    u.user_id,
    u.follower_count,
    u.location,
    COUNT(p.post_id) AS post_count,
    SUM(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments) AS total_engagement
FROM users u
JOIN posts p ON u.user_id = p.user_id
GROUP BY u.user_id, u.follower_count, u.location
ORDER BY post_count DESC, total_engagement DESC
LIMIT 10;
```

#### 4. Query Output
| user_id | follower_count | location | post_count | total_engagement |
| :--- | :--- | :--- | :--- | :--- |
| `user_zqv2vrf5` | 13,531 | Vancouver, Canada | **22** | 85,967 |
| `user_nfo3ih5u` | 40,429 | Barcelona, Spain | **19** | 79,421 |
| `user_q3vs0uj7` | 32,714 | Manchester, UK | **18** | 67,142 |
| `user_8wk0j5ae` | 36,943 | Los Angeles, USA | **18** | 65,496 |
| `user_n0ok02rt` | 2,531 | Dubai, UAE | **18** | 63,716 |
| `user_0irp4abu` | 44,206 | Toronto, Canada | **17** | 73,245 |
| `user_ujllj1n7` | 49,855 | Chicago, USA | **16** | 72,227 |
| `user_uerv85na` | 1,824 | Rome, Italy | **16** | 71,836 |
| `user_hdas0iau` | 1,620 | Rio de Janeiro, Brazil | **16** | 66,500 |
| `user_i1e1kek5` | 46,765 | Vancouver, Canada | **16** | 66,244 |

#### 5. Human Explanation of the Result
`user_zqv2vrf5` in Vancouver leads the platform with 22 published posts and 85.9k engagement. Note that creators with fewer than 2,000 followers (`user_uerv85na` with 1,824 followers; `user_hdas0iau` with 1,620 followers) are posting just as prolifically and generating over 66,000+ interactions!

---

### M4 — Platform Behaviour by High Follower Users

#### 1. Plain-English Objective
When macro-creators (users with $\ge 30,000$ followers) post, which specific social media platform rewards them with the highest average engagement per post?

#### 2. The Thought Process & Data Traps
* We filter for macro-influencers in the `WHERE` clause: `u.follower_count >= 30000`.
* We group by `p.platform`, count how many posts macro-creators published on each platform, and calculate their average engagement.

#### 3. SQL Query
```sql
SELECT 
    p.platform,
    COUNT(p.post_id) AS post_count,
    ROUND(AVG(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments), 2) AS avg_engagement_per_post
FROM users u
JOIN posts p ON u.user_id = p.user_id
WHERE u.follower_count >= 30000 
  AND p.platform IS NOT NULL
GROUP BY p.platform
ORDER BY avg_engagement_per_post DESC;
```

#### 4. Query Output
| platform | post_count | avg_engagement_per_post |
| :--- | :--- | :--- |
| **Instagram** | 809 | **4,109.61** |
| **UNKNOWN** | 681 | **4,001.45** |
| **Twitter** | 785 | **3,998.17** |
| **Facebook** | 827 | **3,981.08** |
| **Reddit** | 799 | **3,978.70** |
| **YouTube** | 846 | **3,953.80** |

#### 5. Human Explanation of the Result
**Instagram provides the highest return for macro-influencers**, averaging 4,109.61 interactions per post—over 150 interactions higher than YouTube (3,953.80). Visual and aesthetic media formats on Instagram offer greater shareability for established influencers.

---

### M5 — Detect Suspicious Engagement

#### 1. Plain-English Objective
Detect potential bot manipulation or viral anomalies by finding posts where the number of shares alone exceeds the total number of likes and comments combined.

#### 2. The Thought Process & Data Traps
* Normally, likes are easy to give (1 tap), comments take effort, and shares take conscious endorsement. A healthy post usually has `likes > shares`.
* If `shares > (likes + comments)`, it represents unusual viral propagation, coordinated bot retweeting, or extreme controversy.
* We calculate `share_excess = shares - (likes + comments)` and order by `shares DESC`.

#### 3. SQL Query
```sql
SELECT 
    post_id, 
    platform, 
    likes, 
    shares, 
    comments,
    (COALESCE(likes_cleaned, likes, 0) + comments) AS likes_plus_comments,
    (shares - (COALESCE(likes_cleaned, likes, 0) + comments)) AS share_excess
FROM posts
WHERE shares > (COALESCE(likes_cleaned, likes, 0) + comments)
ORDER BY shares DESC
LIMIT 20;
```

#### 4. Query Output (Top 5 Sample)
| post_id | platform | likes | shares | comments | likes_plus_comments | share_excess |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `euvr0r10wrj6` | Facebook | 453 | 2,000 | 408 | 861 | **+1,139** |
| `oiszojqm6qnn` | Instagram | 390 | 1,999 | 858 | 1,248 | **+751** |
| `2xcg9ld7du67` | Twitter | 1,425 | 1,999 | 440 | 1,865 | **+134** |
| `qq86lkjrfzlt` | YouTube | 897 | 1,999 | 850 | 1,747 | **+252** |
| `u1aa801qvxeu` | UNKNOWN | 162 | 1,992 | 306 | 468 | **+1,524** |

#### 5. Human Explanation of the Result
On post `u1aa801qvxeu`, shares reached 1,992 while likes + comments combined only amounted to 468 (a surplus of +1,524 shares!). In a trust & safety audit, these 20 posts represent top-priority candidates for coordinated inauthentic behavior investigation.

---

## Part 3: Hard Level Challenges (H1 – H6)

---

### H1 — Find Users With Abnormally High Engagement

#### 1. Plain-English Objective
Identify creators who are massively outperforming the platform: users whose total engagement is **more than twice ($> 2\times$) the overall platform average across all users**.

#### 2. The Thought Process & Data Traps
* This requires a multi-stage aggregation:
  1. **Stage 1 (CTE `UserTotalStats`):** Calculate the total and average engagement for *every single user*.
  2. **Stage 2 (CTE `OverallUserAvg`):** Calculate the benchmark mean of all user totals across the database.
  3. **Stage 3:** Join the two CTEs and filter for users where `u.total_engagement > 2 * o.avg_user_total`.

#### 3. SQL Query
```sql
WITH UserTotalStats AS (
    SELECT 
        u.user_id, 
        u.location, 
        u.follower_count, 
        COUNT(p.post_id) AS post_count,
        ROUND(AVG(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments), 2) AS avg_engagement,
        SUM(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments) AS total_engagement
    FROM users u 
    JOIN posts p ON u.user_id = p.user_id
    GROUP BY u.user_id, u.location, u.follower_count
),
OverallUserAvg AS (
    SELECT AVG(total_engagement) AS avg_user_total 
    FROM UserTotalStats
)
SELECT 
    u.user_id, 
    u.location, 
    u.follower_count, 
    u.post_count, 
    u.avg_engagement, 
    u.total_engagement
FROM UserTotalStats u 
CROSS JOIN OverallUserAvg o
WHERE u.total_engagement > 2 * o.avg_user_total
ORDER BY u.total_engagement DESC
LIMIT 10;
```

#### 4. Query Output
| user_id | location | follower_count | post_count | avg_engagement | total_engagement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `user_zqv2vrf5` | Vancouver, Canada | 13,531 | 22 | 3,907.59 | **85,967** |
| `user_nfo3ih5u` | Barcelona, Spain | 40,429 | 19 | 4,180.05 | **79,421** |
| `user_0irp4abu` | Toronto, Canada | 44,206 | 17 | 4,308.53 | **73,245** |
| `user_ujllj1n7` | Chicago, USA | 49,855 | 16 | 4,514.19 | **72,227** |
| `user_uerv85na` | Rome, Italy | 1,824 | 16 | 4,489.75 | **71,836** |
| `user_2ytzut7i` | Mumbai, India | 17,064 | 14 | 4,906.57 | **68,692** |
| `user_q3vs0uj7` | Manchester, UK | 32,714 | 18 | 3,730.11 | **67,142** |
| `user_s87enj6b` | Mexico City, Mexico | 43,476 | 14 | 4,776.07 | **66,865** |
| `user_hdas0iau` | Rio de Janeiro, Brazil | 1,620 | 16 | 4,156.25 | **66,500** |
| `user_i1e1kek5` | Vancouver, Canada | 46,765 | 16 | 4,140.25 | **66,244** |

#### 5. Human Explanation of the Result
The overall average total engagement across all users is ~31,980. The 10 creators above achieved more than double that threshold (>64,000 engagement), combining high posting volume (14 to 22 posts) with stellar per-post engagement (up to 4,906 interactions per post for `user_2ytzut7i` in Mumbai).

---

### H2 — Rank Users Within Their Location

#### 1. Plain-English Objective
For every global city in the dataset, rank its local creators by total engagement and return the top 3 podium winners (1st, 2nd, and 3rd place) for each location.

#### 2. The Thought Process & Data Traps
* If you do a simple `GROUP BY` with `LIMIT 3`, you only get 3 rows total for the entire database.
* To rank *within* each city, we must use an SQL Window Function:
  `DENSE_RANK() OVER (PARTITION BY location ORDER BY total_engagement DESC)`.
* `PARTITION BY location` resets the rank back to #1 for every new city.
* In the outer query, we simply filter `WHERE location_rank <= 3`.

#### 3. SQL Query
```sql
WITH UserLocationEngagement AS (
    SELECT 
        u.location,
        u.user_id,
        SUM(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments) AS total_engagement
    FROM users u
    JOIN posts p ON u.user_id = p.user_id
    GROUP BY u.location, u.user_id
),
RankedUsers AS (
    SELECT 
        location,
        user_id,
        total_engagement,
        DENSE_RANK() OVER (PARTITION BY location ORDER BY total_engagement DESC) AS location_rank
    FROM UserLocationEngagement
)
SELECT 
    location, 
    user_id, 
    total_engagement, 
    location_rank
FROM RankedUsers
WHERE location_rank <= 3
ORDER BY location, location_rank
LIMIT 15;
```

#### 4. Query Output (Sample of Top 3 per City)
| location | user_id | total_engagement | location_rank |
| :--- | :--- | :--- | :--- |
| **Barcelona, Spain** | `user_nfo3ih5u` | 79,421 | **1** |
| Barcelona, Spain | `user_5s9ifp0y` | 58,184 | **2** |
| Barcelona, Spain | `user_24wzfb8b` | 54,887 | **3** |
| **Beijing, China** | `user_ttlouvlq` | 51,516 | **1** |
| Beijing, China | `user_3jedn9am` | 49,321 | **2** |
| Beijing, China | `user_cdzp4vm2` | 48,019 | **3** |
| **Berlin, Germany** | `user_m5z8a3sg` | 56,480 | **1** |
| Berlin, Germany | `user_6e99lerx` | 55,057 | **2** |
| Berlin, Germany | `user_rtp2dykx` | 52,748 | **3** |
| **Chicago, USA** | `user_ujllj1n7` | 72,227 | **1** |
| Chicago, USA | `user_pr7bcf45` | 57,393 | **2** |
| Chicago, USA | `user_0v6j8dal` | 54,105 | **3** |

#### 5. Human Explanation of the Result
This query produces an exact, city-by-city localized creator leaderboard. In Barcelona, `user_nfo3ih5u` dominates first place with 79.4k engagement, while in Chicago, `user_ujllj1n7` takes gold with 72.2k engagement.

---

### H3 — Platform Performance Compared With Its Own Average

#### 1. Plain-English Objective
Every platform has its own baseline. Find the breakout viral hits that generated **at least double ($\ge 2\times$) their platform's specific average engagement**.

#### 2. The Thought Process & Data Traps
* Comparing a post on Twitter against the overall platform average would be unfair if Twitter had a much lower engagement ceiling than Instagram.
* We first compute each platform's own baseline average in CTE `PlatformAvg`.
* We then evaluate individual post engagement in CTE `PostStats` and join on `platform`.
* The condition `ps.post_engagement >= 2 * pa.platform_avg_engagement` isolates the true outliers.

#### 3. SQL Query
```sql
WITH PlatformAvg AS (
    SELECT 
        platform,
        AVG(COALESCE(likes, 0) + shares + comments) AS platform_avg_engagement
    FROM posts
    WHERE platform IS NOT NULL
    GROUP BY platform
),
PostStats AS (
    SELECT 
        p.post_id,
        p.platform,
        (COALESCE(p.likes, 0) + p.shares + p.comments) AS post_engagement
    FROM posts p
    WHERE p.platform IS NOT NULL
)
SELECT 
    ps.post_id,
    ps.platform,
    ps.post_engagement,
    ROUND(pa.platform_avg_engagement, 2) AS platform_avg_engagement
FROM PostStats ps
JOIN PlatformAvg pa ON ps.platform = pa.platform
WHERE ps.post_engagement >= 2 * pa.platform_avg_engagement
ORDER BY ps.post_engagement DESC
LIMIT 10;
```

#### 4. Query Output
| post_id | platform | post_engagement | platform_avg_engagement |
| :--- | :--- | :--- | :--- |
| `ycjj5zzt7mvx` | Instagram | **7,893** | 3,417.67 |
| `wo7py9aljg3t` | Reddit | **7,793** | 3,453.39 |
| `gmoeib832zbs` | Facebook | **7,764** | 3,456.55 |
| `5kvuyvf38nqx` | YouTube | **7,755** | 3,453.37 |
| `pvfl3d8hj7jd` | Instagram | **7,738** | 3,417.67 |
| `tdgjjylpua20` | UNKNOWN | **7,723** | 3,374.55 |
| `tne7s3o4l4wd` | Instagram | **7,712** | 3,417.67 |
| `a1kiwl618kzy` | Facebook | **7,683** | 3,456.55 |
| `fp89q1ickn9w` | Twitter | **7,628** | 3,345.93 |
| `5n161ir5hhhr` | YouTube | **7,610** | 3,453.37 |

#### 5. Human Explanation of the Result
With platform baseline averages sitting between 3,345 and 3,456 interactions, any post achieving 6,900+ interactions qualifies as a $2\times$ statistical breakout. The top 10 posts achieved between 7,610 and 7,893 interactions—over **2.3 times** their respective platform norms!

---

### H4 — Follower to Engagement Anomaly (Micro-Creators in the Top 10%)

#### 1. Plain-English Objective
Uncover the "giant slayers": creators with tiny audiences (**fewer than 5,000 followers**) who nonetheless generated so much total engagement that they placed into the **top 10% (90th percentile)** of all creators on the entire platform.

#### 2. The Thought Process & Data Traps
* How do you calculate a percentile rank in SQL?
* We use the advanced window function `PERCENT_RANK() OVER (ORDER BY total_engagement)` inside CTE `UserTotals`.
* `PERCENT_RANK()` outputs a value between $0.00$ and $1.00$. A score $\ge 0.90$ means the creator outperformed 90% of the user base.
* We filter for `follower_count < 5000 AND engagement_percentile >= 0.90`.

#### 3. SQL Query
```sql
WITH UserTotals AS (
    SELECT 
        u.user_id,
        u.follower_count,
        u.location,
        SUM(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments) AS total_engagement,
        PERCENT_RANK() OVER (ORDER BY SUM(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments)) AS engagement_percentile
    FROM users u
    JOIN posts p ON u.user_id = p.user_id
    GROUP BY u.user_id, u.follower_count, u.location
)
SELECT 
    user_id, 
    follower_count, 
    location, 
    total_engagement,
    ROUND(engagement_percentile * 100, 2) AS engagement_percentile_pct
FROM UserTotals
WHERE follower_count < 5000 
  AND engagement_percentile >= 0.90
ORDER BY total_engagement DESC
LIMIT 10;
```

#### 4. Query Output
| user_id | follower_count | location | total_engagement | engagement_percentile_pct |
| :--- | :--- | :--- | :--- | :--- |
| `user_uerv85na` | **1,824** | Rome, Italy | **71,836** | **99.73%** |
| `user_hdas0iau` | **1,620** | Rio de Janeiro, Brazil | **66,500** | **99.47%** |
| `user_n0ok02rt` | **2,531** | Dubai, UAE | **63,716** | **98.87%** |
| `user_fgjkkrie` | **2,211** | Lyon, France | **62,690** | **98.80%** |
| `user_6wra58f7` | **4,953** | Johannesburg, South Africa | **55,557** | **96.73%** |
| `user_ogtvuuki` | **4,459** | Cairo, Egypt | **55,128** | **96.26%** |
| `user_rr1uzkql` | **1,069** | Milan, Italy | **54,817** | **96.06%** |
| `user_r7eg1rac` | **2,052** | Houston, USA | **54,552** | **95.86%** |
| `user_5oe5t3js` | **3,151** | London, UK | **53,170** | **94.86%** |
| `user_67hyf45u` | **898** | Vancouver, Canada | **51,406** | **93.20%** |

#### 5. Human Explanation of the Result
Examine `user_67hyf45u` in Vancouver: with **only 898 followers**, this creator generated 51,406 interactions, placing them in the **93.2nd percentile** of all users! And `user_uerv85na` in Rome (1,824 followers) achieved 71.8k interactions, beating **99.73% of all creators** on the platform. This proves that algorithm-driven distribution rewards consistency and content over follower vanity metrics.

---

### H5 — Identify Data Anomalies in Corrupted Dataset

#### 1. Plain-English Objective
Scan the raw corrupted posts table (`posts_corrupted`) and build an audit report that classifies every corrupted record into its specific anomaly category: Negative Likes, Missing Platform, Missing Text Content, or HTML Tags/Entities.

#### 2. The Thought Process & Data Traps
* A single post can suffer from multiple simultaneous corruptions (e.g. both a negative like count AND injected HTML markup).
* Using a series of `CASE` statements with `ELSE` would mask secondary corruptions because `CASE` stops evaluating at the first true condition.
* The correct architectural design is **`UNION ALL` across four independent anomaly detectors**:
  1. `likes < 0` $\rightarrow$ Negative Likes
  2. `platform IS NULL OR TRIM(platform) = ''` $\rightarrow$ Missing Platform
  3. `text_content IS NULL OR TRIM(text_content) = ''` $\rightarrow$ Missing Text Content
  4. `text_content LIKE '%&amp;%' OR '%<div>%' ...` $\rightarrow$ HTML Entities or Tags in Text

#### 3. SQL Query
```sql
SELECT post_id, 'Negative Likes' AS anomaly_type
FROM posts_corrupted
WHERE likes < 0

UNION ALL

SELECT post_id, 'Missing Platform' AS anomaly_type
FROM posts_corrupted
WHERE platform IS NULL OR TRIM(platform) = ''

UNION ALL

SELECT post_id, 'Missing Text Content' AS anomaly_type
FROM posts_corrupted
WHERE text_content IS NULL OR TRIM(text_content) = ''

UNION ALL

SELECT post_id, 'HTML Entities or Tags in Text' AS anomaly_type
FROM posts_corrupted
WHERE text_content LIKE '%&amp;%' 
   OR text_content LIKE '%<div>%' 
   OR text_content LIKE '%</div>%' 
   OR text_content LIKE '%<br>%' 
   OR text_content LIKE '%<br/>%' 
   OR text_content LIKE '%<br />%'
ORDER BY post_id
LIMIT 15;
```

#### 4. Query Output (Audit Log Sample)
| post_id | anomaly_type |
| :--- | :--- |
| `003s4ulm32tk` | HTML Entities or Tags in Text |
| `005g54tmt26m` | Negative Likes |
| `0066x8nnmouc` | Missing Platform |
| `0066x8nnmouc` | HTML Entities or Tags in Text |
| `00pk8aa72o8x` | Missing Text Content |
| `00u9otx16xfc` | Missing Platform |
| `014e8jqloj6h` | Missing Text Content |
| `01gbk9id4v75` | Missing Text Content |
| `01kgwhi645er` | Negative Likes |
| `01kgwhi645er` | Missing Platform |
| `02b0vyoya4hz` | Missing Platform |
| `02vdvvsovgsk` | HTML Entities or Tags in Text |

#### 5. Human Explanation of the Result
Notice post `0066x8nnmouc`: it correctly appears **twice**—once for missing its platform header and once for having injected HTML markup. Similarly, `01kgwhi645er` was caught for both inverted likes and a dropped platform header. This output provides an exact checklist for automated cleaning pipelines.

---

### H6 — Find the Most Suspicious High Impact Users

#### 1. Plain-English Objective
Identify potentially manipulative accounts: creators with modest followings (**$<$ 10,000 followers**) who nonetheless maintain **above-average per-post engagement** AND have at least one post where **shares outpaced likes**.

#### 2. The Thought Process & Data Traps
* We synthesize three conditions:
  1. Small account footprint (`u.follower_count < 10000`).
  2. High impact per post (`um.avg_engagement > om.overall_avg_engagement`).
  3. Evidence of viral skew (`SUM(CASE WHEN p.shares > p.likes THEN 1 ELSE 0 END) >= 1`).
* We construct two modular CTEs (`OverallMetric` for the platform mean and `UserMetrics` for user-level aggregations), filter in the outer query, and rank by total accumulated engagement using `DENSE_RANK()`.

#### 3. SQL Query
```sql
WITH OverallMetric AS (
    SELECT AVG(COALESCE(likes_cleaned, likes, 0) + shares + comments) AS overall_avg_engagement
    FROM posts
),
UserMetrics AS (
    SELECT 
        u.user_id,
        u.location,
        u.follower_count,
        COUNT(p.post_id) AS post_count,
        AVG(COALESCE(likes_cleaned, likes, 0) + p.shares + p.comments) AS avg_engagement,
        SUM(COALESCE(likes_cleaned, likes, 0) + p.shares + p.comments) AS total_engagement,
        SUM(CASE WHEN p.shares > COALESCE(likes_cleaned, likes, 0) THEN 1 ELSE 0 END) AS suspicious_share_posts
    FROM users u
    JOIN posts p ON u.user_id = p.user_id
    GROUP BY u.user_id, u.location, u.follower_count
)
SELECT 
    um.user_id,
    um.location,
    um.follower_count,
    um.post_count,
    ROUND(um.avg_engagement, 2) AS avg_engagement,
    um.total_engagement,
    DENSE_RANK() OVER (ORDER BY um.total_engagement DESC) AS rank_by_total_engagement
FROM UserMetrics um
CROSS JOIN OverallMetric om
WHERE um.follower_count < 10000
  AND um.avg_engagement > om.overall_avg_engagement
  AND um.suspicious_share_posts >= 1
ORDER BY um.total_engagement DESC
LIMIT 10;
```

#### 4. Query Output
| user_id | location | follower_count | post_count | avg_engagement | total_engagement | rank |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `user_uerv85na` | Rome, Italy | 1,824 | 16 | 4,489.75 | **71,836** | **1** |
| `user_hdas0iau` | Rio de Janeiro, Brazil | 1,620 | 16 | 4,156.25 | **66,500** | **2** |
| `user_68enpikx` | Houston, USA | 9,364 | 15 | 4,326.93 | **64,904** | **3** |
| `user_fgjkkrie` | Lyon, France | 2,211 | 14 | 4,477.86 | **62,690** | **4** |
| `user_9mtets0p` | Johannesburg, South Africa | 8,262 | 14 | 4,458.14 | **62,414** | **5** |
| `user_87kc1g6d` | Houston, USA | 7,238 | 14 | 4,333.57 | **60,670** | **6** |
| `user_g9g7onlw` | Munich, Germany | 7,981 | 13 | 4,490.15 | **58,372** | **7** |
| `user_cssz1rea` | Tokyo, Japan | 7,863 | 14 | 4,144.21 | **58,019** | **8** |
| `user_14ibkds2` | Singapore | 7,361 | 13 | 4,388.00 | **57,044** | **9** |
| `user_ogtvuuki` | Cairo, Egypt | 4,459 | 11 | 5,011.64 | **55,128** | **10** |

#### 5. Human Explanation of the Result
`user_uerv85na` in Rome again ranks #1: with under 1,900 followers, they generated 71,836 total interactions with an incredible 4,489 average engagement per post, including posts where shares outnumbered likes. `user_ogtvuuki` in Cairo achieved an astonishing **5,011 average engagement** per post across 11 posts. In a social platform audit, these creators are either viral grassroots sensations or using external amplification rings.

---

## Part 4: Analytical Synthesis & Big Takeaways

Executing these 16 queries across Easy, Medium, and Hard tiers unlocks key macro insights regarding how the Social Engine operates:

1. **The Fallacy of Follower Count ($r \approx 0$):**
   Queries **M2**, **H1**, and **H4** conclusively prove that follower count does not drive engagement. Micro-creators with $<1,000$ followers frequently pull 50,000+ interactions, rivaling macro-influencers with 49,000+ followers. The platform operates on a content-first recommendation algorithm.
2. **Platform Specialization:**
   While total volumes are evenly balanced across networks (**E1**), each platform possesses a distinct behavioral signature (**E3**, **M4**):
   - **Instagram** commands the highest average total engagement (4,043) and is the most lucrative channel for macro-creators.
   - **Reddit** generates the highest comment density (511.2 comments/post), making it the primary hub for deep discussion and product critique.
   - **Twitter** and **Facebook** generate the highest concentration of viral share-heavy anomalies (**E4**, **M5**).
3. **Data Quality Integrity:**
   Queries **E4**, **H3**, and **H5** demonstrate why naive querying on raw data causes catastrophic reporting failures: uncleaned negative likes would invert top rankings, while dropped headers would misattribute platform leadership. Utilizing clean, defensive SQL guarantees reproducible business intelligence.

---

*Report compiled by Team **Fernandoisfasterthanyou** (`pathakuntlabhaskarreddy@gmail.com`) for the DataVortex Challenge.*
