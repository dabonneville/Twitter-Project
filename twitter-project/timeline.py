"""
This file very much resembles stream.py. Polling 
should be used over streaming when following users. Currently,
the streaming API can return unwanted Tweets which cause rate limiting issues. To maximize
data collection (that is, to collect %100 of all followed users Tweets) set a crontab to run this
script at an interval appropriate to the number of your followers and their Tweeting frequency.

Last Updated 10/20/2013 M.Alam
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

from twython import Twython

import qactweet.util
import qactweet.sentiment

APP_KEY = ''
APP_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''

api = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

list_timeline = api.get_list_statuses(slug='', owner_screen_name='', count=n)

conn = MySQLdb.connect('host','user','password','database', charset='utf8',
                     use_unicode=True)
c = conn.cursor()

logger = logging.getLogger('Stream_Logger')
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

# Create a handler to write low-priority messages to a file.
handler = logging.FileHandler(filename='timeline.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

warnings.filterwarnings('ignore', category=MySQLdb.Warning)

htmlparser = HTMLParser.HTMLParser()

try:
    # UCS-4 build; Python 2.6.6 default on REHL 6 hosting this project.
    utf8mb4 = re.compile(u'[\U00010000-\U0010ffff]')
except re.error:
    # UCS-2 build; Python 2.7.5 compiled from source for this project.
    utf8mb4 = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')


for tweet in list_timeline:
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

        q = u'INSERT IGNORE INTO timeline VALUES (%s, %s, %s, %s, %s);'
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
                insert = (tweet['id'],(i['expanded_url']))
                c.execute(q, insert)
            except IOError:
                continue

        q = u'INSERT INTO user_mention VALUES (%s, %s, %s, %s);'
        for i in tweet['entities']['user_mentions']:
            insert = (tweet['id'], i['id'], i['screen_name'], i['name'])
            c.execute(q, insert)

conn.commit()