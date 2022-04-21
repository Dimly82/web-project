from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField


class QuizSound(FlaskForm):
    radio = RadioField()
    submit = SubmitField('Next')
