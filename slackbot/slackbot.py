'''
Reads tweets from PostgreSQL and reposts a tweet with a sentiment score >0 in Slack once an hour
'''
import requests
from sqlalchemy import create_engine
import os
import logging
import time

time.sleep(60)

# Save logs
log_slack = logging.getLogger('log_sack')
log_slack.addHandler(logging.FileHandler('logger_slack.log', mode='w'))
log_slack.setLevel(logging.INFO)
log_slack.info('Messages for logger slack:')

# Link to Slack channel
webhook_url = os.getenv('WEBHOOK_URL')

# Establish connection with PostgreSQL via Docker container pg_container
password = os.getenv('POSTGRES_PASSWORD')
user = os.getenv('POSTGRES_USER')
pg = create_engine('postgres://{}:{}@pg_container:5432/postgres'.format(user,password))

while True:
    '''Select a new tweet (status 1) with a sentiment higher than 0 (positive
     tweet)'''
    get_tweet_query = """SELECT * FROM tweets WHERE status = 1 AND sentiment > 0 LIMIT 1;"""

    # Extract a tweet
    tweet_selection = pg.execute(get_tweet_query)
    tweet = []
    for row in tweet_selection:
        tweet.append([row['id'], row['text'], row['sentiment']])

    tweet_id = tweet[0][0]
    tweet_text = tweet[0][1]
    sentiment = tweet[0][2]

    # Post the tweet in Slack
    data = {'text': tweet_text, 'sentiment': sentiment}
    requests.post(url=webhook_url, json = data)

    log_slack.info(tweet_text)

    # Set status 0 for the used tweet
    update_query = """UPDATE tweets SET status = 0 WHERE id = {}""".format(tweet_id)
    pg.execute(update_query)

    # Wait an hour until next tweet
    time.sleep(3600)