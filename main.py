import os

from flask import Flask, render_template, request, redirect
from flask_login import login_user, LoginManager, login_required, logout_user

from data import db_session
from data.__all_models import *
from data.db_session import create_session
from data.login_form import LoginForm
from data.register_form import RegisterForm

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

db_session.global_init("db/users.sqlite")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player')}")
    return render_template("index.html")


@app.route("/search/<string:player>", methods=["POST", "GET"])
def search(player):
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player')}")
    return render_template("search.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player')}")
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="This email is already used")
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="This nickname is already taken")
        user = User(
            nickname=form.nickname.data,
            battle_tag=form.battle_tag.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player')}")
    form = LoginForm()
    if form.validate_on_submit():   
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong login or password",
                               form=form)
    return render_template('login.html', form=form)


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player')}")
    return render_template("account_page.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
