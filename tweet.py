import re
import os
from configparser import ConfigParser
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import asyncio 
from twikit import Client, TooManyRequests
import httpx
import httpcore
from typing import Set, List, Optional, Tuple, Any

class Tweet:

    # def __init__(self, client):
    #     self.client = client

    async def login_to_twitter(self) -> Any:
        """
        Log in to Twitter using credentials stored in 'config.ini'.
        Returns:
            Any: An authenticated Twitter client instance.
        """
        config = ConfigParser()
        config.read('config.ini')
        username = config['X']['username']
        email = config['X']['email']
        password = config['X']['password']

        client = Client(language='en-US')
            
        if os.path.exists("cookies.json"):
            client.load_cookies("cookies.json")
        else:
            await client.login(auth_info_1=username, auth_info_2=email, password=password)
            client.save_cookies("cookies.json")
            
        return client
    

    async def get_tweets(self, client: Any, tweets: Optional[Any], total_scanned_tweets: int, query: str) -> Any:
        """
        Fetch tweets based on a query.

        Args:
            client (Any): The Twitter client instance.
            tweets (Optional[Any]): The current tweets or None for the initial request.
            total_scanned_tweets (int): Number of tweets scanned so far.
            query (str): Search query.

        Returns:
            Any: A list of tweets or the next page of tweets.
        """
        if tweets is None:
            print(f'{datetime.now()} - Getting tweets...')

            # user = await client.get_user_by_screen_name(user_name)
            # tweets = await user.get_tweets('Tweets')

            tweets = await client.search_tweet(query, product='Latest')
        else:
            wait_time = randint(5, 10)
            print(f'{datetime.now()} - Total scanned tweets: {total_scanned_tweets}')
            print(f'\033[93m{datetime.now()} - Getting next tweets after {wait_time} seconds ...\033[0m')
            # print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
            await asyncio.sleep(wait_time)
            tweets = await tweets.next()

        return tweets
    
    
    def print_summary(self, tweet_count: int, total_scanned_tweets: int, start_time: datetime) -> None:
        """
        Print a summary of the tweet scan process.

        Args:
            tweet_count (int): The number of tweets with addresses found.
            total_scanned_tweets (int): Total tweets scanned.
            start_time (datetime): Start time of the process.
        """
        end_time = datetime.now()
        duration = end_time - start_time
        summary = [
            f'Done! Got {tweet_count} tweets found',
            f'Total scanned tweets: {total_scanned_tweets}',
            f'Time taken: {duration}'
        ]

        max_length = max(len(line) for line in summary)

        print("\033[92m" + "#" * (max_length + 6) + "\033[0m")

        for line in summary:
            print(f"\033[92m#  {line.ljust(max_length)}  #\033[0m")

        print("\033[92m" + "#" * (max_length + 6) + "\033[0m")



    async def too_many_requests(self, error: Any) -> None:
        """
        Handle TooManyRequests error by calculating wait time and pausing execution.

        Args:
            error (Any): The rate limit error.
        """
        rate_limit_reset = datetime.fromtimestamp(error.rate_limit_reset)
        print(f"\033[91m{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}.\033[0m")
        retry_wait_time = (rate_limit_reset - datetime.now()).total_seconds()
        if retry_wait_time < 0:
            retry_wait_time = 0  
        await asyncio.sleep(retry_wait_time)


    # async def handle_request_errors(self, error: Exception) -> None:
    #     """
    #     Handle various request errors during API calls.

    #     Args:
    #         error (Exception): The exception encountered during a request.
    #     """
    #     retry_wait_time = 10  # Default retry wait time
    #     if isinstance(error, TooManyRequests):
    #         await self.too_many_requests(error)
    #     elif isinstance(error, (httpx.ConnectTimeout, httpcore.ConnectTimeout)):
    #         print(f"\033[91m{datetime.now()} - Connection timeout. Retrying in {retry_wait_time} seconds.\033[0m")
    #         await asyncio.sleep(retry_wait_time)
    #     elif isinstance(error, (httpx.RequestError, httpcore.HTTPError)):
    #         print(f"\033[91m{datetime.now()} - HTTP request error: {error}. Retrying.\033[0m")
    #         await asyncio.sleep(retry_wait_time)
    #     elif isinstance(error, httpx.HTTPStatusError):
    #         print(f"\033[91m{datetime.now()} - Server error: {error}. Retrying in {retry_wait_time} seconds.\033[0m")
    #         await asyncio.sleep(retry_wait_time)
    #     else:
    #         print(f"\033[91m{datetime.now()} - An unexpected error occurred: {error}. Retrying in {retry_wait_time} seconds.\033[0m")
    #         await asyncio.sleep(retry_wait_time)



    async def handle_request_errors(self, error: Exception) -> None:
        """
        Handle various request errors during API calls.

        Args:
            error (Exception): The exception encountered during a request.
        """
        retry_wait_time = 10  
        if isinstance(error, TooManyRequests):
            await self.too_many_requests(error)
        elif isinstance(error, (httpx.ConnectTimeout, httpx.ReadTimeout)):
            print(f"\033[91m{datetime.now()} - Connection timeout. Retrying in {retry_wait_time} seconds.\033[0m")
            await asyncio.sleep(retry_wait_time)
        elif isinstance(error, (httpx.RequestError, httpx.RemoteProtocolError)):
            print(f"\033[91m{datetime.now()} - HTTP request error: {error}. Retrying.\033[0m")
            await asyncio.sleep(retry_wait_time)
        elif isinstance(error, httpx.HTTPStatusError):
            print(f"\033[91m{datetime.now()} - Server error: {error}. Retrying in {retry_wait_time} seconds.\033[0m")
            await asyncio.sleep(retry_wait_time)
        else:
            print(f"\033[91m{datetime.now()} - An unexpected error occurred: {error}. Retrying in {retry_wait_time} seconds.\033[0m")
            await asyncio.sleep(retry_wait_time)


    # channel_parser

    def process_addresses_from_urls(self, urls: List[str], address_finder: Any) -> List[Tuple[str, str]]:
        """
        Process a list of URLs and extract all blockchain addresses.

        Args:
            urls (List[str]): A list of URLs to process.
            address_finder (Any): An object that can find blockchain addresses in text.

        Returns:
            List[Tuple[str, str]]: A list of found addresses with their types.
        """
        addresses = []
        for url in urls:
            addresses_in_url = address_finder.find_all_blockchain_addresses(url)
            if addresses_in_url:
                addresses.extend(addresses_in_url)
        return addresses


        # channel_discovery

    # def initialize_csv(self, filename: str):
    #     """Ensure the CSV file exists with headers."""
    #     if not os.path.exists(filename):
    #         with open(filename, 'w', newline='', encoding='utf-8') as coeff_file:
    #             coeff_writer = csv.writer(coeff_file)
    #             coeff_writer.writerow([
    #                 'user_screen_name',
    #                 'user_created_at',
    #                 'coef_tweets_with_addresses',
    #                 'coef_tweets_per_statuses_count',
    #                 'date_range_first_last_tweet',
    #                 'profile_url',
    #                 'location',
    #                 'default_profile',
    #                 'followers_count',
    #                 'media_count',
    #                 'statuses_count',
    #                 'withheld_in_countries',
    #                 'possibly_sensitive',
    #                 'user_id'
    #             ])

    # def get_processed_channels(self, filename: str) -> Set[str]:
    #     """Load already processed channels from the CSV."""
    #     if not os.path.exists(filename):
    #         return set()  # No file, so no channels processed
    #     with open(filename, 'r', encoding='utf-8') as coeff_file:
    #         coeff_reader = csv.DictReader(coeff_file)
    #         return {row['user_screen_name'] for row in coeff_reader}

    # async def fetch_user_details(self, client, channel: str):
    #     """Fetch user details for a channel."""
    #     user = await client.get_user_by_screen_name(channel)
    #     return {
    #         'user_id': user.id,
    #         'created_at': user.created_at,
    #         'screen_name': user.screen_name,
    #         'url': user.urls,
    #         'location': user.location,
    #         'default_profile': user.default_profile,
    #         'followers_count': user.followers_count,
    #         'media_count': user.media_count,
    #         'statuses_count': user.statuses_count,
    #         'withheld_in_countries': user.withheld_in_countries,
    #         'possibly_sensitive': user.possibly_sensitive,
    #     }
    


    def initialize_csv(self, filename: str):
        """Ensure the CSV file exists with headers."""
        if not os.path.exists(filename):
            with open(filename, 'w', newline='', encoding='utf-8') as coeff_file:
                coeff_writer = csv.writer(coeff_file)
                coeff_writer.writerow([
                    'channel',
                    'coefficient_tweets_with_addresses',
                    'user_created_at',
                    'screen_name',
                    'profile_url',
                    'location',
                    'default_profile',
                    'followers_count',
                    'media_count',
                    'date_range_first_last_tweet',
                    'statuses_count',
                    'withheld_in_countries',
                    'possibly_sensitive',
                    'coefficient_tweets_per_statuses_count'  
                ])

    def get_processed_channels(self, filename: str) -> Set[str]:
        """Load already processed channels from the CSV."""
        if not os.path.exists(filename):
            return set()  # No file, so no channels processed
        with open(filename, 'r', encoding='utf-8') as coeff_file:
            coeff_reader = csv.DictReader(coeff_file)
            return {row['channel'] for row in coeff_reader}

    async def fetch_user_details(self, client, channel: str):
        """Fetch user details for a channel."""
        user = await client.get_user_by_screen_name(channel)
        return {
            'created_at': user.created_at,
            'screen_name': user.screen_name,
            'url': user.urls,
            'location': user.location,
            'default_profile': user.default_profile,
            'followers_count': user.followers_count,
            'media_count': user.media_count,
            'statuses_count': user.statuses_count,
            'withheld_in_countries': user.withheld_in_countries,
            'possibly_sensitive': user.possibly_sensitive,
        }


