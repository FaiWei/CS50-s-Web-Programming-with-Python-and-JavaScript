import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://ribvyxoiljnmtg:747a0c2d02fe22bf66d2a41dbd0f6848e208deb9cd84353b5a076a661ae115d5@ec2-46-137-156-205.eu-west-1.compute.amazonaws.com:5432/d5dtbbafsqfea9")
db = scoped_session(sessionmaker(bind=engine))  

f = open("books.csv")
reader = csv.reader(f)

for isbn, title, author, year in reader:
    db.execute("INSERT INTO practice.books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                {"isbn": isbn, "title": title, "author": author, "year": year})
    #print(f"{title} writed by {author} in {year}. ISBN: {isbn}")
db.commit()
print("done")