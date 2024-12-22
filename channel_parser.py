
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

# now = 
QUERY = '(from:peckshield) lang:en until:2024-12-07 since:2018-01-01'
# # user_names = ['SlowMist_Team', AnciliaInc, BeosinAlert,CertiKAlert, MistTrack_io
# , 0xppl_, quillaudits_ai, DecurityHQ, realScamSniffer, MetaSleuth, De_FiSecurity] Phalcon_xyz

MINIMUM_TWEETS = 3

async def main():
    start_time = datetime.now()
    tweet_finder = Tweet() 
    address_finder = BlockchainAddressFinder()
    client = await tweet_finder.login_to_twitter()

    tweet_count = 0  # Счетчик для твитов с адресами 
    total_scanned_tweets = 0  # Счетчик для общего количества просканированных твитов
    tweets = None

    with open('tweets.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'tweet_count', 'source', 'user_id', 'username', 'tweet_id', 'url', 
            'created_at', 'text', 'expanded_urls', 'quote_tweet', 
            'retweeted_tweet', 'media', 'related_tweets', 'crypto_type', 'address'
        ])

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

            addresses = address_finder.find_all_blockchain_addresses(tweet.text)

            expanded_urls = [url['expanded_url'] for url in tweet.urls] if tweet.urls else []
            # Логика для обработки адресов из ссылок
            url_addresses = tweet_finder.process_addresses_from_urls(expanded_urls, address_finder)

            addresses.extend(url_addresses)

            if addresses:
                tweet_count += 1

                tweet_url = f"https://x.com/{tweet.user.screen_name}/status/{tweet.id}"
                source = "Twitter"
                quote_tweet = tweet.quote if hasattr(tweet, 'quote') else None
                retweeted_tweet = tweet.retweeted_tweet if hasattr(tweet, 'retweeted_tweet') else None
                media = ', '.join([m['url'] for m in tweet.media]) if hasattr(tweet, 'media') and tweet.media else None
                related_tweets = ', '.join([str(rt.id) for rt in tweet.related_tweets]) if hasattr(tweet, 'related_tweets') and tweet.related_tweets else None

                for address, crypto_type in addresses:
                    tweet_data = [
                        tweet_count, source, tweet.user.id, tweet.user.screen_name, tweet.id, 
                        tweet_url, tweet.created_at_datetime, tweet.full_text, ', '.join(expanded_urls), 
                        quote_tweet, retweeted_tweet, media, related_tweets, crypto_type, address
                    ]

                    with open('tweets.csv', 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(tweet_data)

                print(f'{datetime.now()} - Found addresses in tweet {tweet_count}')

    tweet_finder.print_summary(tweet_count, total_scanned_tweets, start_time)



if __name__ == "__main__":
    asyncio.run(main())