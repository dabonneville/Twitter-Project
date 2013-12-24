"""Write the members of a Twitter list to a CSV file.

The Twitter Streaming API requires user IDs rather than screen names as
track parameters. Twitter "lists" are useful for finding groups of people,
such as all Congress members on Twitter.

Since the Twitter Streaming API does not support list IDs as track
parameters, this script writes the user IDs, names, screen names, and
other specified paramaters of users from a Twitter list to a CSV file. These user IDs
can then be used as track parameters.

A quick script...

Changelog:
    salam 07/10/13 authored
    rpetchler 07/18/13 added docstring
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import tweepy
import csv


#OAuth reference https://dev.twitter.com/docs/api/1.1#102
consumer_key = ''
consumer_secret = ''
user_token = ''
user_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(user_token, user_secret)

api = tweepy.API(auth)

#write to a csv
with open('file.csv','w') as f:
    w=csv.writer(f)
    w.writerow(("User_Id","Name","Screen_Name","Followers_Count"))

    #from the members in the specified list
    for member in tweepy.Cursor(api.list_members,list_owner='',list_id='').items():
        w.writerow((member.id,member.screen_name,member.name,member.followers_count))


