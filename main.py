import json
import os
import random
import string

from PIL import Image
from flask import Flask, render_template, request, redirect, session
from flask_login import login_user, LoginManager, login_required, logout_user

from api import get_stats
from data import db_session
from data.__all_models import *
from data.db_session import create_session
from data.edit_form import EditForm
from data.login_form import LoginForm
from data.quiz_sound_form import QuizSound
from data.register_form import RegisterForm
from defs import *

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

db_session.global_init("db/users.sqlite")

login_manager = LoginManager()
login_manager.init_app(app)

alph = string.digits + string.ascii_letters

ids = list(range(1, 99999))
quiz_id = {}

with open("./static/json/quiz.json", encoding="utf8") as js:
    js = json.load(js)
    sound = js["soundtrack"]
    photo = js["location"]


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    return render_template("index.html")


@app.route("/search/<string:player>", methods=["POST", "GET"])
def search(player):
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    if player:
        stats = get_stats(player)
        return render_template("search.html", stats=stats)
    return render_template("search.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
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
        if not all(el in alph for el in form.nickname.data):
            return render_template('register.html',
                                   form=form,
                                   message="Nickname can't contain special symbols or spaces")
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
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
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
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    return render_template("account_page.html")


@app.route("/account/edit", methods=["POST", "GET"])
@login_required
def edit_account():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    form = EditForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(form.id.data)
        if form.new_password.data:
            if form.current_password.data and user.check_password(form.current_password.data):
                user.set_password(form.new_password.data)
            else:
                return render_template("edit_account.html", form=form,
                                       message="Wrong current password")
        if not all(el in alph for el in form.nickname.data):
            return render_template('edit_account.html',
                                   form=form,
                                   message="Nickname can't contain special symbols or spaces")
        if form.email.data != user.email and db_sess.query(User).filter(
                User.email == form.email.data).first():
            return render_template('edit_account.html',
                                   form=form,
                                   message="This email is already used")
        if form.nickname.data != user.nickname and db_sess.query(User).filter(
                User.nickname == form.nickname.data).first():
            return render_template('edit_account.html',
                                   form=form,
                                   message="This nickname is already taken")
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.battle_tag = form.battle_tag.data
        avatar = form.avatar.data.read()
        if len(avatar) > 0:
            with open(f"static/img/{form.id.data}.png", mode="wb") as av:
                av.write(avatar)
            user.avatar = f"static/img/{form.id.data}.png"
            user.avatar = f"static/img/{form.id.data}.png"
            crop_max_square(Image.open(f"static/img/{form.id.data}.png")).save(
                f"static/img/{form.id.data}_thmb.png")
            user.thumbnail = f"static/img/{form.id.data}_thmb.png"
        db_sess.commit()
        return redirect("/account")
    return render_template("edit_account.html", form=form)


@app.route("/wiki", methods=["POST", "GET"])
def wiki():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    with open("static/json/heroes.json") as js:
        heroes = json.load(js)
    return render_template("wiki_main.html", heroes=heroes)


@app.route("/wiki/<string:name>", methods=["POST", "GET"])
def wiki_hero(name):
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    with open("static/json/heroes.json") as js:
        heroes = json.load(js)
        try:
            hero = heroes["support"][name]
        except KeyError:
            try:
                hero = heroes["damage"][name]
            except KeyError:
                try:
                    hero = heroes["tank"][name]
                except KeyError:
                    return "Something went wrong"
    return render_template("hero_page.html", name=name, hero=hero)


@app.route("/quiz", methods=["POST", "GET"])
def quiz():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    id = ids.pop(0)
    with open("static/json/quiz.json") as js:
        quiz = json.load(js)
    return render_template("quiz_main.html", quizs=quiz, id=id)


@app.route("/quiz/soundtrack/<int:id>/<int:num>", methods=["POST", "GET"])
def sound_quiz():
    score, num = session.get("score", 0), session.get("num", 0)
    if score or num:
        session[]
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    form = QuizSound()
    if id not in quiz_id.keys():
        quiz_id[id] = [random.sample(list(zip(list(sound.values()), sound.keys())), 5), 0, 0]
        idk = []
        for i in range(5):
            answ = [quiz_id[id][0][i][1]]
            temp = list(sound.keys())
            temp.remove(answ[0])
            answ.extend(random.sample(temp, 2))
            random.shuffle(answ)
            idk.append(answ)
        quiz_id[id].append(idk)
        form.radio.choices = idk[num]
    else:
        answ = quiz_id[id][3][num]
        form.radio.choices = answ
        if form.is_submitted():
            print(form.radio.data)
    return render_template("soundtrack_quiz.html", data=quiz_id[id], num=num, answ=answ, form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
