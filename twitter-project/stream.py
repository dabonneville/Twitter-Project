"""
Consume and process Tweets from the Streaming API.
Authored: rpetchler 

"""


import HTMLParser
import json
import logging
import logging.handlers
import Queue
import re
import socket
import threading
import time
import urllib
import warnings

import MySQLdb
import requests
import tweepy

import qactweet.geo
import qactweet.sentiment
import qactweet.util


with open('parameters.json') as f:
    p = json.load(f)


logger = logging.getLogger('Stream_Logger')
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

# Create a handler to write low-priority messages to a file.
handler = logging.FileHandler(filename='stream.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Define a handler to send high-priority messages via email.
handler = logging.handlers.SMTPHandler(
              mailhost='smtp.mail.yahoo.com',
              fromaddr=p['email']['username'],
              toaddrs=p['email']['recipients'],
              credentials=(p['email']['username'], p['email']['password']),
              subject='Stream Aborted')
handler.setLevel(logging.CRITICAL)
handler.setFormatter(formatter)
logger.addHandler(handler)


conn = MySQLdb.connect(host=p['mysql']['host'],
                       user=p['mysql']['user'],
                       passwd=p['mysql']['passwd'],
                       db=p['mysql']['db'],
                       charset='utf8')
c = conn.cursor()

warnings.filterwarnings('ignore', category=MySQLdb.Warning)

# Versions of MySQL prior to 5.5 cannot store UTF-8 characters containing
# four bytes. This regular expression contains the four-byte characters
# that must be removed before inserting strings to MySQL.
# Adapted from: http://stackoverflow.com/a/12636588
# See also: http://dev.mysql.com/doc/refman/5.5/en/charset-unicode.html
try:
    # UCS-4 build; Python 2.6.6 default on REHL 6 hosting this project.
    utf8mb4 = re.compile(u'[\U00010000-\U0010ffff]')
except re.error:
    # UCS-2 build; Python 2.7.5 compiled from source for this project.
    utf8mb4 = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')


# A queue to pass Tweets between the stream and reverse geocoder.
queue = Queue.Queue()

# HTML parser for unescaping HTML character entities in strings.
# Adapted from: http://stackoverflow.com/a/2087433
htmlparser = HTMLParser.HTMLParser()

# Add to the tweepy.models.Status class an instance variable containing
# the raw Tweet JSON, including Unicode characters.
@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    status.json = json.dumps(raw, ensure_ascii=False)
    return status

tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse


class ThreadedReverseGeocoder(threading.Thread):
    """A threaded reverse geocoder for Tweets.

    Attributes:
        queue: The global queue instance that the Listener and
            ThreadedReverseGeocoder use to share data.
        conn, c: Thread-specific MySQL connection and cursor because
            threads cannot share connections.
    """

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.conn = MySQLdb.connect(host=p['mysql']['host'],
                                    user=p['mysql']['user'],
                                    passwd=p['mysql']['passwd'],
                                    db=p['mysql']['db'],
                                    charset='utf8')
        self.c = self.conn.cursor()

    def run(self):
        while True:
            time.sleep(1)
            status_id, lon, lat = self.queue.get()
            fips = qactweet.geo.reverse_geocode(lon, lat)

            q = u'INSERT IGNORE INTO geo VALUES (%s, POINT(%s, %s), %s);'
            self.c.execute(q, (status_id, lon, lat, fips))

            self.conn.commit()
            self.queue.task_done()


class Listener(tweepy.StreamListener):
    """Consumes Tweets from the Twitter Streaming API.

    This class overrides the default methods of the tweepy.StreamListener
    class in order to clean Tweets and write them to MySQL.
    """

    def on_status(self, tweet):
        """Insert Tweet into MySQL."""
        tweet = utf8mb4.sub(u'', tweet.json)
        tweet = json.loads(tweet)

        tweet['created_at'] = qactweet.util.isoformat(tweet['created_at'])
        tweet['text'] = htmlparser.unescape(tweet['text'])
        tweet['source'] = qactweet.util.strip_tags(tweet['source'])
        q = u'INSERT IGNORE INTO status VALUES (%s, %s, %s, %s, %s);'
        insert = (tweet['id'],
                  tweet['user']['id'],
                  tweet['created_at'],
                  tweet['text'],
                  tweet['source'])
        c.execute(q, insert)

        user = tweet['user']
        user['created_at'] = qactweet.util.isoformat(user['created_at'])
        user['description'] = htmlparser.unescape(user['description'])
        q = u'INSERT IGNORE INTO user VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'
        insert = (user['id'],
                  user['screen_name'],
                  user['name'],
                  user['created_at'],
                  user['description'],
                  user['location'],
                  user['followers_count'],
                  user['friends_count'],
                  user['statuses_count'])

        c.execute(q, insert)

        q = u'INSERT INTO hashtag VALUES (%s, %s);'
        for i in tweet['entities']['hashtags']:
            c.execute(q, (tweet['id'], i['text']))

        q = u'INSERT INTO url VALUES (%s, %s);'
        for i in tweet['entities']['urls']:
            try:
                insert = (tweet['id'],
                          qactweet.util.unshorten(i['expanded_url']))
                c.execute(q, insert)
            except IOError:
                continue

        q = u'INSERT INTO user_mention VALUES (%s, %s, %s, %s);'
        for i in tweet['entities']['user_mentions']:
            insert = (tweet['id'], i['id'], i['screen_name'], i['name'])
            c.execute(q, insert)

        # Pass Tweet geodata to the reverse geocoder.
        if tweet['coordinates']:
            lon, lat = tweet['coordinates']['coordinates']
            queue.put((tweet['id'], lon, lat))
        elif tweet['user']['location']:
            lon, lat = qactweet.geo.parse_location(tweet['user']['location'])
            if lon is not None:
                queue.put((tweet['id'], lon, lat))
        else:
            pass

        # Sentiment analysis.
        q = u'INSERT IGNORE INTO sentiment VALUES (%s, %s, %s);'
        bag_of_words = qactweet.sentiment.preprocess(tweet['text'])
        p, n = qactweet.sentiment.score(bag_of_words,
                   qactweet.sentiment.positive_words,
                   qactweet.sentiment.negative_words)
        c.execute(q, (tweet['id'], p, n))

        conn.commit()

    def on_error(self, status_code):
        """Raise errors that occur."""
        raise tweepy.error.TweepError(status_code)


class ErrorHandler(object):
    """Handles errors raised by the Twitter Streaming API.

    This class contains methods to handle various types of errors that
    may occur while connecting to the Streaming API. Each method
    sleeps, logs the error, and increments the error count. The sleep
    durations and error count are reset if the last error occurred more
    than 60 minutes ago.

    See also: https://dev.twitter.com/docs/streaming-apis/connecting

    Attributes:
        sleep_{rate_limit, http_error, network_error, db_error}:
            Seconds to sleep before retrying the API connection.
        error_count: Number of errors that have occurred.
        time_of_last_error: The Unix time when the last error occurred.
    """

    def __init__(self):
        """Initializes class with default parameter values."""
        self._reset()

    def _reset(self):
        """Reset class parameters to default values."""
        self.sleep_rate_limit = 60
        self.sleep_http_error = 5
        self.sleep_network_error = .25
        self.sleep_db_error = .25
        self.error_count = 0
        self.time_of_last_error = time.time()

    def _decorator(func):
        """Reset (if necessary) and increment class parameters."""
        def wrapper(self, *args):
            if time.time() - self.time_of_last_error > 60 * 60:
                self._reset()  # No errors occured in the past 60 minutes.
            func(self, *args)
            self.error_count += 1
            self.time_of_last_error = time.time()
        return wrapper

    @_decorator
    def rate_limit(self, status_code):
        msg = 'HTTP error, status code {}. Retrying in {} seconds.'
        msg = msg.format(status_code, self.sleep_rate_limit)
        logger.error(msg)
        time.sleep(self.sleep_rate_limit)
        self.sleep_rate_limit *= 2

    @_decorator
    def http_error(self, status_code):
        msg = 'HTTP error, status code {}. Retrying in {} seconds.'
        msg = msg.format(status_code, self.sleep_http_error)
        logger.error(msg)
        time.sleep(self.sleep_http_error)
        self.sleep_http_error = min(self.sleep_http_error * 2, 320)

    @_decorator
    def network_error(self):
        msg = 'TCP/IP error. Retrying in {} seconds.'
        msg = msg.format(self.sleep_network_error)
        logger.error(msg)
        time.sleep(self.sleep_network_error)
        self.sleep_network_error = min(self.sleep_network_error + 1, 16)

    @_decorator
    def db_error(self):
        msg = 'Database error. Retrying in {} seconds.'
        msg = msg.format(self.sleep_db_error)
        logger.error(msg)
        time.sleep(self.sleep_db_error)  # Sleep time remains constant.


def main():

    # Create a pool of reverse geocoder threads. Pass the queue to each.
    # For now, use a single thread to prevent abusing the geocoding API.
    for i in range(1):
        t = ThreadedReverseGeocoder(queue)
        t.start()

    auth = tweepy.OAuthHandler(p['twitter']['consumer_key'],
                               p['twitter']['consumer_secret'])
    auth.set_access_token(p['twitter']['access_token'],
                          p['twitter']['access_token_secret'])

    error_handler = ErrorHandler()
    while True:
        try:
            stream = tweepy.Stream(auth, Listener(), timeout=None)
            stream.filter(p['twitter']['follow'], p['twitter']['track'])
        except Exception as e:
            if error_handler.error_count > 10:
                logger.critical('Exceeded 10 errors. Aborted.')
                break
            if isinstance(e, tweepy.error.TweepError) and (e.args[0] == 420 or e.args[0] >= 500):
                error_handler.rate_limit(e.args[0])
            elif isinstance(e, tweepy.error.TweepError):
                error_handler.http_error(e.args[0])
            elif isinstance(e, socket.error):
                error_handler.network_error()
            elif isinstance(e, MySQLdb.MySQLError):
                error_handler.db_error()
            #else:
            #    raise e

    queue.join()  # Block until all tasks finish.
    conn.close()
    logger.critical('Finished.')
    logging.shutdown()


if __name__ == '__main__':
    main()


