import asyncio
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from db_setup import connect_to_database, TweetsData
from db_operations import add_tweet_to_db, is_tweet_in_db
from twikit import TooManyRequests
from tweet import Tweet
from regex_patterns import BlockchainAddressFinder

QUERY_TEMPLATE = "(from:{channel})"
# QUERY_TEMPLATE = "(from:{channel}) lang:en until:2024-12-07 since:2018-01-01"

MINIMUM_TWEETS = 100
CHANNELS = ['PeckShieldAlert', 'SlowMist_Team']  

async def main():
    Session = connect_to_database()
    session = Session()

    start_time = datetime.now()
    tweet_finder = Tweet()
    address_finder = BlockchainAddressFinder()
    client = await tweet_finder.login_to_twitter()

    parsed_tweets_with_addresses = 0
    total_scanned_tweets = 0

    for channel in CHANNELS:
        print(f"Fetching tweets from channel: {channel}")
        tweet_count = 0
        total_skip_count = 0  # Счетчик пропусков для текущего канала
        tweets = None
        query = QUERY_TEMPLATE.format(channel=channel)

        while tweet_count < MINIMUM_TWEETS:
            try:
                tweets = await tweet_finder.get_tweets(client, tweets, total_scanned_tweets, query)
            except Exception as e:
                await tweet_finder.handle_request_errors(e)
                continue

            if not tweets:
                print(f'{datetime.now()} - No more tweets found for channel {channel}')
                break

            # Собираем список tweet_id для проверки
            tweet_ids = [tweet.id for tweet in tweets]
            existing_tweets = {t.tweet_id for t in session.query(TweetsData).filter(TweetsData.tweet_id.in_(tweet_ids)).all()}

            for tweet in tweets:
                total_scanned_tweets += 1

                if tweet.id in existing_tweets:
                    print(f"Tweet {tweet.id} already in DB, skipping...")
                    total_skip_count += 1
                    if total_skip_count > 2:
                        print(f"{datetime.now()} - Too many skips for channel {channel}. Moving to next channel.")
                        break
                    continue

                # Обнуляем счетчик при успешной обработке твита
                total_skip_count = 0

                addresses = address_finder.find_all_blockchain_addresses(tweet.text)
                expanded_urls = [url['expanded_url'] for url in tweet.urls] if tweet.urls else []
                url_addresses = tweet_finder.process_addresses_from_urls(expanded_urls, address_finder)
                addresses.extend(url_addresses)

                if addresses:
                    tweet_count += 1
                    parsed_tweets_with_addresses += 1

                    for address, crypto_type in addresses:
                        tweet_data = {
                            'source': 'Twitter',
                            'user_id': tweet.user.id,
                            'username': tweet.user.screen_name,
                            'tweet_id': tweet.id,
                            'url': f"https://x.com/{tweet.user.screen_name}/status/{tweet.id}",
                            'created_at': tweet.created_at_datetime,
                            'text': tweet.full_text,
                            'expanded_urls': ', '.join(expanded_urls),
                            'quote_tweet': str(getattr(tweet, 'quote', None)) if getattr(tweet, 'quote', None) else None,
                            'retweeted_tweet': str(getattr(tweet, 'retweeted_tweet', None)) if getattr(tweet, 'retweeted_tweet', None) else None,
                            'media': ', '.join([m['url'] for m in tweet.media]) if hasattr(tweet, 'media') and tweet.media else None,
                            'related_tweets': ', '.join([str(rt.id) for rt in tweet.related_tweets]) if hasattr(tweet, 'related_tweets') and tweet.related_tweets else None,
                            'crypto_type': crypto_type,
                            'address': address,
                        }
                        add_tweet_to_db(session, tweet_data)
                        print(f"{datetime.now()} - Added tweet {tweet.id} with address {address} to DB")


            if total_skip_count > 2:
                break  

            if tweet_count == 0:
                print(f"No new tweets with addresses found for channel {channel}")
                break


    tweet_finder.print_summary(parsed_tweets_with_addresses, total_scanned_tweets, start_time)
    session.close()

if __name__ == "__main__":
    asyncio.run(main())
