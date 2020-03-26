import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#db.execute("INSERT INTO practice.reviews (review, book_id, user_id) VALUES (:review, :book_id, :user_id)",cd
#{"review": review, "book_id": book, "user_id": session["user_id"]})
user_reviews = db.execute("SELECT to_char(practice.reviews.timestamp, 'HH12:MI:SS, DD Mon YYYY'), practice.reviews.review, practice.reviews.score, practice.reviews.user_id, practice.reviews.book_id, practice.users.username FROM practice.reviews, practice.users WHERE practice.users.id = practice.reviews.user_id AND practice.reviews.book_id = :id", {"id": '6844'}).fetchall()
for data in user_reviews:
    print('===' + data['username'] + '===')
    print(data['review'])
    print(data['to_char'])
rev_count = db.execute("SELECT COUNT(*) FROM practice.reviews WHERE book_id = :book_id",
{"book_id": '6844'}).fetchone()
print('wew')
print(rev_count[0])

rew = db.execute("SELECT * FROM practice.reviews WHERE book_id = :book_id",
{"book_id": '6844'}).fetchone()
print(rew.review)

#db.execute("DELETE FROM practice.reviews WHERE book_id = :book_id",
#{"book_id": '6844'})
#db.commit()