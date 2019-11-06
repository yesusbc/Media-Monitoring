#!/usr/bin/python3.6
try:
    import json
except ImportError:
    import simplejson as json

import tweepy
from credentials import ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET
from textblob import TextBlob

import pytz
import csv

import re

# Global Variables
TRACK_TERMS = ["KEYWORD1, #KEYWORD2"]
sentiment = ""
CVS_DEST_PATH = ""


# Writing our file headers
#with open('Sample.csv', mode='w') as tweetdata:
#    tweetdata_writer = csv.writer(tweetdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#    tweetdata_writer.writerow(['Location', 'Created At', 'Text', 'Sentiment', 'Polarity', 'subjectivity', 'Favs', 'Retweets', 'Tags', 'Nouns'])


# Defining users timezone
tz = pytz.timezone('US/Central')


# Setup tweepy to authenticate with Twitter credentials:
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)


# Create the api to connect to twitter with your creadentials
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True, compression=True)


class StreamListener(tweepy.StreamListener):

    # To remove retweets you can simply check whether the 'status' argument in on_status() method has the 'retweeted_status' attribute.
    def on_status(self, status):
        # Twitter
        loc = status.user.location
        created = tz.localize(status.created_at)
        text = status.text
        favs = status.favorite_count
        retweets = status.retweet_count

        # Textblob
        blob = TextBlob(text)
        tags = [tup[0] for tup in blob.tags if tup[1] == 'NNP' or tup[1] == 'JJS']      # tags = blob.tags
        tags += re.findall(r"#(\w+)", text)
        nouns = [re.sub('[!@#$]', '', noun) for noun in blob.noun_phrases]
        subjectivity = blob.sentiment.subjectivity
        polarity = blob.sentiment.polarity
        if polarity > 0:
            sentiment = "Positive"
        elif polarity <0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        with open(CVS_DEST_PATH, mode='a') as tweetdata:
            tweetdata_writer = csv.writer(tweetdata, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            tweetdata_writer.writerow([loc, created, text, sentiment, polarity, subjectivity, favs, retweets, tags, nouns])

        print(text)
        

    def on_error(self, status_code):
        if status_code == 401:
            print("Unauthorized")
        elif status_code == 406:
            print("Not Acceptable")
        elif status_code == 413:
            print("Too long")
        elif status_code == 416:
            print("Range Unacceptable")
        elif status_code == 420:
            print("Rate limited")
        elif status_code == 503:
            print("Service unavailable")
            return False

        
    def on_timeout(self):
        print("Connection Time out")
        return

    def on_disconnect(self, notice):
        print("disconnected")
        return



stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=TRACK_TERMS)

