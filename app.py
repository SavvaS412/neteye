from flask import Flask, render_template, request, session
from flask_session import Session
from multiprocessing import Manager, Process

from notification import Notification, delete_old_notifications
from scanning import scan

app = Flask(__name__)
app.secret_key = "Sky's the Limit - The Notorious BIG"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_FILE_THRESHOLD'] = 100
Session(app)

with app.app_context():
    manager = Manager()
    device_list = manager.list()
    notification_list = manager.list()
    Process(target=delete_old_notifications, args=(notification_list,), daemon=True).start()
    Process(target=scan, args=(device_list, notification_list,), daemon=True).start()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/traffic")
def capture():
    return render_template("traffic.html")

@app.route("/map")
def map():
    return render_template("map.html", list=device_list)

@app.route("/notifications")
def notifications():
    notifications = Notification.get_all()
    if len(notifications) == 0:
        if not session.get("notification_list"):
            session["notification_list"] = []
        for noti in session["notification_list"]:
            notifications.insert(0, noti.__dict__)
    return render_template("notifications.html", list=notifications)

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/api/map", methods=["GET","POST"])
def api_map():
    copy_list = []
    for device in device_list:
        copy_list.append(device.__dict__)   
    return copy_list

@app.route("/api/notifications", methods=["GET","POST"])
def api_active_notifications():
    if not session.get("notification_list"):
        session["notification_list"] = []
    copy_list = []
    for notification in notification_list:
        if notification not in session["notification_list"]:
            copy_list.append(notification.__dict__)
            session["notification_list"].append(notification)
    session.modified = True
    return copy_list

if __name__ == "__main__":
    app.run(debug=True)