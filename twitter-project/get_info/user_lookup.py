""" 
A quick script for user lookup. 

"""
from twython import Twython
import csv
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
       
#from the screen_names in the list, write the specified items to a CSV     
    screen_names=('')
    lookup = api.lookup_users(screen_names=screen_names)
    with open('file.csv','w') as acsv:
        w=csv.writer(acsv)
        w.writerow(("User_Id","Screen_Name","User_Name"))
        for user in lookup: 
            w.writerow((user.id,user.screen_name,user.name))

if __name__ == "__main__":
    main()
