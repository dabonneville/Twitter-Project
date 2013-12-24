
"""Write the user_id's from a list of screen_names to a CSV file.

The Twitter Streaming API requires user IDs rather than screen_names as
track parameters. This script writes out user_id's and other specified paramaters
for a list of Twitter Handles to a CSV file.
See https://dev.twitter.com/docs/platform-objects/users for more infomation

A quick script...

Changelog:
    salam 07/20/13 authored
    
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import tweepy
import csv

def main():
        
#OAuth reference https://dev.twitter.com/docs/api/1.1#102
    consumer_key = ''
    consumer_secret = ''
    user_token = ''
    user_secret = ''

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(user_token, user_secret)
    
    api = tweepy.API(auth)
       
#from the screen_names in the list, write specified items to a CSV     
    lookup = api.lookup_users(screen_names=[''])
    with open('file.csv','w') as acsv:
        w=csv.writer(acsv)
        w.writerow(("User_Id","Screen_Name","User_Name"))
        for user in lookup: 
            w.writerow((user.id,user.screen_name,user.name))

if __name__ == "__main__":
    main()