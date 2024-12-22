import time
from datetime import datetime, timedelta
import csv
from configparser import ConfigParser
import asyncio
from twikit import Client, TooManyRequests
from tweet import Tweet
from regex_patterns import BlockchainAddressFinder
import os
from typing import Set, List, Optional, Tuple


# channels = ['SlowMist_Team', 'Phalcon_xyz', 'CertiKAlert', 'BeosinAlert', 'MistTrack_io', 
# '0xppl_', 'web3_watchdog', 'AegisWeb3', 'De_FiSecurity', 'quillaudits_ai', 'Deebs_DeFi', 
# 'mirrormirrorxyz', 'officer_cia', 'zachxbt', 'Phalcon_xyz', 'DecurityHQ', 'realScamSniffer', 
# 'DeBankDeFi', 'PeckShieldAlert', 'BlockSecTeam', 'MetaSleuth', 'HypernativeLabs', '0xleastwood']

channels = ['MetaSleuth', 'DeltaPrimeDefi', 'peckshield', 'wublockchain12', 'coinwaft']
            # , 'Phalcon_xyz', 'RDNTCapital']

TWEET_SCAN_LIMIT = 100

async def fetch_tweets(tweet_finder: Tweet, client, address_finder: BlockchainAddressFinder, channel: str) -> Tuple[int, int, List[datetime]]:
    """Fetch tweets and calculate statistics."""
    query = f'(from:{channel})'
    total_scanned_tweets = 0
    tweet_count_with_addresses = 0
    tweet_dates = []
    tweets = None

    while total_scanned_tweets < TWEET_SCAN_LIMIT:
        try:
            tweets = await tweet_finder.get_tweets(client, tweets, total_scanned_tweets, query)
        except Exception as e:
            await tweet_finder.handle_request_errors(e)
            continue

        if not tweets:
            break

        for tweet in tweets:
            total_scanned_tweets += 1
            tweet_dates.append(tweet.created_at_datetime)

            addresses = address_finder.find_all_blockchain_addresses(tweet.text)

            if not addresses:
                expanded_urls = [url['expanded_url'] for url in tweet.urls] if tweet.urls else []
                for url in expanded_urls:
                    addresses_in_url = address_finder.find_all_blockchain_addresses(url)
                    if addresses_in_url:
                        addresses.extend(addresses_in_url)

            if addresses:
                tweet_count_with_addresses += 1

        if total_scanned_tweets >= TWEET_SCAN_LIMIT:
            break

    return tweet_count_with_addresses, total_scanned_tweets, tweet_dates


async def process_channel(client, tweet_finder: Tweet, address_finder: BlockchainAddressFinder, channel: str, filename: str):
    """Process a single channel and save results to the CSV."""
    user_details = await tweet_finder.fetch_user_details(client, channel)
    addresses, scanned, dates = await fetch_tweets(tweet_finder, client, address_finder, channel)

    coefficient = (addresses / scanned) if scanned > 0 else 0
    if dates:
        first_date = min(dates)
        last_date = max(dates)
        duration = (last_date - first_date).days
    else:
        duration = "No tweets found"

    calculated_value = TWEET_SCAN_LIMIT / user_details['statuses_count'] if user_details['statuses_count'] > 0 else "N/A"

    with open(filename, 'a', newline='', encoding='utf-8') as coeff_file:
        coeff_writer = csv.writer(coeff_file)
        coeff_writer.writerow([
            channel,
            coefficient,
            user_details['created_at'],
            user_details['screen_name'],
            user_details['url'],
            user_details['location'],
            user_details['default_profile'],
            user_details['followers_count'],
            user_details['media_count'],
            duration,
            user_details['statuses_count'],
            user_details['withheld_in_countries'],
            user_details['possibly_sensitive'],
            calculated_value
        ])


async def main():
    filename = 'channel_coefficients.csv'
    tweet_finder = Tweet()
    address_finder = BlockchainAddressFinder()

    tweet_finder.initialize_csv(filename)
    processed_channels = tweet_finder.get_processed_channels(filename)

    client = await tweet_finder.login_to_twitter()

    for channel in channels:
        if channel in processed_channels:
            print(f"Skipping already processed channel: {channel}")
            continue

        print(f"Processing channel: {channel}")
        await process_channel(client, tweet_finder, address_finder, channel, filename)

    print("Processing completed.")


if __name__ == "__main__":
    asyncio.run(main())