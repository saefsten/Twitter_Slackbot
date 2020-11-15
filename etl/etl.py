'''
ETL - Extract, Transform, Load
* Extracts tweets from MongoDB
* Cleans them (removes URLs, "RT :" for retweets and "@username")
* Uses Vader for a sentiment analysis
* The cleaned tweet is saved with it's sentiment score and status 1 in PostgreSQL
* The processed tweets recieves status 'done' in MongoDB
'''
import pymongo
from sqlalchemy import create_engine
import time
import logging
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

time.sleep(10)

# Save logs
log_etl = logging.getLogger('log_etl')
log_etl.addHandler(logging.FileHandler('logger_etl.log', mode='w'))
log_etl.setLevel(logging.INFO)
log_etl.info('Messages for logger etl:')

# Establish connection with PostgreSQL via Docker container pg_container
password = os.getenv('POSTGRES_PASSWORD')
user = os.getenv('POSTGRES_USER')
pg = create_engine('postgres://{}:{}@pg_container:5432/postgres'.format(user,password))

create_query = """
CREATE TABLE IF NOT EXISTS tweets (
    id INTEGER,
    text TEXT,
    sentiment FLOAT,
    status INTEGER
);
"""
pg.execute(create_query)

# Establish connection with the MongoDB via the Docker container mdb_container
client = pymongo.MongoClient('mdb_container')
db = client.tweets_mdb
collection = db.collection

# Create sentiment analyzer
s = SentimentIntensityAnalyzer()

# Tweet counter
tweet_nr = 0

while True:
    # Find a new tweet in MongoDB and clean it
    tweet = collection.find_one({'status':'new'})
    if tweet == None:
        time.sleep(20)
        continue
    else:
        clean_tweet = re.sub(r"@[A-Za-z0-9]+|\A(RT\s:)|https?:\S+","", tweet['text'])
        log_etl.info(clean_tweet)

        # Sentiment analysis with Vader
        sentiment_score = s.polarity_scores(clean_tweet)
        compound = sentiment_score['compound']

        # Insert tweet into PostgreSQL
        tweet_nr += 1
        insert_query = "INSERT INTO tweets VALUES (%s,%s,%s,1);"
        pg.execute(insert_query,(tweet_nr,clean_tweet,compound))

        # Mark the entry from MongoDB as 'done'
        id_filter = {'_id':tweet['_id']}
        status_done = {"$set" : {'status':'done'}}
        collection.update_one(id_filter,status_done)