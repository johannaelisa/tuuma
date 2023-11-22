from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField, HiddenField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import Users


class LoginForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired()])
    password = PasswordField('Salasana', validators=[DataRequired()])
    remember_me = BooleanField('Muista minut')
    submit = SubmitField('Kirjaudu')

class PasswordResetForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired()])
    submit = SubmitField('Lähetä salasanan vaihtolinkki')

class PasswordResetForm2(FlaskForm):
    password = PasswordField('Uusi salasana', validators=[DataRequired()])
    confirm_password = PasswordField('Vahvista salasana', validators=[DataRequired(), EqualTo('password')])
    token = HiddenField('Token', validators=[DataRequired()])
    submit = SubmitField('Vaihda salasana')

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
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError('Sähköposti on jo käytössä.')

class ConfirmEmailForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired()])
    token = HiddenField('token') 
    submit = SubmitField('Vahvista sähköposti')
    
    def validate_email(self, field):
        if not Users.query.filter_by(email=field.data).first():
            raise ValidationError('Sähköposti ei ole käytössä.')
