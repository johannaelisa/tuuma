from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email
from flask_login import current_user


class UserEditForm(FlaskForm):
    username = StringField('Nimi', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role_choices = [(1, 'User'), (8, 'Moderator'), (16, 'Admin')]
    role = SelectField('Rooli', choices=role_choices, coerce=int)
    submit = SubmitField('Päivitä')

class NewQuestionFormA(FlaskForm):
    country = HiddenField('Country', default=current_user.country if current_user else "")
    type_id = HiddenField('type_ID', default=1)
    question = StringField('Kysymys')
    primary_category = SelectField('Pääkategoria', choices=[
        ("aikajaavaruus", "Aika ja Avaruus"),
        ("luonnontieteet", "Luonnontieteet"),
        ("Ihmiselämä", "Ihmiselämä"),
        ("ihmisetjayhteiskunta", "Ihmiset ja yhteiskunta"),
        ("filosofiajauskonto", "Filosofia ja uskonto"),
        ("politiikkajaoikeus", "Politiikka ja oikeus"),
        ("tulevaisuudentutkimus", "Tulevaisuudentutkimus"),
        ("liiketoimintajatalous", "Liiketoiminta ja talous"),
        ("teknologia", "Teknologia"),
        ("ymparisto", "Ympäristö"),
        ("taidejaviihde", "Taide ja viihde"),
        ("urheilujavapaa-aika", "Urheilu ja vapaa-aika"),
    ], validators=[DataRequired()])
    status = HiddenField('Published', default="unpublished")
    user_id = HiddenField('User ID', default=current_user.id if current_user and current_user.is_authenticated else "")
    is_parent = HiddenField('Is Parent' , default=True)
    parent_id = HiddenField('Parent ID', default=0)
    children = HiddenField('Children', default=0)
    submit = SubmitField('Lähetä')
    
class EditMyProfileForm(FlaskForm):
    id = HiddenField('ID', default=current_user.id if current_user and current_user.is_authenticated else "")
    username = StringField('Nimi', validators=[DataRequired()])
    firstname = StringField('Etunimi', validators=[DataRequired()])
    lastname = StringField('Sukunimi', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Puhelinnumero', validators=[DataRequired()])
    country = SelectField('Maa', choices=[
        ("Finland", "Suomi"),
        ("Sweden", "Ruotsi"),
        ("Norway", "Norja"),
        ("Denmark", "Tanska"),
        ("Iceland", "Islanti"),
        ("Lithuania", "Liettua"),
        ("Latvia", "Latvia"),
        ("Estonia", "Viro")
    ], validators=[DataRequired()])
    submit = SubmitField('Päivitä')
    
        