CREATE DATABASE IF NOT EXISTS pixel-tailor;

USE pixel-tailor;

DROP TABLE IF EXISTS photos;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS lables;

CREATE TABLE users
(
    userid       int not null AUTO_INCREMENT,
    username     varchar(64) not null,
    password     varchar(256) not null,
    bucketfolder varchar(48) not null,  -- random, unique name (UUID)
    PRIMARY KEY  (userid),
    UNIQUE       (username)
);

ALTER TABLE users AUTO_INCREMENT = 80001;  -- starting value

CREATE TABLE photos
(
    photoid           int not null AUTO_INCREMENT,
    userid            int not null,
    original_name     varchar(256) not null,  -- original photo filename from user
    bucketkey         varchar(256) not null,  -- photo filename in S3 (bucketkey)
    PRIMARY KEY (photoid),
    FOREIGN KEY (userid) REFERENCES users(userid),
    UNIQUE      (bucketkey)
);

ALTER TABLE photos AUTO_INCREMENT = 10001;  -- starting value

CREATE TABLE lables
(
    lableid           int not null AUTO_INCREMENT,
    photoid           int not null,
    userid            int not null,
    labelname         varchar(256) not null,  -- cat or dog or...
    PRIMARY KEY (lableid),
    FOREIGN KEY (photoid) REFERENCES photos(photoid),
    FOREIGN KEY (userid) REFERENCES users(userid)
);

ALTER TABLE lables AUTO_INCREMENT = 101;  -- starting value




--
-- Insert some users to start with:
-- 
-- PWD hashing: https://phppasswordhash.com/
--
--INSERT INTO users(username, password)  -- pwd = abc123!!
--            values('p_sarkar', 'abc123!!');

--INSERT INTO users(username, password)  -- pwd = abc456!!
--            values('e_ricci', 'abc456!!');

--INSERT INTO users(username, password)  -- pwd = abc789!!
--            values('l_chen', 'abc789!!');

--
-- creating user accounts for database access:
--
-- ref: https://dev.mysql.com/doc/refman/8.0/en/create-user.html
--

DROP USER IF EXISTS 'pixel-tailor-read-only';
DROP USER IF EXISTS 'pixel-tailor-read-write';

CREATE USER 'pixel-tailor-read-only' IDENTIFIED BY 'abc123!!';
CREATE USER 'pixel-tailor-read-write' IDENTIFIED BY 'def456!!';

GRANT SELECT, SHOW VIEW ON pixel-tailor.* 
      TO 'pixel-tailor-read-only';
GRANT SELECT, SHOW VIEW, INSERT, UPDATE, DELETE, DROP, CREATE, ALTER ON pixel-tailor.* 
      TO 'pixel-tailor-read-write';
      
FLUSH PRIVILEGES;

--
-- done
--

