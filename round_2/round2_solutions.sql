-- ==============================================================================
-- DATAVORTEX — ROUND 2: SQL CHALLENGES & QUERY SUITE WITH OUTPUT TABLES
-- Database Tables:
--   1. posts / posts_cleaned (post_id, user_id, platform, text_content, likes, shares, comments, likes_cleaned)
--   2. users / users_cleaned (user_id, location, language, account_created, follower_count)
--   3. posts_corrupted       (post_id, user_id, platform, text_content, likes, shares, comments)
-- ==============================================================================


-- ==============================================================================
-- EASY LEVEL
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- E1 — Platform Popularity
-- Challenge: Determine which social media platform has the highest number of posts. Ignore posts where the platform is missing. Return the platform name and number of posts.
-- ------------------------------------------------------------------------------
SELECT 
    platform, 
    COUNT(*) AS post_count
FROM posts
WHERE platform IS NOT NULL 
  AND TRIM(platform) != ''
GROUP BY platform
ORDER BY post_count DESC
LIMIT 1;

/*
-- [QUERY OUTPUT TABLE]
+----------+------------+
| platform | post_count |
+----------+------------+
| Facebook | 2074       |
+----------+------------+
-- (1 row)
*/


-- ------------------------------------------------------------------------------
-- E2 — Most Engaged Posts
-- Challenge: Find the top 10 posts based on total engagement. Total engagement is defined as likes + shares + comments. Ignore posts where likes are missing.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+--------------+-----------+-------+--------+----------+------------------+
| post_id      | platform  | likes | shares | comments | total_engagement |
+--------------+-----------+-------+--------+----------+------------------+
| ycjj5zzt7mvx | Instagram | 4983  | 1919   | 991      | 7893             |
| wo7py9aljg3t | Reddit    | 4864  | 1981   | 948      | 7793             |
| gmoeib832zbs | Facebook  | 4902  | 1880   | 982      | 7764             |
| 5kvuyvf38nqx | YouTube   | 4923  | 1971   | 861      | 7755             |
| pvfl3d8hj7jd | Instagram | 4989  | 1840   | 909      | 7738             |
| tdgjjylpua20 | UNKNOWN   | 4979  | 1932   | 812      | 7723             |
| tne7s3o4l4wd | Instagram | 4931  | 1903   | 878      | 7712             |
| a1kiwl618kzy | Facebook  | 4811  | 1952   | 920      | 7683             |
| fp89q1ickn9w | Twitter   | 4740  | 1933   | 955      | 7628             |
| 5n161ir5hhhr | YouTube   | 4751  | 1981   | 878      | 7610             |
+--------------+-----------+-------+--------+----------+------------------+
-- (10 rows)
*/


-- ------------------------------------------------------------------------------
-- E3 — Average Engagement by Platform
-- Challenge: Calculate the average likes, shares, and comments for each platform. Which platform generates the highest average total engagement?
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+-----------+-----------+------------+--------------+----------------------+
| platform  | avg_likes | avg_shares | avg_comments | avg_total_engagement |
+-----------+-----------+------------+--------------+----------------------+
| Instagram | 2502.99   | 1040.84    | 499.80       | 4043.63              |
| YouTube   | 2502.65   | 1011.83    | 504.38       | 4018.86              |
| Facebook  | 2508.24   | 984.17     | 506.94       | 3999.35              |
| Reddit    | 2465.48   | 1002.23    | 511.18       | 3978.89              |
| UNKNOWN   | 2481.21   | 998.61     | 496.54       | 3976.35              |
| Twitter   | 2448.89   | 1005.39    | 506.13       | 3960.41              |
+-----------+-----------+------------+--------------+----------------------+
-- (6 rows)
*/


-- ------------------------------------------------------------------------------
-- E4 — Highly Shared but Poorly Liked
-- Challenge: Identify posts that received more than 1,500 shares but fewer than 500 likes. Return the post ID, platform, likes, shares, and comments.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+--------------+-----------+-------+--------+----------+
| post_id      | platform  | likes | shares | comments |
+--------------+-----------+-------+--------+----------+
| euvr0r10wrj6 | Facebook  | 453   | 2000   | 408      |
| oiszojqm6qnn | Instagram | 390   | 1999   | 858      |
| f2e5kdfldedz | UNKNOWN   | 447   | 1997   | 641      |
| mgv7p46wzpek | Reddit    | 252   | 1993   | 971      |
| u1aa801qvxeu | UNKNOWN   | 162   | 1992   | 306      |
| 6s9mxoemn488 | Twitter   | 169   | 1991   | 856      |
| 0nsga7zrxpvt | YouTube   | 390   | 1991   | 848      |
| lit2hyqg0v0l | Facebook  | 14    | 1990   | 769      |
| 0xytg6ityrle | Instagram | 322   | 1989   | 170      |
| twgx52qb72eo | YouTube   | 462   | 1989   | 636      |
| k8hwwxunhdf4 | YouTube   | 25    | 1988   | 615      |
| e9f22k15r0e4 | UNKNOWN   | 449   | 1986   | 132      |
| vlh7lbn658qt | Twitter   | 357   | 1982   | 312      |
| elh8jw3o1btq | Twitter   | 430   | 1981   | 209      |
| nb0mfumbhk9s | Instagram | 16    | 1979   | 534      |
+--------------+-----------+-------+--------+----------+
-- (15 rows)
*/


-- ------------------------------------------------------------------------------
-- E5 — Users With Large Audiences
-- Challenge: Find all users with more than 40,000 followers. Display their user ID, location, language, and follower count.
-- ------------------------------------------------------------------------------
SELECT 
    user_id, 
    location, 
    language, 
    follower_count
FROM users
WHERE follower_count > 40000
ORDER BY follower_count DESC
LIMIT 15;

/*
-- [QUERY OUTPUT TABLE]
+---------------+------------------+----------+----------------+
| user_id       | location         | language | follower_count |
+---------------+------------------+----------+----------------+
| user_3o7w66o2 | Berlin, Germany  | ja       | 49944          |
| user_u98jwp3f | Chicago, USA     | zh       | 49936          |
| user_usts5yuo | Shanghai, China  | ja       | 49933          |
| user_d4eat3v3 | Tokyo, Japan     | de       | 49914          |
| user_siuvpkza | Chicago, USA     | en       | 49905          |
| user_ujllj1n7 | Chicago, USA     | es       | 49855          |
| user_kr0ydzhh | Barcelona, Spain | fr       | 49836          |
| user_9asov0m8 | Singapore        | hi       | 49763          |
| user_84k7x6zn | Barcelona, Spain | ja       | 49736          |
| user_t028mbub | Osaka, Japan     | en       | 49727          |
| user_i8ncp2ai | Delhi, India     | fr       | 49722          |
| user_sjm4thcl | Dubai, UAE       | en       | 49721          |
| user_b8ysn8r5 | Shanghai, China  | hi       | 49699          |
| user_kf84zwv2 | Paris, France    | es       | 49575          |
| user_8i81i0p7 | Los Angeles, USA | en       | 49518          |
+---------------+------------------+----------+----------------+
-- (15 rows)
*/



-- ==============================================================================
-- MEDIUM LEVEL
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- M1 — Which Locations Generate the Most Engagement?
-- Challenge: Using both datasets, calculate the total engagement generated by users from each location. Return the location, number of posts, and total engagement. Rank locations from highest to lowest engagement.
-- ------------------------------------------------------------------------------
SELECT 
    u.location,
    COUNT(p.post_id) AS post_count,
    SUM(COALESCE(p.likes_cleaned, p.likes, 0) + p.shares + p.comments) AS total_engagement
FROM users u
JOIN posts p ON u.user_id = p.user_id
GROUP BY u.location
ORDER BY total_engagement DESC
LIMIT 15;

/*
-- [QUERY OUTPUT TABLE]
+------------------------+------------+------------------+
| location               | post_count | total_engagement |
+------------------------+------------+------------------+
| Los Angeles, USA       | 459        | 1850886          |
| Munich, Germany        | 452        | 1802490          |
| Shanghai, China        | 451        | 1795875          |
| Barcelona, Spain       | 439        | 1769556          |
| Melbourne, Australia   | 421        | 1706510          |
| Dubai, UAE             | 421        | 1700950          |
| Houston, USA           | 422        | 1660952          |
| Rio de Janeiro, Brazil | 414        | 1655378          |
| Osaka, Japan           | 398        | 1646374          |
| Mumbai, India          | 413        | 1612905          |
| Milan, Italy           | 403        | 1605068          |
| Chicago, USA           | 392        | 1588980          |
| Paris, France          | 379        | 1547833          |
| London, UK             | 386        | 1542458          |
| Beijing, China         | 373        | 1516335          |
+------------------------+------------+------------------+
-- (15 rows)
*/


-- ------------------------------------------------------------------------------
-- M2 — Do High Follower Users Get More Engagement?
-- Challenge: Divide users into two groups: High follower users (>= 25,000) and Low follower users (< 25,000). Compare their average engagement per post.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+---------------------------------+-------------+-------------------------+
| user_group                      | total_posts | avg_engagement_per_post |
+---------------------------------+-------------+-------------------------+
| High follower users (>= 25,000) | 5925        | 3997.41                 |
| Low follower users (< 25,000)   | 6075        | 3995.67                 |
+---------------------------------+-------------+-------------------------+
-- (2 rows)
*/


-- ------------------------------------------------------------------------------
-- M3 — Most Active Users
-- Challenge: Find the top 10 users who have created the highest number of posts. Display their follower count, location, post count, and total engagement.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+---------------+----------------+------------------------+------------+------------------+
| user_id       | follower_count | location               | post_count | total_engagement |
+---------------+----------------+------------------------+------------+------------------+
| user_zqv2vrf5 | 13531          | Vancouver, Canada      | 22         | 85967            |
| user_nfo3ih5u | 40429          | Barcelona, Spain       | 19         | 79421            |
| user_q3vs0uj7 | 32714          | Manchester, UK         | 18         | 67142            |
| user_8wk0j5ae | 36943          | Los Angeles, USA       | 18         | 65496            |
| user_n0ok02rt | 2531           | Dubai, UAE             | 18         | 63716            |
| user_0irp4abu | 44206          | Toronto, Canada        | 17         | 73245            |
| user_ujllj1n7 | 49855          | Chicago, USA           | 16         | 72227            |
| user_uerv85na | 1824           | Rome, Italy            | 16         | 71836            |
| user_hdas0iau | 1620           | Rio de Janeiro, Brazil | 16         | 66500            |
| user_i1e1kek5 | 46765          | Vancouver, Canada      | 16         | 66244            |
+---------------+----------------+------------------------+------------+------------------+
-- (10 rows)
*/


-- ------------------------------------------------------------------------------
-- M4 — Platform Behaviour by High Follower Users
-- Challenge: Among users with at least 30,000 followers, determine which platform gives them the highest average engagement per post.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+-----------+------------+-------------------------+
| platform  | post_count | avg_engagement_per_post |
+-----------+------------+-------------------------+
| Instagram | 809        | 4109.61                 |
| UNKNOWN   | 681        | 4001.45                 |
| Twitter   | 785        | 3998.17                 |
| Facebook  | 827        | 3981.08                 |
| Reddit    | 799        | 3978.70                 |
| YouTube   | 846        | 3953.80                 |
+-----------+------------+-------------------------+
-- (6 rows)
*/


-- ------------------------------------------------------------------------------
-- M5 — Detect Suspicious Engagement
-- Challenge: Find posts where the number of shares is greater than the number of likes and comments combined. Such posts may represent unusual sharing behaviour. Return the top 20.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+--------------+-----------+-------+--------+----------+---------------------+--------------+
| post_id      | platform  | likes | shares | comments | likes_plus_comments | share_excess |
+--------------+-----------+-------+--------+----------+---------------------+--------------+
| euvr0r10wrj6 | Facebook  | 453   | 2000   | 408      | 861                 | 1139         |
| oiszojqm6qnn | Instagram | 390   | 1999   | 858      | 1248                | 751          |
| 2xcg9ld7du67 | Twitter   | 1425  | 1999   | 440      | 1865                | 134          |
| qq86lkjrfzlt | YouTube   | 897   | 1999   | 850      | 1747                | 252          |
| sjv1fkkjr8e1 | UNKNOWN   | 1524  | 1998   | 129      | 1653                | 345          |
| rryxmp0nra55 | Instagram | 981   | 1997   | 958      | 1939                | 58           |
| zvj4ja8bp4xx | UNKNOWN   | 1503  | 1997   | 338      | 1841                | 156          |
| f2e5kdfldedz | UNKNOWN   | 447   | 1997   | 641      | 1088                | 909          |
| 0a5v0izr0rbb | YouTube   | NULL  | 1997   | 493      | 802                 | 1195         |
| x8wq022t0pa5 | UNKNOWN   | 1380  | 1997   | 201      | 1581                | 416          |
| lx50tyodyt6m | Instagram | 1545  | 1996   | 63       | 1608                | 388          |
| 8leyamlw9c72 | Reddit    | 947   | 1994   | 331      | 1278                | 716          |
| mgv7p46wzpek | Reddit    | 252   | 1993   | 971      | 1223                | 770          |
| mgjoprfiflsm | Facebook  | 803   | 1992   | 644      | 1447                | 545          |
| ib1a4n09l99i | Reddit    | 632   | 1992   | 728      | 1360                | 632          |
| u1aa801qvxeu | UNKNOWN   | 162   | 1992   | 306      | 468                 | 1524         |
| 16ekyit17mzt | Twitter   | NULL  | 1991   | 439      | 1091                | 900          |
| 6s9mxoemn488 | Twitter   | 169   | 1991   | 856      | 1025                | 966          |
| 8d1dbq225yud | Instagram | 539   | 1991   | 544      | 1083                | 908          |
| 0nsga7zrxpvt | YouTube   | 390   | 1991   | 848      | 1238                | 753          |
+--------------+-----------+-------+--------+----------+---------------------+--------------+
-- (20 rows)
*/



-- ==============================================================================
-- HARD LEVEL
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- H1 — Find Users With Abnormally High Engagement
-- Challenge: Calculate the average total engagement per user. Identify users whose average engagement per post is more than twice the overall average engagement per post. Return the user ID, location, follower count, post count, and average engagement.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+---------------+------------------------+----------------+------------+----------------+------------------+
| user_id       | location               | follower_count | post_count | avg_engagement | total_engagement |
+---------------+------------------------+----------------+------------+----------------+------------------+
| user_zqv2vrf5 | Vancouver, Canada      | 13531          | 22         | 3907.59        | 85967            |
| user_nfo3ih5u | Barcelona, Spain       | 40429          | 19         | 4180.05        | 79421            |
| user_0irp4abu | Toronto, Canada        | 44206          | 17         | 4308.53        | 73245            |
| user_ujllj1n7 | Chicago, USA           | 49855          | 16         | 4514.19        | 72227            |
| user_uerv85na | Rome, Italy            | 1824           | 16         | 4489.75        | 71836            |
| user_2ytzut7i | Mumbai, India          | 17064          | 14         | 4906.57        | 68692            |
| user_q3vs0uj7 | Manchester, UK         | 32714          | 18         | 3730.11        | 67142            |
| user_s87enj6b | Mexico City, Mexico    | 43476          | 14         | 4776.07        | 66865            |
| user_hdas0iau | Rio de Janeiro, Brazil | 1620           | 16         | 4156.25        | 66500            |
| user_i1e1kek5 | Vancouver, Canada      | 46765          | 16         | 4140.25        | 66244            |
+---------------+------------------------+----------------+------------+----------------+------------------+
-- (10 rows)
*/


-- ------------------------------------------------------------------------------
-- H2 — Rank Users Within Their Location
-- Challenge: For every location, rank users based on their total engagement. Return only the top 3 users from each location.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+------------------+---------------+------------------+---------------+
| location         | user_id       | total_engagement | location_rank |
+------------------+---------------+------------------+---------------+
| Barcelona, Spain | user_nfo3ih5u | 79421            | 1             |
| Barcelona, Spain | user_5s9ifp0y | 58184            | 2             |
| Barcelona, Spain | user_24wzfb8b | 54887            | 3             |
| Beijing, China   | user_ttlouvlq | 51516            | 1             |
| Beijing, China   | user_3jedn9am | 49321            | 2             |
| Beijing, China   | user_cdzp4vm2 | 48019            | 3             |
| Berlin, Germany  | user_m5z8a3sg | 56480            | 1             |
| Berlin, Germany  | user_6e99lerx | 55057            | 2             |
| Berlin, Germany  | user_rtp2dykx | 52748            | 3             |
| Cairo, Egypt     | user_cuzig14g | 58095            | 1             |
| Cairo, Egypt     | user_ogtvuuki | 55128            | 2             |
| Cairo, Egypt     | user_g37hrbp3 | 53809            | 3             |
| Chicago, USA     | user_ujllj1n7 | 72227            | 1             |
| Chicago, USA     | user_pr7bcf45 | 57393            | 2             |
| Chicago, USA     | user_0v6j8dal | 54105            | 3             |
+------------------+---------------+------------------+---------------+
-- (15 rows)
*/


-- ------------------------------------------------------------------------------
-- H3 — Platform Performance Compared With Its Own Average
-- Challenge: For every platform, identify posts whose engagement is significantly higher than the average engagement of that platform. A post is considered exceptional if its engagement is at least 2× the average engagement of its platform.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+--------------+-----------+-----------------+-------------------------+
| post_id      | platform  | post_engagement | platform_avg_engagement |
+--------------+-----------+-----------------+-------------------------+
| ycjj5zzt7mvx | Instagram | 7893            | 3417.67                 |
| wo7py9aljg3t | Reddit    | 7793            | 3453.39                 |
| gmoeib832zbs | Facebook  | 7764            | 3456.55                 |
| 5kvuyvf38nqx | YouTube   | 7755            | 3453.37                 |
| pvfl3d8hj7jd | Instagram | 7738            | 3417.67                 |
| tdgjjylpua20 | UNKNOWN   | 7723            | 3374.55                 |
| tne7s3o4l4wd | Instagram | 7712            | 3417.67                 |
| a1kiwl618kzy | Facebook  | 7683            | 3456.55                 |
| fp89q1ickn9w | Twitter   | 7628            | 3345.93                 |
| 5n161ir5hhhr | YouTube   | 7610            | 3453.37                 |
+--------------+-----------+-----------------+-------------------------+
-- (10 rows)
*/


-- ------------------------------------------------------------------------------
-- H4 — Follower to Engagement Anomaly
-- Challenge: Find users who have fewer than 5,000 followers but whose total post engagement places them among the top 10% of all users.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+---------------+----------------+----------------------------+------------------+---------------------------+
| user_id       | follower_count | location                   | total_engagement | engagement_percentile_pct |
+---------------+----------------+----------------------------+------------------+---------------------------+
| user_uerv85na | 1824           | Rome, Italy                | 71836            | 99.73                     |
| user_hdas0iau | 1620           | Rio de Janeiro, Brazil     | 66500            | 99.47                     |
| user_n0ok02rt | 2531           | Dubai, UAE                 | 63716            | 98.87                     |
| user_fgjkkrie | 2211           | Lyon, France               | 62690            | 98.80                     |
| user_6wra58f7 | 4953           | Johannesburg, South Africa | 55557            | 96.73                     |
| user_ogtvuuki | 4459           | Cairo, Egypt               | 55128            | 96.26                     |
| user_rr1uzkql | 1069           | Milan, Italy               | 54817            | 96.06                     |
| user_r7eg1rac | 2052           | Houston, USA               | 54552            | 95.86                     |
| user_5oe5t3js | 3151           | London, UK                 | 53170            | 94.86                     |
| user_67hyf45u | 898            | Vancouver, Canada          | 51406            | 93.20                     |
+---------------+----------------+----------------------------+------------------+---------------------------+
-- (10 rows)
*/


-- ------------------------------------------------------------------------------
-- H5 — Identify Data Anomalies (Corrupted Dataset)
-- Challenge: Identify potentially corrupted posts where likes are negative, platform is missing, text content is missing, or text contains HTML entities/tags. Return post ID and anomaly type.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+--------------+-------------------------------+
| post_id      | anomaly_type                  |
+--------------+-------------------------------+
| 003s4ulm32tk | HTML Entities or Tags in Text |
| 005g54tmt26m | Negative Likes                |
| 0066x8nnmouc | Missing Platform              |
| 0066x8nnmouc | HTML Entities or Tags in Text |
| 00pk8aa72o8x | Missing Text Content          |
| 00u9otx16xfc | Missing Platform              |
| 014e8jqloj6h | Missing Text Content          |
| 01gbk9id4v75 | Missing Text Content          |
| 01kgwhi645er | Negative Likes                |
| 01kgwhi645er | Missing Platform              |
| 02b0vyoya4hz | Missing Platform              |
| 02vdvvsovgsk | HTML Entities or Tags in Text |
| 030vdql1vwxl | HTML Entities or Tags in Text |
| 033i6hfsrdo8 | Missing Platform              |
| 033i6hfsrdo8 | Missing Text Content          |
+--------------+-------------------------------+
-- (15 rows)
*/


-- ------------------------------------------------------------------------------
-- H6 — Find the Most Suspicious High Impact Users
-- Challenge: Identify users who have < 10,000 followers, whose average post engagement is above overall average, and at least one post has more shares than likes. Rank by total engagement.
-- ------------------------------------------------------------------------------
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

/*
-- [QUERY OUTPUT TABLE]
+---------------+----------------------------+----------------+------------+----------------+------------------+--------------------------+
| user_id       | location                   | follower_count | post_count | avg_engagement | total_engagement | rank_by_total_engagement |
+---------------+----------------------------+----------------+------------+----------------+------------------+--------------------------+
| user_uerv85na | Rome, Italy                | 1824           | 16         | 4489.75        | 71836            | 1                        |
| user_hdas0iau | Rio de Janeiro, Brazil     | 1620           | 16         | 4156.25        | 66500            | 2                        |
| user_68enpikx | Houston, USA               | 9364           | 15         | 4326.93        | 64904            | 3                        |
| user_fgjkkrie | Lyon, France               | 2211           | 14         | 4477.86        | 62690            | 4                        |
| user_9mtets0p | Johannesburg, South Africa | 8262           | 14         | 4458.14        | 62414            | 5                        |
| user_87kc1g6d | Houston, USA               | 7238           | 14         | 4333.57        | 60670            | 6                        |
| user_g9g7onlw | Munich, Germany            | 7981           | 13         | 4490.15        | 58372            | 7                        |
| user_cssz1rea | Tokyo, Japan               | 7863           | 14         | 4144.21        | 58019            | 8                        |
| user_14ibkds2 | Singapore                  | 7361           | 13         | 4388           | 57044            | 9                        |
| user_ogtvuuki | Cairo, Egypt               | 4459           | 11         | 5011.64        | 55128            | 10                       |
+---------------+----------------------------+----------------+------------+----------------+------------------+--------------------------+
-- (10 rows)
*/

