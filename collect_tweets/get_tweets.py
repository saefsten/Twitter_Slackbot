'''
Streas tweets from Twitter and saves these inside a MongoDB
'''

from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json
import logging
import pymongo
import time
import os

# Save logs
log_gt = logging.getLogger('log_gt')
log_gt.addHandler(logging.FileHandler('logger_gt.log', mode='w'))
log_gt.setLevel(logging.INFO)
log_gt.info('Messages for logger get_tweets:')

# Establish connection with the MongoDB via the Docker container mdb_container
client = pymongo.MongoClient(host='mdb_container', port=27017)
db = client.tweets_mdb
collection = db.tweet_collection


def authenticate():

    auth = OAuthHandler(os.getenv('CONSUMER_API_KEY'), os.getenv('CONSUMER_API_SECRET'))
    auth.set_access_token(os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET'))

    return auth

class TwitterListener(StreamListener):
    '''Collects tweets fro Twitter and inserts them in a MongoDB'''

    def on_data(self, data):

        t = json.loads(data)

        tweet = {
        'text': t['text'],
        'username': t['user']['screen_name'],
        'followers_count': t['user']['followers_count'],
        'status' : 'new'
        }
        
        db.collection.insert_one(tweet)
        log_gt.critical(tweet)


    def on_error(self, status):

        if status == 420:
            print(status)
            return False

if __name__ == '__main__':
    '''Streas tweets about Sweden'''

    auth = authenticate()
    listener = TwitterListener()
    stream = Stream(auth, listener)
    stream.filter(track=['sweden'], languages=['en'])