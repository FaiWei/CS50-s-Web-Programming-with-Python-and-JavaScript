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

#class for channels
pass_channel_id = {}

class Channel:
    def __init__(self):
        self.id = 0
        self.channel = {}             
        self.time = {}
        self.check = False
        self.channel_name = {}
    def regID(self, channel_name):
        self.channel_name[self.id] = channel_name
        self.channel[self.id] = []
        self.id += 1
        self.check = True
        return self.id - 1
    def memorizeMessage(self, channel_id, message, timestamp, user):
        dict_temp = {'message': message, 'user': user, 'timestamp': timestamp}
        self.channel[channel_id].append(dict_temp) 
        if (len(self.channel[channel_id]) > 100):
            print('deleted: ' + self.channel[channel_id].pop(0)) 


channels_storage = Channel()

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


@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("username") is None:
         session["username"] = None
    if request.method == "POST":
        session["username"] = request.form.get("username")

    return render_template("index.html", username=session["username"])

@app.route("/check", methods=["GET", "POST"])
def check_current_situation():
    global channels_storage
    global pass_channel_id
    #check if username already exists
    if session.get("username"):
        if channels_storage.check:
            print('channel in check: ' + str(pass_channel_id[session["username"]]))

            return jsonify({"success": True, "user": session["username"], "loadChannelsReady": True, "LoadExistingChannels": channels_storage.channel_name, "ChannelID": pass_channel_id[session["username"]]})
        else:
            return jsonify({"success": True, "user": session["username"], "loadChannelsReady": False})
    else:
        return jsonify({"success": False})

  

@socketio.on("submit channel name")
def channel_submit(data):
    channel_name_emit = data["channel_name"]
    global channels_storage
    channel_number = channels_storage.regID(channel_name_emit) 
    global pass_channel_id
    pass_channel_id[session["username"]] = channel_number
    emit("share channel name", {"ChannelNameEmit": channel_name_emit, "ChannelID": channel_number, "ChatCreated": True}, broadcast=True)

@socketio.on("submit message")
def message_submit(data):
    user_message_emit = data["user_message"]
    time_stamp_emit = data["time_stamp"]
    global pass_channel_id 
    global channels_storage
    channels_storage.memorizeMessage(pass_channel_id[session["username"]], user_message_emit, time_stamp_emit, session["username"]) 
    emit("share user message", {"UserMessageEmit": user_message_emit, "User": session["username"], "Timestamp": time_stamp_emit}, broadcast=True)

@app.route("/<int:channel_id>")
def channels(channel_id):
    global channels_storage
    global pass_channel_id 
    pass_channel_id[session["username"]] = channel_id
    return jsonify({"success": True, "Messages": channels_storage.channel[channel_id], "Channel": channels_storage.channel_name[channel_id]})


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

if __name__ == '__main__':
    socketio.run(app)