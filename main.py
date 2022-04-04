import os

from flask import Flask, render_template, request, redirect

from data import db_session
from data.__all_models import *
from data.register_form import RegisterForm

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST" and request.form.get('player'):
        return redirect(f"/search/{request.form.get('player')}")
    return render_template("index.html")


@app.route("/search/<string:player>")
def search(player):
    return render_template("search.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_form.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register_form.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register_form.html', title='Регистрация', form=form)


if __name__ == '__main__':
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    db_session.global_init("db/users.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
