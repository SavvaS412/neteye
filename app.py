from flask import Flask, render_template

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

if __name__ == "__main__":
    app.run(debug=True)