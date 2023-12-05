from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import main
from .forms import LoginForm, RegistrationForm, ConfirmEmailForm, PasswordResetForm, PasswordResetForm2
from .. import db, bcrypt
from ..models import Users, SignupTokens, RememberMeTokens, PasswordResetTokens
from ..email import send_email
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from ..utils import confirmation_token, remember_me_token, check_user_and_redirect, check_is_active, new_password_token
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from ..main import main

@main.route('/', methods=['GET'])
def root():
    if current_user.is_authenticated:
        return check_user_and_redirect(current_user)
    return redirect(url_for('main.index'))


@main.route('/index', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return check_user_and_redirect(current_user)
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return check_user_and_redirect(current_user)
    
    if form.validate_on_submit():
        form.email.data = form.email.data.strip()
        form.password.data = form.password.data.strip()
        form.remember_me.data = form.remember_me.data
        
        user = Users.query.filter_by(email=form.email.data).first()
        remember_me = False
        
        if user and user.check_password(form.password.data) and check_is_active(user):
            if form.remember_me.data:
                remember_me = remember_me_token(user, db)  
            login_user(user, remember=remember_me, duration=None, force=False, fresh=True)
            return redirect(url_for('auth.home'))
        else:
            current_app.logger.info("Kirjautuminen epäonnistui.")
            flash('Kirjautuminen epäonnistui. Tarkista sähköposti ja salasana.')
            return redirect(url_for('main.login'))
    return render_template('auth/login.html', form=form)

@main.route('/logout', methods=['GET'])
@login_required
def logout():
    remember_me_token = RememberMeTokens.query.filter_by(user_id=current_user.id).first()
    logout_user()
    if remember_me_token:
        db.session.delete(remember_me_token)
        db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/newpassword', methods=['GET', 'POST'])
def newpassword():
    form = PasswordResetForm()
    if current_user.is_authenticated:
        return check_user_and_redirect(current_user)
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if not user.confirmed:
                current_app.logger.info('Käyttäjätiliä ei ole vahvistettu.')
                flash('Käyttäjätiliä ei ole vahvistettu. Tarkista sähköpostisi.')
                confirmation_token(user, db)
                return render_template('main/newpassword.html', form=form)
            
            # Väliaikainen käyttäjätilin aktivoiminen
            user.is_active = True
            db.session.commit()
            
            new_password_token(user, db)            
            flash('Salasanan vaihtolinkki lähetetty sähköpostiisi.')
            return redirect(url_for('main.index'))
        else:
            flash('Sähköpostia ei löytynyt.')
            return redirect(url_for('main.newpassword'))
    return render_template('main/newpassword.html', form=form)

@main.route('/confirmnewpassword/<token>', methods=['GET', 'POST'])
def confirmnewpassword(token):
    current_app.logger.info('Salasanan vaihtosivu avattu.')
    form = PasswordResetForm2()
    if request.method == 'GET':
        form.token.data = token
    try:
        decoded_token = urlsafe_b64decode(token)
    except Exception as e:
        current_app.logger.error(f"Virhe tokenin purkamisessa: {e}")
        return redirect(url_for('index'))
    
    
    new_password_token = PasswordResetTokens.query.filter_by(token=decoded_token).first()
    user = Users.query.filter_by(id=new_password_token.user_id).first() if new_password_token else None
    
    if new_password_token is None or new_password_token.expiration_time < datetime.utcnow():
        current_app.logger.error('Token on vanhentunut.')
        
        if new_password_token:
            db.session.delete(new_password_token)
            db.session.commit()

        if user:
            new_password_token(user, db)

        return redirect(url_for('index'))
    
    else:
        current_app.logger.info('Token on voimassa.')
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.add(user)
            db.session.commit()
            flash('Salasanasi on vaihdettu.')
            return redirect(url_for('main.login'))
        return render_template('main/confirmnewpassword.html', form=form)
    

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    current_app.logger.info('Rekisteröitymissivu avattu.')
    form = RegistrationForm()
    if current_user.is_authenticated:
        current_app.logger.info('Käyttäjä on jo kirjautunut sisään.')
        return check_user_and_redirect(current_user)
    if form.validate_on_submit():
        if Users.query.filter_by(email=form.email.data).first():
            flash('Sähköposti on jo käytössä.')
            return redirect(url_for('main.signup'))
        
        generated_username = 'user_' + secrets.token_urlsafe(8)
        form.firstname.data = form.firstname.data.strip()
        form.lastname.data = form.lastname.data.strip()
        form.phone.data = form.phone.data.strip()
        form.country.data = form.country.data.strip()
        form.email.data = form.email.data.strip()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        user = Users(username=generated_username,
                    firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    country=form.country.data,
                    password=hashed_password,
                    confirmed=False,
                    is_active=False,
                    role=1,
                    member_since=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        confirmation_token(user, db)

        return redirect(url_for('main.thankyou'))
    return render_template('/auth/signup.html', form=form)

@main.route('/thankyou', methods=['GET'])
def thankyou():
    current_app.logger.info('Kiitos-sivu avattu.')
    return render_template('main/thankyou.html')

@main.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    current_app.logger.info('Sähköpostin vahvistussivu on avattu.')
    form = ConfirmEmailForm() 
    if request.method == 'GET':
        form.token.data = token
    try:
        decoded_token = urlsafe_b64decode(token)
    except Exception as e:
        current_app.logger.error(f"Virhe tokenin purkamisessa: {e}")
        return redirect(url_for('index'))

    signup_token = SignupTokens.query.filter_by(token=decoded_token).first()
    email = signup_token.email if signup_token else None
    user = Users.query.filter_by(email=email).first() if signup_token else None
  
    if signup_token is None or signup_token.expiration_time < datetime.utcnow():
        current_app.logger.error('Token on vanhentunut.')
        
        if signup_token:
            db.session.delete(signup_token)
            db.session.commit()

        if user:
            confirmation_token(user, db)

        return redirect(url_for('index'))

    else:
        current_app.logger.info('Token on voimassa.')
        
        user.confirmed = True
        user.is_active = True
        db.session.add(user)
        db.session.commit()
        flash('Tilisi on nyt vahvistettu.')
        return redirect(url_for('main.login'))
