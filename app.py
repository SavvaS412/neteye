from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/traffic")
def capture():
    return render_template("traffic.html")

@app.route("/map")
def map():
    device_list = []
    return render_template("map.html", list=device_list)

@app.route("/notifications")
def notifications():
    notifications_list = []
    return render_template("notifications.html", list=notifications_list)

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/api/notifications", methods=["GET","POST"])
def api_notifications():
    if request.method == "GET" or (request.method == "POST" and request.args.get("html")):
        return [{"id":2, "name":"DDOS", "type":"Network Problems", "description":"lol", "date":"24/02/2024"}]
    else:
        return render_template("notification_popup.html")

if __name__ == "__main__":
    app.run(debug=True)