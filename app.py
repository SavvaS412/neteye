from flask import Flask, render_template, request, jsonify

from notification import Notification
from scanning import start_scan_thread
from db_manager import get_rules, connect_to_db, RULES_TABLE_NAME, RULES_COL_ID
import mysql.connector

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
    return render_template("settings.html", rules_list=get_rules())

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

@app.route("/rule-details/<int:rule_id>")
def rule_details(rule_id):
    rule = get_rule_details(rule_id)
    return jsonify(rule)

def get_rule_details(rule_id):
    try:
        with connect_to_db() as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {RULES_TABLE_NAME} WHERE {RULES_COL_ID} = %s", (rule_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'action': row[2],
                    'parameter': row[3],
                    'amount': row[4],
                    'target': row[5]
                }
            else:
                return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    except Exception as e:
        print(f"Error getting rule details: {e}")

if __name__ == "__main__":
    app.run(debug=True)