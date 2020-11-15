# Twitter_Slackbot
Tweets are collected from Twitter and reposted in Slack via a Slackbot

In this process Docker is used, in total five containers
* Tweet container to collect tweets
* MongoDB to store the raw tweets
* ETL for processing them and sending them to PostgreSQL
* PostgreSQL
* The Slackbot
