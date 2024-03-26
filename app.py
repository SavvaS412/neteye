from flask import Flask, render_template, request, redirect, url_for, jsonify

from notification import Notification
from scanning import start_scan_thread
from db_manager import get_rules, remove_rule, insert_rule, get_emails, remove_email
from rule import Rule
from detection import Parameter
from file_utils import save_settings, load_settings

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
    notifications = Notification.get_all()
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
    copy_list = []
    for notification in notification_list:
        copy_list.append(notification.__dict__)
    notification_list.clear()
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
