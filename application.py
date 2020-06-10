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
#set FLASK_ENV=development //debug option
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
    hello_user = '<h2>Oof, ${name}!</h2>'

    #check if username already exists
    if session.get("username") is None:
        return jsonify({"success": False })

    #return json with username
    return jsonify({"success": True, "helloUser": hello_user, "user": session["username"]})

@socketio.on("submit channel name")
def vote(data):
    channel_name_emit = data["channel_name"]
    emit("share channel name", {"ChannelNameEmit": channel_name_emit}, broadcast=True)


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