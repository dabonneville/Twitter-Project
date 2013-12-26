SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `db_name
--

-- --------------------------------------------------------

--
-- Table structure for table `geo`
--

CREATE TABLE IF NOT EXISTS `geo` (
  `status_id` bigint(20) unsigned NOT NULL,
  `coordinates` point NOT NULL,
  `fips` char(15) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`status_id`),
  KEY `ix_geo_status_id` (`status_id`),
  SPATIAL KEY `sx_geo_coordinates` (`coordinates`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hashtag`
--

CREATE TABLE IF NOT EXISTS `hashtag` (
  `status_id` bigint(20) unsigned NOT NULL,
  `hashtag` varchar(560) COLLATE utf8_unicode_ci NOT NULL,
  KEY `ix_hashtag_status_id` (`status_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `legislators`
--

CREATE TABLE IF NOT EXISTS `legislators` (
  `district` varchar(5) DEFAULT NULL,
  `first` varchar(13) DEFAULT NULL,
  `last` varchar(17) DEFAULT NULL,
  `id` int(4) DEFAULT NULL,
  `affiliation` int(1) DEFAULT NULL,
  `user_id` int(10) DEFAULT NULL,
  `screen_name` varchar(15) DEFAULT NULL,
  `chamber` int(1) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sentiment`
--

CREATE TABLE IF NOT EXISTS `sentiment` (
  `status_id` bigint(20) unsigned NOT NULL,
  `positive` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `negative` tinyint(2) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`status_id`),
  KEY `ix_sentiment_status_id` (`status_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `status`
--

CREATE TABLE IF NOT EXISTS `status` (
  `status_id` bigint(20) unsigned NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `text` varchar(560) COLLATE utf8_unicode_ci NOT NULL,
  `source` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`status_id`),
  KEY `ix_status_user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `timeline`
--

CREATE TABLE IF NOT EXISTS `timeline` (
  `status_id` bigint(20) unsigned NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `text` varchar(560) COLLATE utf8_unicode_ci NOT NULL,
  `source` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`status_id`),
  UNIQUE KEY `status_id` (`status_id`),
  KEY `ix_status_user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `url`
--

CREATE TABLE IF NOT EXISTS `url` (
  `status_id` bigint(20) unsigned NOT NULL,
  `url` varchar(560) COLLATE utf8_unicode_ci NOT NULL,
  KEY `ix_url_status_id` (`status_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `user_id` int(10) unsigned NOT NULL,
  `screen_name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(80) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `description` varchar(640) COLLATE utf8_unicode_ci DEFAULT NULL,
  `location` varchar(120) COLLATE utf8_unicode_ci DEFAULT NULL,
  `followers_count` bigint(20) unsigned DEFAULT NULL,
  `friends_count` bigint(20) unsigned DEFAULT NULL,
  `statuses_count` bigint(20) unsigned DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_mention`
--

CREATE TABLE IF NOT EXISTS `user_mention` (
  `status_id` bigint(20) unsigned NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `screen_name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(80) COLLATE utf8_unicode_ci NOT NULL,
  KEY `ix_user_mention_status_id` (`status_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
