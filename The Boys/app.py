from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Path to store statuses
DATA_FILE = "data/statuses.json"

# Initialize the data file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump([], file)


def read_statuses():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


def write_status(statuses):
    with open(DATA_FILE, "w") as file:
        json.dump(statuses, file, indent=4)


@app.route("/")
def index():
    statuses = read_statuses()
    return render_template("index.html", statuses=statuses)


@app.route("/update", methods=["GET", "POST"])
def update_status():
    if request.method == "POST":
        name = request.form["name"]
        activities = request.form.getlist("activities")
        custom_activity = request.form.get("custom_activity", "").strip()
        with_people = [person.strip() for person in request.form.getlist("with_people") if person.strip()]

        # Include custom activity if provided
        if custom_activity:
            activities.append(custom_activity)

        # Remove existing entry with the same name
        statuses = read_statuses()
        statuses = [status for status in statuses if status["name"] != name]

        # Add the new status with a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        new_status = {
            "name": name,
            "activities": activities,
            "timestamp": timestamp
        }
        if with_people:  # Only add "with" key if there are people listed
            new_status["with"] = with_people

        statuses.append(new_status)
        write_status(statuses)

        # Emit a real-time notification
        notification_message = f"{name} updated their status!"
        socketio.emit('status_update', {
            'name': name,
            'activities': activities,
            'with_people': with_people,
            'timestamp': timestamp,
            'message': notification_message
        })

        return redirect(url_for("index"))

    options = ["on cord", "playing fortnite", "working", "busy"]
    return render_template("update_status.html", options=options)


@app.route("/delete/<name>", methods=["POST"])
def delete_status(name):
    statuses = read_statuses()
    statuses = [status for status in statuses if status["name"] != name]
    write_status(statuses)
    return redirect(url_for("index"))


if __name__ == "__main__":
    socketio.run(app, debug=True)
