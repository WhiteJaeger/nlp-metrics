from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class InputForm(FlaskForm):
    text_hypothesis = TextAreaField(validators=[DataRequired()])
    text_reference = TextAreaField(validators=[DataRequired()])
    text_pos = TextAreaField(validators=[DataRequired()])
