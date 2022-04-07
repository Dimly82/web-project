from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, FileField, IntegerField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):
    id = IntegerField()
    nickname = StringField('Nickname', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    battle_tag = StringField('BattleTag')
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    avatar = FileField("Avatar")
    submit = SubmitField('Save Changes')
