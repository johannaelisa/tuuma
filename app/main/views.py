from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import main
from .forms import LoginForm, RegistrationForm, ConfirmEmailForm
from .. import db
from ..models import User, SignupToken
from ..email import send_email
import secrets
from flask_bcrypt import Bcrypt
from base64 import urlsafe_b64encode, urlsafe_b64decode

bcrypt = Bcrypt()

@main.route('/', methods=['GET', 'POST'])
def index():
    current_app.logger.info('Sovellus avattu pääsivulle.')
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))
    current_app.logger.info('Login-sivu avattu.')
    form = LoginForm()
    if form.validate_on_submit():
        form.email.data = form.email.data.strip()
        form.password.data = form.password.data.strip()
        
        user = User.query.filter_by(email=form.email.data).first()
        
        if user.check_password(form.password.data):
            session['username'] = user.username
            current_app.config['SESSION_COOKIE_SECURE'] = False
            current_app.config['SESSION_COOKIE_HTTPONLY'] = True
    
            if form.remember_me.data:
                remember_token = secrets.token_urlsafe(32)
                user.remember_token = remember_token
                current_app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365).total_seconds()
                expiration = datetime.utcnow() + timedelta(seconds=current_app.config['REMEMBER_COOKIE_DURATION'])
                                
                db.session.commit()
                session['remember_token'] = remember_token
            else:
                session['remember_token'] = None
                
            
            login_user(user, form.remember_me.data)
            if user.role == 16:
                return redirect(url_for('auth.admin'))
            elif user.role == 8:
                return redirect(url_for('auth.moderator'))
            else:
                return redirect(url_for('auth.home'))

        return redirect(url_for('main.login'))
   
    return render_template('auth/login.html', form=form)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    current_app.logger.info('Rekisteröitymissivu avattu.')
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Sähköposti on jo käytössä.')
            return redirect(url_for('main.signup'))
        
        generated_username = 'user_' + secrets.token_urlsafe(8)
        form.firstname.data = form.firstname.data.strip()
        form.lastname.data = form.lastname.data.strip()
        form.phone.data = form.phone.data.strip()
        form.country.data = form.country.data.strip()
        form.email.data = form.email.data.strip()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        user = User( username=generated_username,
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

        token = user.generate_confirmation_token()
        signup_token = SignupToken(user_id=user.id, token=token)
        db.session.add(signup_token)
        db.session.commit()
        
        encoded_token = urlsafe_b64encode(token).decode('utf-8')
        confirmation_link = url_for('main.confirm_email', token=encoded_token, _external=True)
        current_app.logger.info('Vahvistuslinkki: ' + confirmation_link)
        send_email(user.email, 'Vahvista tilisi', 'email/confirm', user=user, confirmation_link=confirmation_link)
        flash('Olet nyt rekisteröitynyt käyttäjä.')
        flash('Vahvistusviesti on lähetetty sähköpostiisi.')
        
        #return redirect(url_for('main.thankyou'))
   
    return render_template('/auth/signup.html', form=form)

from flask import render_template, redirect, url_for, flash


@main.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    current_app.logger.info('Sähköpostin vahvistussivu on avattu.')
    form = ConfirmEmailForm()
    decoded_token = urlsafe_b64decode(token).decode('utf-8')
    
    if form.validate_on_submit():
        email = form.email.data.strip()
        signup_token = SignupToken.query.filter_by(token=decoded_token).first()
        
        if signup_token:
            user = signup_token.user
            user.confirmed = True
            user.is_active = True
            db.session.commit()
            flash('Sähköposti vahvistettu onnistuneesti!')
            return redirect(url_for('main.index'))
    
    flash('Sähköpostin vahvistus epäonnistui. Tarkista linkki ja yritä uudelleen.')
    return render_template('confirm_email.html', form=form)



