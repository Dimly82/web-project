import os
from data import db_session


from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
