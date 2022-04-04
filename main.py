import os
from data import db_session


from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player')}")
    return render_template("index.html")


@app.route("/search/<string:player>")
def search(player):
    return render_template("search.html")


@app.route("/register")
def register():
    return render_template("register_form.html")


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
