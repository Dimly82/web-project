import os
import string
from io import BytesIO

import PIL
import werkzeug.exceptions
from PIL import Image
from flask import Flask, render_template, request, redirect, session
from flask_login import login_user, LoginManager, login_required, logout_user

from data import db_session
from data.__all_models import *
from data.db_session import create_session
from data.delete_form import DeleteForm
from data.edit_form import EditForm
from data.login_form import LoginForm
from data.register_form import RegisterForm
from defs import *

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

db_path = os.path.abspath("db/users.sqlite")
db_session.global_init(db_path)

login_manager = LoginManager()
login_manager.init_app(app)

errors = {
    404: ["Ooooopsies, looks like the page's missing..",
          "/static/img/oops.gif", "Monkey killing a laptop",
          "404 Not found"],
    401: ["Looks like you're not authorised (´･ω･`)?",
          "/static/img/hack.gif", "The russian hacker",
          "401 Unauthorised"]
}

alph = string.digits + string.ascii_letters

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


@app.route("/search")
def search_main():
    return render_template("search_main.html")


@app.route("/search/<string:player>", methods=["POST", "GET"])
def search(player):
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    if player:
        stats = get_stats(player)
        if not stats:
            return render_template("search_main.html", message="Incorrect BattleTag")
        return render_template("search.html", stats=stats)
    return render_template("search_main.html")


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
            try:
                Image.open(BytesIO(avatar)).save(f"static/profile_pictures/{form.id.data}.png")
            except PIL.UnidentifiedImageError:
                return render_template("edit_account.html", form=form, message="Wrong image format")
            user.avatar = f"/static/profile_pictures/{form.id.data}.png"
            crop_max_square(Image.open(f"static/profile_pictures/{form.id.data}.png")).save(
                f"static/profile_pictures/{form.id.data}_thmb.png")
            user.thumbnail = f"/static/profile_pictures/{form.id.data}_thmb.png"
        db_sess.commit()
        return redirect("/account")
    return render_template("edit_account.html", form=form)


@app.route("/account/delete", methods=["POST", "GET"])
@login_required
def account_delete():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    form = DeleteForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(form.id.data)
        print(11)
        if user.check_password(form.password.data):
            db_sess.delete(user)
            db_sess.commit()
            logout_user()
            return redirect("/")
        else:
            return render_template("delete.html", form=form,
                                   message="Wrong password")
    return render_template("delete.html", form=form)


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
    session["score"] = 0
    session["num"] = 0
    session["sound"] = generate_quiz("sound")
    session["photo"] = generate_quiz("photo")
    print(session["photo"])
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    return render_template("quiz_main.html")


@app.route("/quiz/soundtrack", methods=["POST", "GET"])
def sound_quiz():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    try:
        session["num"]
    except KeyError:
        session["num"] = 0
        session["score"] = 0
        session["sound"] = generate_quiz("sound")
        session["photo"] = generate_quiz("photo")
    if request.method == "POST" and request.form.get("answer"):
        answer = request.form.get("answer")
        if answer == session["sound"][0][session["num"]][1]:
            session["score"] += 1
        session["num"] += 1
        if session["num"] > 4:
            temp = session["score"]
            session["num"] = 0
            session["score"] = 0
            session["sound"] = generate_quiz("sound")
            session["photo"] = generate_quiz("photo")
            return render_template("results.html", score=temp)
    return render_template("soundtrack_quiz.html", num=session["num"], qz=session["sound"])


@app.route("/quiz/photo", methods=["POST", "GET"])
def photo_quiz():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    try:
        session["num"]
    except KeyError:
        session["num"] = 0
        session["score"] = 0
        session["sound"] = generate_quiz("sound")
        session["photo"] = generate_quiz("photo")
    if request.method == "POST" and request.form.get("answer"):
        answer = request.form.get("answer")
        if answer == session["photo"][0][session["num"]][1]:
            session["score"] += 1
        session["num"] += 1
        if session["num"] > 4:
            temp = session["score"]
            session["num"] = 0
            session["score"] = 0
            session["sound"] = generate_quiz("sound")
            session["photo"] = generate_quiz("photo")
            return render_template("results.html", score=temp)
    return render_template("photo_quiz.html", num=session["num"], qz=session["photo"])


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(Exception)
def error_handle(error):
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player').replace('#', '-')}")
    e = error.code
    if e in errors:
        return render_template("error.html", message=errors[e][0],
                               img=errors[e][1], alt=errors[e][2],
                               error=errors[e][3])
    else:
        return render_template("error.html", message="Something went wrong :(",
                               img="/static/img/what.gif", alt="Doctor's confused",
                               error=f"{error.code} {error.name}")


@app.route("/raise_error")
def raise_error():
    raise werkzeug.exceptions.BadRequest


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
