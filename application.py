import os

from flask import Flask, jsonify, render_template, session, request, redirect
from flask_session import Session
from flask_socketio import SocketIO, emit
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

#set FLASK_APP=application.py

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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

votes = {"yes": 0, "no": 0, "maybe": 0}

@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("username") is None:
         session["username"] = None
    if request.method == "POST":
        session["username"] = request.form.get("username")

    return render_template("index.html", username=session["username"])

@app.route("/usercheck", methods=["GET", "POST"])
def usercheck():

    #login html
    input_user = '<form method="post"><fieldset><div class="form-group">\
            <input name="username" autocomplete="off" autofocus class="form-control" placeholder="Nickname" type="text"/></div>\
            <div class="form-group"><button class="btn btn-primary" type="submit">Input nickname</button></div></fieldset></form>'
    usercarcas = '<h2>Oof, ${name}!</h2>'

    #check if username already exists
    if session.get("username") is None:
        return jsonify({"success": False, "input": input_user})

    #return json with username
    return jsonify({"success": True, "usercarcas": usercarcas, "user": session["username"]})

@socketio.on("submit vote")
def vote(data):
    selection = data["selection"]
    votes[selection] += 1
    emit("vote totals", votes, broadcast=True)



@app.route("/logout")
def logout():
    """Log out"""

    # Forget session
    session.clear()

    # Redirect user to login form
    return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)