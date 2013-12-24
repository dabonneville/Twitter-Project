"""
This script can be used to collect the 3,200 most recent tweets of a user. As the 
Twitter API will only go back about 3-5 days, this is useful for recovering data or 
accessing older data for a specific set of users. Because of the limitations of the 
get_list_timeline method, we must create a list(s) of user screen_names and loop through each
to retrieve their individiual timeline. 

If you receive a 404 error "Sorry this page does not exist", this likely means one of the screen_names
in your list is not valid or no longer exists. If this happens, use the user_lookup script to retrieve
a list of only valid screen_names on your list.

Last Updated: M.Alam, 26 Oct 2013
"""
from twython import Twython
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



APP_KEY = ""
APP_SECRET = ""
OAUTH_TOKEN = ""
OAUTH_TOKEN_SECRET = ""

api = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

user_timeline = []

screen_names_list = ['']
for i in range(0,len(screen_names_list)):
    user_timeline.append(api.get_user_timeline(screen_name=screen_names_list[i],count='450',max_id='',since_id=''))

conn = MySQLdb.connect('host','user','password','database', charset='utf8',
                     use_unicode=True)
c = conn.cursor()

warnings.filterwarnings('ignore', category=MySQLdb.Warning)

htmlparser = HTMLParser.HTMLParser()

try:
    # UCS-4 build; Python 2.6.6 default on REHL 6 hosting this project.
    utf8mb4 = re.compile(u'[\U00010000-\U0010ffff]')
except re.error:
    # UCS-2 build; Python 2.7.5 compiled from source for this project.
    utf8mb4 = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')


    for i in range(0,len(user_timeline)):
        for tweet in user_timeline[i]:
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

	        q = u'INSERT IGNORE INTO sentiment VALUES (%s, %s, %s);'
	        bag_of_words = qactweet.sentiment.preprocess(tweet['text'])
	        p, n = qactweet.sentiment.score(bag_of_words,
	                   qactweet.sentiment.positive_words,
	                   qactweet.sentiment.negative_words)
	        c.execute(q, (tweet['id'], p, n))
            
conn.commit()