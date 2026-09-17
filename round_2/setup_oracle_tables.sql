SET ECHO ON;
SET FEEDBACK ON;

CREATE OR REPLACE DIRECTORY datavortex_dir AS 'C:\app\patha\datavortex';
GRANT READ, WRITE ON DIRECTORY datavortex_dir TO PUBLIC;

-- Drop previous tables if existing
BEGIN EXECUTE IMMEDIATE 'DROP TABLE posts CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE posts_ext CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE users CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE users_ext CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE posts_corrupted CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE posts_corr_ext CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

-- 1. POSTS TABLE (Cleaned)
CREATE TABLE posts_ext (
    post_id        VARCHAR2(50),
    user_id        VARCHAR2(50),
    platform       VARCHAR2(50),
    text_content   VARCHAR2(4000),
    timestamp      VARCHAR2(50),
    likes          NUMBER,
    shares         NUMBER,
    comments       NUMBER,
    timestamp_utc  VARCHAR2(50),
    likes_cleaned  NUMBER,
    likes_imputed  VARCHAR2(20)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY datavortex_dir
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY NEWLINE
        SKIP 1
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
    )
    LOCATION ('Social_Engine_Posts_Cleaned.csv')
)
REJECT LIMIT UNLIMITED;

CREATE TABLE posts AS SELECT * FROM posts_ext;
DROP TABLE posts_ext;


-- 2. USERS TABLE
CREATE TABLE users_ext (
    user_id          VARCHAR2(50),
    location         VARCHAR2(100),
    language         VARCHAR2(20),
    account_created  VARCHAR2(50),
    follower_count   NUMBER,
    city             VARCHAR2(50),
    country          VARCHAR2(50)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY datavortex_dir
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY NEWLINE
        SKIP 1
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
    )
    LOCATION ('Social_Engine_Users_Cleaned.csv')
)
REJECT LIMIT UNLIMITED;

CREATE TABLE users AS SELECT * FROM users_ext;
DROP TABLE users_ext;


-- 3. CORRUPTED POSTS TABLE
CREATE TABLE posts_corr_ext (
    post_id       VARCHAR2(50),
    user_id       VARCHAR2(50),
    platform      VARCHAR2(50),
    text_content  VARCHAR2(4000),
    timestamp     VARCHAR2(50),
    likes         NUMBER,
    shares        NUMBER,
    comments      NUMBER
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY datavortex_dir
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0A'
        SKIP 1
        FIELDS TERMINATED BY ','
        OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
    )
    LOCATION ('Social_Engine_Posts_Corrupted.csv')
)
REJECT LIMIT UNLIMITED;

CREATE TABLE posts_corrupted AS SELECT * FROM posts_corr_ext;
DROP TABLE posts_corr_ext;

PROMPT ==============================================================================
PROMPT TABLES SUCCESSFULLY CREATED:
PROMPT ==============================================================================
SELECT 'posts' AS table_name, COUNT(*) AS row_count FROM posts
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'posts_corrupted', COUNT(*) FROM posts_corrupted;

COMMIT;
