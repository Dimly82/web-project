from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "The best web project in the world!"


if __name__ == '__main__':
    app.run()
