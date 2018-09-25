CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users,
  book_id INTEGER REFERENCES books,
  rating INTEGER NOT NULL,
  review_title VARCHAR NOT NULL,
  review_body VARCHAR NOT NULL
);
