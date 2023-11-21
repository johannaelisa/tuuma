from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email

class UserForm(FlaskForm):
    username = StringField('Käyttäjä', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_active = BooleanField('Tila')
    role = SelectField('Rooli', choices=[('admin', 'Admin'), ('moderator', 'Moderator'), ('user', 'User')])

    field_order = ['username', 'email', 'is_active', 'role']
