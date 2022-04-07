from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, FileField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):
    nickname = StringField('Nickname')
    email = EmailField('Email')
    battle_tag = StringField('BattleTag')
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    avatar = FileField("Avatar")
    submit = SubmitField('Save Changes')
