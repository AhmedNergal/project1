import os

from flask import Flask, render_template, session, request, redirect, jsonify
from flask_session import Session
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Index Route

@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        return render_template("index.html", username=username)
    else:
        return render_template("index.html")

# Register Routes

@app.route("/register", methods=["GET", "POST"])
def register():
    if 'username' not in session:
        if request.method == "GET":
            return render_template("register.html")
        elif request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            try:
                db.execute("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)",
                        {"username" : username, "password_hash" : password_hash})
                db.commit()
                return redirect("/search", code=303)

            except:
                return render_template("error.html", message="Username already exists!!!")
    else:
            return redirect("/", code=303)

# Login Routes

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' not in session:
        if request.method == "GET":
            return render_template("login.html")
        elif request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user = db.execute("SELECT * FROM users WHERE username = :username", {"username":username}).fetchone()
            if user == None:
                return render_template("error.html", message="Incorrect username!!")
            database_password_hash = user[2]
            check_password = bcrypt.check_password_hash(database_password_hash, password)
            if check_password == True:
                session['username'] = username
                return redirect("/search", code=303)
            else:
                return render_template("error.html", message="Incorrect password!!")
    else:
        return redirect("/", code=303)

# Logout Route

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect('/', code=303)

# Search Routes

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        if 'username' in session:
                username = session['username']
                return render_template("search.html", username=username)
        else:
            return redirect("/login")
    elif request.method == "POST":
        username = session['username']
        keyword = request.form.get("keyword")
        query = request.form.get("query")
        if query == "isbn":
            results = db.execute("SELECT * FROM books WHERE isbn = :keyword", {"keyword" : keyword}).fetchall()
        elif query == "title":
            results = db.execute("SELECT * FROM books WHERE title LIKE :keyword", {"keyword" : '%' + keyword + '%'}).fetchall()
        elif query == "author":
            results = db.execute("SELECT * FROM books WHERE author LIKE :keyword", {"keyword" : '%' + keyword + '%'}).fetchall()
        elif query == "year":
            results = db.execute("SELECT * FROM books WHERE year = :keyword", {"keyword" : keyword}).fetchall()

        return render_template("results.html", results=results, username=username)

# Book Route

@app.route("/book/<int:book_id>")
def book(book_id):
    if 'username' in session:
        username = session['username']
        book = db.execute("SELECT * FROM books WHERE id = :id", {"id" : book_id}).fetchone()
        reviews = db.execute("SELECT * FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id", {"book_id" : book_id}).fetchall()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key" : "DnUD36XqebyhLfdgeQav5Q", "isbns" : book.isbn})
        goodreads_results = res.json()
        average_score = goodreads_results["books"][0]["average_rating"]
        review_count = goodreads_results["books"][0]["reviews_count"]
        if book is None:
            return render_template("error.html", message="Such book doesn't exist!!!")
        else:
            return render_template("book.html", book=book, reviews=reviews, average_score=average_score, review_count=review_count, username=username)

    else:
        return render_template("login.html")

# Review Routes

@app.route("/book/<int:book_id>/review", methods=["GET", "POST"])
def review(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id" : book_id}).fetchone()
    if 'username' in session:
        username = session['username']
        user_id = int(db.execute("SELECT id FROM users WHERE username = :username", {"username" : username}).fetchone()[0])
        if request.method == "GET":
            return render_template("review.html", book=book, username=username)
        elif request.method == "POST":
            if db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                    {"user_id" : user_id, "book_id" : book_id }).rowcount != 0:
                    return render_template("error.html", username=username, message="You reviewed this book before!!!")
            else:
                rating = request.form.get("rating")
                review_title = request.form.get("review_title")
                review_body = request.form.get("review_body")
                db.execute("INSERT INTO reviews (user_id, book_id, rating, review_title, review_body) VALUES (:user_id, :book_id, :rating, :review_title, :review_body)",
                            {"user_id" : user_id, "book_id" : book_id, "rating" : rating, "review_title" : review_title, "review_body" : review_body})
                db.commit()
                stringId = str(book_id)
                redirectURL = "/book/" + stringId
                return redirect(redirectURL, code=303)

# ISBN API Route

@app.route("/api/<string:isbn>")
def isbn_api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn" : isbn}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key" : "DnUD36XqebyhLfdgeQav5Q", "isbns" : book.isbn})
    goodreads_results = res.json()
    average_score = goodreads_results["books"][0]["average_rating"]
    review_count = goodreads_results["books"][0]["reviews_count"]

    if book is None:
        return jsonify(result="error",
                message="book not found!"), 404
    else:
        return jsonify(
            title=book.title,
            author=book.author,
            year=book.year,
            isbn=book.isbn,
            review_count=review_count,
            average_score=average_score
        )
