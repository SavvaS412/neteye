from flask import Flask, render_template, request, redirect, url_for, jsonify

from notification import Notification
from scanning import start_scan_thread
from db_manager import get_rules, remove_rule, insert_rule, get_emails, remove_email
from rule import Rule
from detection import Parameter
from file_utils import save_settings

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

        return render_template("settings.html", rules_list=rules, emails=emails, parameters=parameters)

    
    elif request.method == "POST":
        # Extract form data
        print(request.form)
        rule_name = request.form['rule_name']
        rule_parameter = int(request.form['rule_parameter'])
        rule_action = int(request.form['rule_action'])
        rule_amount = int(request.form['rule_amount'])
        rule_target = request.form['rule_target']

        # Insert the new rule into the database
        insert_rule(rule_name, rule_parameter, rule_action, rule_amount, rule_target)


        # Redirect back to the settings page
        return redirect(url_for('settings'))


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
