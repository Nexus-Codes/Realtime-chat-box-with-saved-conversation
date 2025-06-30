from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, join_room, send, disconnect, leave_room
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
socketio = SocketIO(app)

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/create-room", methods=["POST"])
def create_room():
    username = request.form.get("username")
    session['username'] = username
    session['code'] = 'VVGQ'  # fixed room for now

    # Load previous messages
    messages = []
    if os.path.exists(CHAT_LOG_FILE):
        with open(CHAT_LOG_FILE, "r") as f:
            messages = json.load(f)

    return render_template("room.html", messages=messages)


@socketio.on("join")
def handle_join():
    room = session.get("code")
    username = session.get("username")
    join_room(room)

    join_message = f"{username} has entered the chat."
    save_message(username, join_message)

    send({"name": username, "message": "has entered the chat."}, to=room)


@socketio.on("send_message")
def handle_message(data):
    room = session.get("code")
    username = session.get("username")
    message = data["message"]

    save_message(username, message)

    send({"name": username, "message": message}, to=room)


@socketio.on("disconnect")
def handle_disconnect():
    username = session.get("username")
    room = session.get("code")

    if username and room:
        leave_room(room)
        time.sleep(0.1)  # small delay to let last messages propagate
        leave_message = f"{username} has left the chat."
        save_message(username, leave_message)
        send({"name": username, "message": "has left the chat."}, to=room)


import json
import os

CHAT_LOG_FILE = "chat_history.json"

def save_message(username, message):
    log = []
    if os.path.exists(CHAT_LOG_FILE):
        with open(CHAT_LOG_FILE, "r") as f:
            log = json.load(f)

    log.append({"name": username, "message": message})

    with open(CHAT_LOG_FILE, "w") as f:
        json.dump(log, f)



if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=False)
