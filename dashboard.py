from flask import Flask, render_template
import json

app = Flask(__name__)

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

@app.route("/")
def index():

    users = load_users()

    total_users = len(users)

    return render_template(
        "index.html",
        users=users.values(),
        total_users=total_users
    )

app.run(port=5000)