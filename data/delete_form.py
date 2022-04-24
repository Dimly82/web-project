from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class DeleteForm(FlaskForm):
    id = IntegerField()
    password = PasswordField('Your Password', validators=[DataRequired()])
    submit = SubmitField('Delete Account..')
