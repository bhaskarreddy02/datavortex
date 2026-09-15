# DataVortex: Round 2 SQL Challenge Solutions & Output Tables

> **Executable SQL Queries and Verified Dataset Output Tables for Round 2 Analytics Challenges**

---


## EASY LEVEL

### E1 — Platform Popularity

**Challenge**: *Determine which social media platform has the highest number of posts. Ignore posts where the platform is missing. Return the platform name and number of posts.*

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

#### Query Output Table:

| platform | post_count |
| ---: | ---: |
| Facebook | 2,074 |

---

### E2 — Most Engaged Posts

**Challenge**: *Find the top 10 posts based on total engagement. Total engagement is defined as likes + shares + comments. Ignore posts where likes are missing.*

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

#### Query Output Table:

| post_id | platform | likes | shares | comments | total_engagement |
| ---: | ---: | ---: | ---: | ---: | ---: |
| ycjj5zzt7mvx | Instagram | 4,983 | 1,919 | 991 | 7,893 |
| wo7py9aljg3t | Reddit | 4,864 | 1,981 | 948 | 7,793 |
| gmoeib832zbs | Facebook | 4,902 | 1,880 | 982 | 7,764 |
| 5kvuyvf38nqx | YouTube | 4,923 | 1,971 | 861 | 7,755 |
| pvfl3d8hj7jd | Instagram | 4,989 | 1,840 | 909 | 7,738 |
| tdgjjylpua20 | UNKNOWN | 4,979 | 1,932 | 812 | 7,723 |
| tne7s3o4l4wd | Instagram | 4,931 | 1,903 | 878 | 7,712 |
| a1kiwl618kzy | Facebook | 4,811 | 1,952 | 920 | 7,683 |
| fp89q1ickn9w | Twitter | 4,740 | 1,933 | 955 | 7,628 |
| 5n161ir5hhhr | YouTube | 4,751 | 1,981 | 878 | 7,610 |

---

### E3 — Average Engagement by Platform

**Challenge**: *Calculate the average likes, shares, and comments for each platform. Which platform generates the highest average total engagement?*

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

#### Query Output Table:

| platform | avg_likes | avg_shares | avg_comments | avg_total_engagement |
| ---: | ---: | ---: | ---: | ---: |
| Instagram | 2,502.99 | 1,040.84 | 499.80 | 4,043.63 |
| YouTube | 2,502.65 | 1,011.83 | 504.38 | 4,018.86 |
| Facebook | 2,508.24 | 984.17 | 506.94 | 3,999.35 |
| Reddit | 2,465.48 | 1,002.23 | 511.18 | 3,978.89 |
| UNKNOWN | 2,481.21 | 998.61 | 496.54 | 3,976.35 |
| Twitter | 2,448.89 | 1,005.39 | 506.13 | 3,960.41 |

---

### E4 — Highly Shared but Poorly Liked

**Challenge**: *Identify posts that received more than 1,500 shares but fewer than 500 likes. Return the post ID, platform, likes, shares, and comments.*

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

#### Query Output Table:

| post_id | platform | likes | shares | comments |
| ---: | ---: | ---: | ---: | ---: |
| euvr0r10wrj6 | Facebook | 453 | 2,000 | 408 |
| oiszojqm6qnn | Instagram | 390 | 1,999 | 858 |
| f2e5kdfldedz | UNKNOWN | 447 | 1,997 | 641 |
| mgv7p46wzpek | Reddit | 252 | 1,993 | 971 |
| u1aa801qvxeu | UNKNOWN | 162 | 1,992 | 306 |
| 6s9mxoemn488 | Twitter | 169 | 1,991 | 856 |
| 0nsga7zrxpvt | YouTube | 390 | 1,991 | 848 |
| lit2hyqg0v0l | Facebook | 14 | 1,990 | 769 |
| 0xytg6ityrle | Instagram | 322 | 1,989 | 170 |
| twgx52qb72eo | YouTube | 462 | 1,989 | 636 |
| k8hwwxunhdf4 | YouTube | 25 | 1,988 | 615 |
| e9f22k15r0e4 | UNKNOWN | 449 | 1,986 | 132 |
| vlh7lbn658qt | Twitter | 357 | 1,982 | 312 |
| elh8jw3o1btq | Twitter | 430 | 1,981 | 209 |
| nb0mfumbhk9s | Instagram | 16 | 1,979 | 534 |

---

### E5 — Users With Large Audiences

**Challenge**: *Find all users with more than 40,000 followers. Display their user ID, location, language, and follower count.*

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

#### Query Output Table:

| user_id | location | language | follower_count |
| ---: | ---: | ---: | ---: |
| user_3o7w66o2 | Berlin, Germany | ja | 49,944 |
| user_u98jwp3f | Chicago, USA | zh | 49,936 |
| user_usts5yuo | Shanghai, China | ja | 49,933 |
| user_d4eat3v3 | Tokyo, Japan | de | 49,914 |
| user_siuvpkza | Chicago, USA | en | 49,905 |
| user_ujllj1n7 | Chicago, USA | es | 49,855 |
| user_kr0ydzhh | Barcelona, Spain | fr | 49,836 |
| user_9asov0m8 | Singapore | hi | 49,763 |
| user_84k7x6zn | Barcelona, Spain | ja | 49,736 |
| user_t028mbub | Osaka, Japan | en | 49,727 |
| user_i8ncp2ai | Delhi, India | fr | 49,722 |
| user_sjm4thcl | Dubai, UAE | en | 49,721 |
| user_b8ysn8r5 | Shanghai, China | hi | 49,699 |
| user_kf84zwv2 | Paris, France | es | 49,575 |
| user_8i81i0p7 | Los Angeles, USA | en | 49,518 |

---


## MEDIUM LEVEL

### M1 — Which Locations Generate the Most Engagement?

**Challenge**: *Using both datasets, calculate the total engagement generated by users from each location. Return the location, number of posts, and total engagement. Rank locations from highest to lowest engagement.*

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

#### Query Output Table:

| location | post_count | total_engagement |
| ---: | ---: | ---: |
| Los Angeles, USA | 459 | 1,850,886 |
| Munich, Germany | 452 | 1,802,490 |
| Shanghai, China | 451 | 1,795,875 |
| Barcelona, Spain | 439 | 1,769,556 |
| Melbourne, Australia | 421 | 1,706,510 |
| Dubai, UAE | 421 | 1,700,950 |
| Houston, USA | 422 | 1,660,952 |
| Rio de Janeiro, Brazil | 414 | 1,655,378 |
| Osaka, Japan | 398 | 1,646,374 |
| Mumbai, India | 413 | 1,612,905 |
| Milan, Italy | 403 | 1,605,068 |
| Chicago, USA | 392 | 1,588,980 |
| Paris, France | 379 | 1,547,833 |
| London, UK | 386 | 1,542,458 |
| Beijing, China | 373 | 1,516,335 |

---

### M2 — Do High Follower Users Get More Engagement?

**Challenge**: *Divide users into two groups: High follower users (>= 25,000) and Low follower users (< 25,000). Compare their average engagement per post.*

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

#### Query Output Table:

| user_group | total_posts | avg_engagement_per_post |
| ---: | ---: | ---: |
| High follower users (>= 25,000) | 5,925 | 3,997.41 |
| Low follower users (< 25,000) | 6,075 | 3,995.67 |

---

### M3 — Most Active Users

**Challenge**: *Find the top 10 users who have created the highest number of posts. Display their follower count, location, post count, and total engagement.*

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

#### Query Output Table:

| user_id | follower_count | location | post_count | total_engagement |
| ---: | ---: | ---: | ---: | ---: |
| user_zqv2vrf5 | 13,531 | Vancouver, Canada | 22 | 85,967 |
| user_nfo3ih5u | 40,429 | Barcelona, Spain | 19 | 79,421 |
| user_q3vs0uj7 | 32,714 | Manchester, UK | 18 | 67,142 |
| user_8wk0j5ae | 36,943 | Los Angeles, USA | 18 | 65,496 |
| user_n0ok02rt | 2,531 | Dubai, UAE | 18 | 63,716 |
| user_0irp4abu | 44,206 | Toronto, Canada | 17 | 73,245 |
| user_ujllj1n7 | 49,855 | Chicago, USA | 16 | 72,227 |
| user_uerv85na | 1,824 | Rome, Italy | 16 | 71,836 |
| user_hdas0iau | 1,620 | Rio de Janeiro, Brazil | 16 | 66,500 |
| user_i1e1kek5 | 46,765 | Vancouver, Canada | 16 | 66,244 |

---

### M4 — Platform Behaviour by High Follower Users

**Challenge**: *Among users with at least 30,000 followers, determine which platform gives them the highest average engagement per post.*

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

#### Query Output Table:

| platform | post_count | avg_engagement_per_post |
| ---: | ---: | ---: |
| Instagram | 809 | 4,109.61 |
| UNKNOWN | 681 | 4,001.45 |
| Twitter | 785 | 3,998.17 |
| Facebook | 827 | 3,981.08 |
| Reddit | 799 | 3,978.70 |
| YouTube | 846 | 3,953.80 |

---

### M5 — Detect Suspicious Engagement

**Challenge**: *Find posts where the number of shares is greater than the number of likes and comments combined. Such posts may represent unusual sharing behaviour. Return the top 20.*

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

#### Query Output Table:

| post_id | platform | likes | shares | comments | likes_plus_comments | share_excess |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| euvr0r10wrj6 | Facebook | 453 | 2,000 | 408 | 861 | 1,139 |
| oiszojqm6qnn | Instagram | 390 | 1,999 | 858 | 1,248 | 751 |
| 2xcg9ld7du67 | Twitter | 1,425 | 1,999 | 440 | 1,865 | 134 |
| qq86lkjrfzlt | YouTube | 897 | 1,999 | 850 | 1,747 | 252 |
| sjv1fkkjr8e1 | UNKNOWN | 1,524 | 1,998 | 129 | 1,653 | 345 |
| rryxmp0nra55 | Instagram | 981 | 1,997 | 958 | 1,939 | 58 |
| zvj4ja8bp4xx | UNKNOWN | 1,503 | 1,997 | 338 | 1,841 | 156 |
| f2e5kdfldedz | UNKNOWN | 447 | 1,997 | 641 | 1,088 | 909 |
| 0a5v0izr0rbb | YouTube | *NULL* | 1,997 | 493 | 802 | 1,195 |
| x8wq022t0pa5 | UNKNOWN | 1,380 | 1,997 | 201 | 1,581 | 416 |
| lx50tyodyt6m | Instagram | 1,545 | 1,996 | 63 | 1,608 | 388 |
| 8leyamlw9c72 | Reddit | 947 | 1,994 | 331 | 1,278 | 716 |
| mgv7p46wzpek | Reddit | 252 | 1,993 | 971 | 1,223 | 770 |
| mgjoprfiflsm | Facebook | 803 | 1,992 | 644 | 1,447 | 545 |
| ib1a4n09l99i | Reddit | 632 | 1,992 | 728 | 1,360 | 632 |
| u1aa801qvxeu | UNKNOWN | 162 | 1,992 | 306 | 468 | 1,524 |
| 16ekyit17mzt | Twitter | *NULL* | 1,991 | 439 | 1,091 | 900 |
| 6s9mxoemn488 | Twitter | 169 | 1,991 | 856 | 1,025 | 966 |
| 8d1dbq225yud | Instagram | 539 | 1,991 | 544 | 1,083 | 908 |
| 0nsga7zrxpvt | YouTube | 390 | 1,991 | 848 | 1,238 | 753 |

---


## HARD LEVEL

### H1 — Find Users With Abnormally High Engagement

**Challenge**: *Calculate the average total engagement per user. Identify users whose average engagement per post is more than twice the overall average engagement per post. Return the user ID, location, follower count, post count, and average engagement.*

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

#### Query Output Table:

| user_id | location | follower_count | post_count | avg_engagement | total_engagement |
| ---: | ---: | ---: | ---: | ---: | ---: |
| user_zqv2vrf5 | Vancouver, Canada | 13,531 | 22 | 3,907.59 | 85,967 |
| user_nfo3ih5u | Barcelona, Spain | 40,429 | 19 | 4,180.05 | 79,421 |
| user_0irp4abu | Toronto, Canada | 44,206 | 17 | 4,308.53 | 73,245 |
| user_ujllj1n7 | Chicago, USA | 49,855 | 16 | 4,514.19 | 72,227 |
| user_uerv85na | Rome, Italy | 1,824 | 16 | 4,489.75 | 71,836 |
| user_2ytzut7i | Mumbai, India | 17,064 | 14 | 4,906.57 | 68,692 |
| user_q3vs0uj7 | Manchester, UK | 32,714 | 18 | 3,730.11 | 67,142 |
| user_s87enj6b | Mexico City, Mexico | 43,476 | 14 | 4,776.07 | 66,865 |
| user_hdas0iau | Rio de Janeiro, Brazil | 1,620 | 16 | 4,156.25 | 66,500 |
| user_i1e1kek5 | Vancouver, Canada | 46,765 | 16 | 4,140.25 | 66,244 |

---

### H2 — Rank Users Within Their Location

**Challenge**: *For every location, rank users based on their total engagement. Return only the top 3 users from each location.*

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

#### Query Output Table:

| location | user_id | total_engagement | location_rank |
| ---: | ---: | ---: | ---: |
| Barcelona, Spain | user_nfo3ih5u | 79,421 | 1 |
| Barcelona, Spain | user_5s9ifp0y | 58,184 | 2 |
| Barcelona, Spain | user_24wzfb8b | 54,887 | 3 |
| Beijing, China | user_ttlouvlq | 51,516 | 1 |
| Beijing, China | user_3jedn9am | 49,321 | 2 |
| Beijing, China | user_cdzp4vm2 | 48,019 | 3 |
| Berlin, Germany | user_m5z8a3sg | 56,480 | 1 |
| Berlin, Germany | user_6e99lerx | 55,057 | 2 |
| Berlin, Germany | user_rtp2dykx | 52,748 | 3 |
| Cairo, Egypt | user_cuzig14g | 58,095 | 1 |
| Cairo, Egypt | user_ogtvuuki | 55,128 | 2 |
| Cairo, Egypt | user_g37hrbp3 | 53,809 | 3 |
| Chicago, USA | user_ujllj1n7 | 72,227 | 1 |
| Chicago, USA | user_pr7bcf45 | 57,393 | 2 |
| Chicago, USA | user_0v6j8dal | 54,105 | 3 |

---

### H3 — Platform Performance Compared With Its Own Average

**Challenge**: *For every platform, identify posts whose engagement is significantly higher than the average engagement of that platform. A post is considered exceptional if its engagement is at least 2× the average engagement of its platform.*

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

#### Query Output Table:

| post_id | platform | post_engagement | platform_avg_engagement |
| ---: | ---: | ---: | ---: |
| ycjj5zzt7mvx | Instagram | 7,893 | 3,417.67 |
| wo7py9aljg3t | Reddit | 7,793 | 3,453.39 |
| gmoeib832zbs | Facebook | 7,764 | 3,456.55 |
| 5kvuyvf38nqx | YouTube | 7,755 | 3,453.37 |
| pvfl3d8hj7jd | Instagram | 7,738 | 3,417.67 |
| tdgjjylpua20 | UNKNOWN | 7,723 | 3,374.55 |
| tne7s3o4l4wd | Instagram | 7,712 | 3,417.67 |
| a1kiwl618kzy | Facebook | 7,683 | 3,456.55 |
| fp89q1ickn9w | Twitter | 7,628 | 3,345.93 |
| 5n161ir5hhhr | YouTube | 7,610 | 3,453.37 |

---

### H4 — Follower to Engagement Anomaly

**Challenge**: *Find users who have fewer than 5,000 followers but whose total post engagement places them among the top 10% of all users.*

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

#### Query Output Table:

| user_id | follower_count | location | total_engagement | engagement_percentile_pct |
| ---: | ---: | ---: | ---: | ---: |
| user_uerv85na | 1,824 | Rome, Italy | 71,836 | 99.73 |
| user_hdas0iau | 1,620 | Rio de Janeiro, Brazil | 66,500 | 99.47 |
| user_n0ok02rt | 2,531 | Dubai, UAE | 63,716 | 98.87 |
| user_fgjkkrie | 2,211 | Lyon, France | 62,690 | 98.80 |
| user_6wra58f7 | 4,953 | Johannesburg, South Africa | 55,557 | 96.73 |
| user_ogtvuuki | 4,459 | Cairo, Egypt | 55,128 | 96.26 |
| user_rr1uzkql | 1,069 | Milan, Italy | 54,817 | 96.06 |
| user_r7eg1rac | 2,052 | Houston, USA | 54,552 | 95.86 |
| user_5oe5t3js | 3,151 | London, UK | 53,170 | 94.86 |
| user_67hyf45u | 898 | Vancouver, Canada | 51,406 | 93.20 |

---

### H5 — Identify Data Anomalies (Corrupted Dataset)

**Challenge**: *Identify potentially corrupted posts where likes are negative, platform is missing, text content is missing, or text contains HTML entities/tags. Return post ID and anomaly type.*

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

#### Query Output Table:

| post_id | anomaly_type |
| ---: | ---: |
| 003s4ulm32tk | HTML Entities or Tags in Text |
| 005g54tmt26m | Negative Likes |
| 0066x8nnmouc | Missing Platform |
| 0066x8nnmouc | HTML Entities or Tags in Text |
| 00pk8aa72o8x | Missing Text Content |
| 00u9otx16xfc | Missing Platform |
| 014e8jqloj6h | Missing Text Content |
| 01gbk9id4v75 | Missing Text Content |
| 01kgwhi645er | Negative Likes |
| 01kgwhi645er | Missing Platform |
| 02b0vyoya4hz | Missing Platform |
| 02vdvvsovgsk | HTML Entities or Tags in Text |
| 030vdql1vwxl | HTML Entities or Tags in Text |
| 033i6hfsrdo8 | Missing Platform |
| 033i6hfsrdo8 | Missing Text Content |

---

### H6 — Find the Most Suspicious High Impact Users

**Challenge**: *Identify users who have < 10,000 followers, whose average post engagement is above overall average, and at least one post has more shares than likes. Rank by total engagement.*

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

#### Query Output Table:

| user_id | location | follower_count | post_count | avg_engagement | total_engagement | rank_by_total_engagement |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| user_uerv85na | Rome, Italy | 1,824 | 16 | 4,489.75 | 71,836 | 1 |
| user_hdas0iau | Rio de Janeiro, Brazil | 1,620 | 16 | 4,156.25 | 66,500 | 2 |
| user_68enpikx | Houston, USA | 9,364 | 15 | 4,326.93 | 64,904 | 3 |
| user_fgjkkrie | Lyon, France | 2,211 | 14 | 4,477.86 | 62,690 | 4 |
| user_9mtets0p | Johannesburg, South Africa | 8,262 | 14 | 4,458.14 | 62,414 | 5 |
| user_87kc1g6d | Houston, USA | 7,238 | 14 | 4,333.57 | 60,670 | 6 |
| user_g9g7onlw | Munich, Germany | 7,981 | 13 | 4,490.15 | 58,372 | 7 |
| user_cssz1rea | Tokyo, Japan | 7,863 | 14 | 4,144.21 | 58,019 | 8 |
| user_14ibkds2 | Singapore | 7,361 | 13 | 4,388 | 57,044 | 9 |
| user_ogtvuuki | Cairo, Egypt | 4,459 | 11 | 5,011.64 | 55,128 | 10 |

---
