import os
import requests

#set FLASK_APP=application.py
#set DATABASE_URL=postgres://ribvyxoiljnmtg:747a0c2d02fe22bf66d2a41dbd0f6848e208deb9cd84353b5a076a661ae115d5@ec2-46-137-156-205.eu-west-1.compute.amazonaws.com:5432/d5dtbbafsqfea9

from flask import Flask, session, redirect, render_template, jsonify, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show main page with search or search results"""  

    if request.method == "POST":
        #get user search request
        search_request = request.form.get("search_request")
        request_splitted = search_request.split()
        liked_req = phraseforlike(request_splitted)
        # derive search results by to_tsvector-to_tsquery
        smart_req = db.execute("SELECT * FROM practice.books WHERE to_tsvector(title) || to_tsvector(author) || to_tsvector(isbn) @@ plainto_tsquery(:search_request) ORDER BY title ASC", {"search_request": search_request}).fetchall()
        # derive search results by LIKE
        simple_req = db.execute("SELECT * FROM practice.books WHERE title || author || isbn LIKE :search_request ORDER BY title ASC", {"search_request": liked_req}).fetchall()
        # merge them there to_tsvector-to_tsquery goes first
        for row_s in simple_req:
            for row in smart_req:
                if row_s == row:
                    simple_req.remove(row_s)
        smart_req.extend(simple_req)
        
        #if search result "None" return different page
        if not smart_req:
            return apology("Results not found")
        return render_template("search.html", rows=smart_req)

    else:
        # derive username database
        username = db.execute("SELECT username FROM practice.users \
                                WHERE id = :id", {"id": session["user_id"]}).fetchone()
        return render_template("index.html", username=username.username)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        row = db.execute("SELECT * FROM practice.users WHERE username = :username",
                          {"username":request.form.get("username")}).fetchone()


        # Ensure username exists and password is correct
        if row is None or not check_password_hash(row.password, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = row.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        name = request.form.get("username")

        exists_username = db.execute("SELECT username FROM practice.users WHERE username = :username", {"username":name}).fetchone()

        if exists_username:
            return apology("username already exists", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # Ensure password check was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password check", 400)
        # Ensure password check was submitted
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords do not match", 400)

        # insert new info in db
        passhash = generate_password_hash(request.form.get("password"))
        db.execute(
            "INSERT INTO practice.users (username,password) VALUES (:username, :password)",
            {"username": name, "password": passhash})
        db.commit()

        # log into session
        fetchid = db.execute("SELECT id FROM practice.users WHERE username = :username", {"username":name}).fetchone()
        session["user_id"] = fetchid.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/books/<int:book>", methods=["GET", "POST"])
def books(book):
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # check delete request
        delete = request.form.get("delete")       
        if delete:
            db.execute("DELETE FROM practice.reviews WHERE book_id = :book_id",
            {"book_id": book})

            rev_count = db.execute("SELECT COUNT(*) FROM practice.reviews WHERE book_id = :book_id",
            {"book_id": book}).fetchone()    
            db.execute("UPDATE practice.books SET review_count = :rev_count WHERE id = :id",
            {"id": book, "rev_count": rev_count[0]})

            av_score = db.execute("SELECT AVG(score) FROM practice.reviews WHERE book_id = :book_id",
            {"book_id": book}).fetchone()
            db.execute("UPDATE practice.books SET average_score = :av_score WHERE id = :id",
            {"id": book, "av_score": av_score[0]}) 
            db.commit()
        review = request.form.get("review")
        # check review request TO DO^ add to delet avg
        if review:
            score = request.form.get("score")
            if review is None:
                return apology("Add review", 400)
            db.execute("INSERT INTO practice.reviews (review, book_id, user_id) VALUES (:review, :book_id, :user_id)",
            {"review": review, "book_id": book, "user_id": session["user_id"]})
            rev_count = db.execute("SELECT COUNT(*) FROM practice.reviews WHERE book_id = :book_id",
            {"book_id": book}).fetchone()    
            db.execute("UPDATE practice.books SET review_count = :rev_count WHERE id = :id",
            {"id": book, "rev_count": rev_count[0]})
            # check score
            if score:
                db.execute("UPDATE practice.reviews SET score = :score WHERE book_id = :book_id AND user_id = :user_id",
                {"book_id": book, "user_id": session["user_id"], "score": score})
                av_score = db.execute("SELECT AVG(score) FROM practice.reviews WHERE book_id = :book_id",
                {"book_id": book}).fetchone()
                db.execute("UPDATE practice.books SET average_score = :av_score WHERE id = :id",
                {"id": book, "av_score": av_score[0]})
            db.commit()      
    # User reached route via GET (as by clicking a link or via redirect)
    #else:
    # Make sure book exists.
    getbook = db.execute("SELECT * FROM practice.books WHERE id = :id", {"id": book}).fetchone()
    #user_reviews = db.execute("SELECT * FROM practice.reviews WHERE book_id = :id", {"id": book}).fetchall()  
    user_review = db.execute("SELECT * FROM practice.reviews WHERE user_id = :id AND book_id = :book_id", {"book_id": book, "id": session["user_id"]}).fetchone()
    time = db.execute("SELECT to_char(timestamp, 'HH12:MI:SS, DD Mon YYYY') FROM practice.reviews WHERE user_id = :id AND book_id = :book_id", {"book_id": book, "id": session["user_id"]}).fetchone()
    gr_info = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "5jXseztBn2uj3YIDp0rA", "isbns": getbook.isbn})
    gr_book = gr_info.json()
    g_req = gr_book['books'][0]
    if getbook is None:
        return apology("No such book", 400)
    return render_template("book.html", getbook=getbook, gr_info=g_req, user_review=user_review, time=time)

@app.route("/api/<string:isbn_api>")
def book_api(isbn_api):
    #Return details about a book.

    # Make sure book exists.
    getbook = db.execute("SELECT * FROM practice.books WHERE isbn = :isbn", {"isbn": isbn_api}).fetchone()
    if getbook is None:
        return jsonify({"error": "this string or isbn number isn’t in database"}), 404

    return jsonify({
            "isbn": getbook.isbn,
            "title": getbook.title,
            "author": getbook.author,
            "year": getbook.year,
            "review_count": getbook.review_count,
            "average_score": getbook.average_score
        })

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

#create search variable for LIKE
def phraseforlike(words):
    x = '%'
    a = 1
    for word in words:
        if a == 1:
            x = x + word + '%'
            a = 0
        else:
            x = x + ' AND %' + word + '%'
    return x

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
