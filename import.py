import csv

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)

    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                {"isbn" : isbn, "title" : title, "author" : author, "year" : year})
        print(f'Added book with isbn {isbn} whose name is {title} written by {author} published on {year}.')
    db.commit()


if __name__ == "__main__":
    main()
