from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email

class UserEditForm(FlaskForm):
    username = StringField('Nimi', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_active = BooleanField('Tila')
    role_choices = [(1, 'User'), (8, 'Moderator'), (16, 'Admin')]
    role = SelectField('Rooli', choices=role_choices, coerce=int)
    submit = SubmitField('Päivitä')