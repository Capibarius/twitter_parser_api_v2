from sqlalchemy.orm import sessionmaker
from db_setup import TweetsData

# Проверка, существует ли твит в базе данных
def is_tweet_in_db(session, tweet_id):
    return session.query(TweetsData).filter_by(tweet_id=tweet_id).first() is not None

# Добавление твита в базу данных
def add_tweet_to_db(session, tweet_data):
    tweet = TweetsData(**tweet_data)
    session.add(tweet)
    session.commit()
