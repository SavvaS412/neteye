from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_session import Session
from multiprocessing import Manager, Process

from notification import Notification, delete_old_notifications
from db_manager import get_rules, remove_rule, insert_rule, get_emails, remove_email
from rule import Rule
from scanning import scan
import packet_capture
from detection import Parameter
from file_utils import save_settings, load_settings

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
    packet_list = manager.list()
    Process(target=delete_old_notifications, args=(notification_list,), daemon=True).start()
    Process(target=scan, args=(device_list, notification_list,), daemon=True).start()
    Process(target=packet_capture.capture, args=(30,packet_list,), daemon=True).start()

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

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "GET":
        rows = get_rules()
        rules = []
        for row in rows:
            rule = Rule(row[1], row[2], row[3], row[4], row[5])
            rules.append(rule)

        parameters = [(param.value, param.name) for param in Parameter]

        emails = get_emails()

        # Load settings from settings.json
        global_settings = load_settings()

        return render_template("settings.html", rules_list=rules, emails=emails, parameters=parameters, global_settings=global_settings)

    elif request.method == "POST":
        # Extract form data and save settings
        try:
            updated_settings = {key: int(request.form[key]) for key in request.form}
            save_settings(updated_settings)
            return redirect(url_for('settings'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/map", methods=["GET","POST"])
def api_map():
    copy_list = []
    for device in device_list:
        copy_list.append(device.__dict__)   
    return copy_list

@app.route("/api/notifications", methods=["GET","POST"])
def api_notifications():
    if not session.get("notification_list"):
        session["notification_list"] = []
    copy_list = []
    for notification in notification_list:
        if notification not in session["notification_list"]:
            copy_list.append(notification.__dict__)
            session["notification_list"].append(notification)
    session.modified = True
    return copy_list

@app.route("/api/traffic")
def api_capture():
    if not session.get("packet_list"):
        session["packet_list"] = []
    copy_list = []
    for packet in packet_list[:packet_capture.PACKET_LIMIT]:
        packet_json = packet_capture.packet_to_json(packet)
        if packet_json not in session["packet_list"]:
            copy_list.append(packet_json)
            session["packet_list"].insert(0,packet_json)
    if len(session["packet_list"]) > packet_capture.PACKET_LIMIT:
        session["packet_list"] = session["packet_list"][:packet_capture.PACKET_LIMIT]
    session.modified = True
    return copy_list

@app.route("/delete_rule/<rule_name>", methods=["POST"])
def delete_rule(rule_name):
    remove_rule(rule_name)
    return "", 204  # No content response

@app.route("/delete_email/<email_address>", methods=["POST"])
def delete_email(email_address):
    remove_email(email_address)
    return "", 204  # No content response

@app.route("/save_global_settings", methods=["POST"])
def save_settings_route():
    try:
        settings = request.json  # Assuming JSON data is sent in the request body
        save_settings(settings)
        return jsonify({"message": "Settings saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
