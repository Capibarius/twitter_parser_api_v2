from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Таблица tweets_data
class TweetsData(Base):
    __tablename__ = 'tweets_data'

    id = Column(Integer, primary_key=True)  # Используем id как первичный ключ
    source = Column(String(255))
    user_id = Column(String(255))
    username = Column(String(255))
    tweet_id = Column(String(255))
    url = Column(String(255))
    created_at = Column(DateTime)
    text = Column(Text)
    expanded_urls = Column(Text)
    quote_tweet = Column(String(255))
    retweeted_tweet = Column(String(255))
    media = Column(Text)
    related_tweets = Column(Text)
    crypto_type = Column(String(255))
    address = Column(String(255))

# Таблица channel_coefficients
class ChannelCoefficients(Base):
    __tablename__ = 'channel_coefficients'

    id = Column(Integer, primary_key=True)  # Используем id как первичный ключ
    channel = Column(String(255))
    coefficient_tweets_with_addresses = Column(Float)
    user_created_at = Column(DateTime)
    screen_name = Column(String(255))
    profile_url = Column(String(255))
    location = Column(String(255))
    default_profile = Column(Boolean)
    followers_count = Column(Integer)
    media_count = Column(Integer)
    date_range_first_last_tweet = Column(String(255))
    statuses_count = Column(Integer)
    withheld_in_countries = Column(String(255))
    possibly_sensitive = Column(Boolean)
    coefficient_tweets_per_statuses_count = Column(Float)

# Таблица channel_followers
class ChannelFollowers(Base):
    __tablename__ = 'channel_followers'

    id = Column(Integer, primary_key=True)  # Первичный ключ
    channel_name = Column(String(255))  # Имя канала
    channel_id = Column(String(255))  # ID канала
    followers_count = Column(Integer)  # Количество подписчиков
    followers_list = Column(Text)  # Список всех подписчиков в виде строки (например, JSON)

# Таблица continuous_parsing_channels
class ContinuousParsingChannels(Base):
    __tablename__ = 'continuous_parsing_channels'

    id = Column(Integer, primary_key=True)  # Первичный ключ
    channel_name = Column(String(255))  # Имя канала
    channel_id = Column(String(255))  # ID канала
    coefficient_tweets_with_addresses = Column(Float)
    user_created_at = Column(DateTime)
    screen_name = Column(String(255))
    media_count = Column(Integer)
    date_range_first_last_tweet = Column(String(255))
    statuses_count = Column(Integer)
    coefficient_tweets_per_statuses_count = Column(Float)
    should_parse = Column(Boolean)  # 1 - парсить, 0 - не парсить

def connect_to_database(db_url='sqlite:///twitter.db'):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

def create_database(db_url='sqlite:///twitter.db'):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

session = create_database()

session.close()
