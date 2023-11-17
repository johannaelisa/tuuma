from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField 
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired()])
    password = PasswordField('Salasana', validators=[DataRequired()])
    remember_me = BooleanField('Muista minut')
    submit = SubmitField('Kirjaudu')


class RegistrationForm(FlaskForm):
    firstname = StringField('Etunimi', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z-\'\\s]*$', 0,
               'Kirjoita oikea etunimi')])
    lastname = StringField('Sukunimi', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z-\'\\s]*$', 0,
               'Kirjoita oikea sukunimi')])
    phone = StringField('Puhelinnumero', validators=[
        DataRequired(), Length(1, 64),
        Regexp(r'^(\+\d{1,3})?\d{9,15}$', 0,
               'Kirjoita oikea puhelinnumero')])
    country = StringField('Maa', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z-\'\\s]*$', 0,
               'Kirjoita oikea maa')])
    email = StringField('Email', validators=[
        DataRequired(), Length(1, 64),
        Email()])             
    
    password = PasswordField('Salasana', validators=[
        DataRequired(), EqualTo('password2', message='Salasanojen tulee täsmätä.')])
    password2 = PasswordField('Vahvista salasana', validators=[DataRequired()])
    
    
    submit = SubmitField('Rekisteröidy')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Sähköposti on jo käytössä.')

class ConfirmEmailForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired()])
    submit = SubmitField('Lähetä vahvistusviesti uudelleen')
    
    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Sähköposti ei ole käytössä.')
