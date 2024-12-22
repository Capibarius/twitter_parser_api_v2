from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from db_setup import TweetsData  

db_url = 'sqlite:///twitter.db'
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Количество строк в таблице
total_rows = session.query(func.count(TweetsData.id)).scalar()
print(f"Общее количество строк в БД: {total_rows}")

# Количество уникальных значений в столбце address
unique_addresses = session.query(func.count(func.distinct(TweetsData.address))).scalar()
print(f"Количество уникальных адресов: {unique_addresses}")

# Количество повторяющихся адресов
duplicate_addresses = (
    session.query(TweetsData.address)
    .group_by(TweetsData.address)
    .having(func.count(TweetsData.address) > 1)
    .count()
)
print(f"Количество адресов с повторениями: {duplicate_addresses}")

# Количество уникальных значений в столбце crypto_type
crypto_counts = (
    session.query(TweetsData.crypto_type, func.count(TweetsData.crypto_type))
    .group_by(TweetsData.crypto_type)
    .all()
)
print("Количество уникальных значений по crypto_type:")
for crypto_type, count in crypto_counts:
    print(f"  {crypto_type}: {count}")

# Количество строк с пустыми (NULL) значениями в столбце text
null_text_count = session.query(func.count()).filter(TweetsData.text == None).scalar()
print(f"Количество строк с пустым text: {null_text_count}")

# Адрес с наибольшим количеством упоминаний
most_frequent_address = (
    session.query(TweetsData.address, func.count(TweetsData.address).label("count"))
    .group_by(TweetsData.address)
    .order_by(func.count(TweetsData.address).desc())
    .first()
)
if most_frequent_address:
    print(
        f"Адрес с наибольшим количеством упоминаний: {most_frequent_address.address} ({most_frequent_address.count} раз)"
    )

# Самый ранний и самый поздний tweet
earliest_tweet = session.query(func.min(TweetsData.created_at)).scalar()
latest_tweet = session.query(func.max(TweetsData.created_at)).scalar()
print(f"Самый ранний tweet: {earliest_tweet}")
print(f"Самый поздний tweet: {latest_tweet}")

# Количество уникальных пользователей
unique_users = session.query(func.count(func.distinct(TweetsData.user_id))).scalar()
print(f"Количество уникальных пользователей: {unique_users}")

session.close()
