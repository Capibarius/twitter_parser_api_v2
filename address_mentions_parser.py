import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import asyncio 
from twikit import Client, TooManyRequests
from tweet import Tweet
from regex_patterns import BlockchainAddressFinder
from twikit.streaming import Topic
import os

MINIMUM_TWEETS = 100
QUERY = '0x111ceeee040739fd91d29c34c33e6b3e112f2177'

async def main():
    start_time = datetime.now()
    tweet_finder = Tweet()  
    client = await tweet_finder.login_to_twitter()

    # user_info = await client.user()
    # print(f"Logged in as {user_info}")

    tweet_count = 0  # Счетчик для твитов
    total_scanned_tweets = 0  # Счетчик для общего количества просканированных твитов
    tweets = None

    with open('tweets_ad.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['tweet_count', 'tweet_id', 'username', 'text', 'created_at', 'expanded_urls'])

    while tweet_count < MINIMUM_TWEETS:
        try:
            tweets = await tweet_finder.get_tweets(client, tweets, total_scanned_tweets, QUERY)
        except Exception as e:
            await tweet_finder.handle_request_errors(e)
            continue

        if not tweets:
            print(f'{datetime.now()} - No more tweets found')
            break

        for tweet in tweets:
            total_scanned_tweets += 1  
            tweet_count += 1  

            tweet_id = tweet.id
            username = tweet.user.name
            text = tweet.full_text
            created_at = tweet.created_at_datetime
            expanded_urls = ', '.join([url['expanded_url'] for url in tweet.urls]) if tweet.urls else ''

            tweet_data = [tweet_count, tweet_id, username, text, created_at, expanded_urls]

            with open('tweets_ad.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

            print(f'{datetime.now()} - Parsed tweet {tweet_count}')

    tweet_finder.print_summary(tweet_count, total_scanned_tweets, start_time)

if __name__ == "__main__":
    asyncio.run(main())