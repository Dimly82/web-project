from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    battle_tag = StringField('BattleTag', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')
