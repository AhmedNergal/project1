import os

from flask import Flask, render_template, session, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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
    print(session)
    if 'username' in session:
        username = session['username']
        return render_template("index.html", username=username)
    else:
        return render_template("index.html")

# Register Routes

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    {"username" : username, "password" : password})
            db.commit()
            return redirect("/search", code=303)

        except:
            return render_template("error.html", message="Username already exists!!!")

# Login Routes

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username" : username, "password" : password}).rowcount != 0:
            session['username'] = username
            return redirect("/search", code=303)
        else:
            return render_template("error.html", message="Incorrect username or password!!")

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
            return render_template("search.html")
        else:
            return redirect("/login")
    elif request.method == "POST":
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

        return render_template("results.html", results=results)

@app.route("/book/<int:book_id>")
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id" : book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="Such book doesn't exist!!!")
    else:
        return render_template("book.html", book=book)
