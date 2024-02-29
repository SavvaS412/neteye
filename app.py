from flask import Flask, render_template, request

from notification import Notification
from scanning import start_scan_thread

app = Flask(__name__)
device_list = []
notification_list = []
start_scan_thread(device_list)

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
    return render_template("notifications.html", list=Notification.get_all())

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/api/map", methods=["GET","POST"])
def api_map():
    copy_list = [] #TODO: lock
    for device in device_list:
        copy_list.append(device.__dict__)   
    return copy_list    #TODO: unlock

@app.route("/api/notifications", methods=["GET","POST"])
def api_notifications():
    copy_list = []  #TODO: lock
    for notification in notification_list:
        copy_list.append(notification.__dict__)
    notification_list.clear()   #TODO: unlock
    return copy_list

if __name__ == "__main__":
    app.run(debug=True)