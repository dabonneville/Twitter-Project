"""
A quick script to create a list and add multiple members to a list (~90 at a time!).
Authored on 6 Aug 2013, M.Alam

"""
from twython import Twython, TwythonError

APP_KEY = ""
APP_SECRET = ""
OAUTH_TOKEN = ""
OAUTH_TOKEN_SECRET = ""

# Requires Authentication as of Twitter API v1.1
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

#Comma separated list of screen_names
screen_names=['']

#If not creating a list, obtain list_id for existing list
#qaclist_id=[]

'''try:
    create_list=twitter.create_list(name='')
    qaclist_id=create_list['id_str']
except TwythonError as e:
    print e'''

#the above should be commented out if you are simply updating list members.
try:
    update_list = twitter.create_list_members(list_id=,screen_name=screen_names)
except TwythonError as e:
    print e
