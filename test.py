import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#db.execute("INSERT INTO practice.reviews (review, book_id, user_id) VALUES (:review, :book_id, :user_id)",
#{"review": review, "book_id": book, "user_id": session["user_id"]})
rev_count = db.execute("SELECT COUNT(*) FROM practice.reviews WHERE book_id = :book_id",
{"book_id": '6844'}).fetchone()
print(rev_count[0])

rew = db.execute("SELECT * FROM practice.reviews WHERE book_id = :book_id",
{"book_id": '6844'}).fetchone()
print(rew.review)

#db.execute("DELETE FROM practice.reviews WHERE book_id = :book_id",
#{"book_id": '6844'})
#db.commit()