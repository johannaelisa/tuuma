from datetime import datetime, timedelta, timezone
from flask import current_app, redirect, url_for, flash, render_template
from .email import send_email
from base64 import urlsafe_b64decode, urlsafe_b64encode
from .models import Users, SignupTokens, RememberMeTokens
from flask_login import login_user
from . import db

def confirmation_token(user, db):
    token = None
    try:
        token = user.generate_confirmation_token()
        expiration_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=1))
        signup_token = SignupTokens(email=user.email,
                                token=token,
                                expiration_time=expiration_time.replace(tzinfo=timezone.utc))
        current_app.logger.info('Token: ' + token.decode('utf-8'))
        current_app.logger.info('Signup token: ' + str(signup_token))
        db.session.add(signup_token)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Virhe tokenin generoinnissa: {e}")
        db.session.rollback()
        flash('Rekisteröitymisessä tapahtui virhe. Yritä uudelleen.')

    if token is not None:
        encoded_token = urlsafe_b64encode(token).decode('utf-8')
        current_app.logger.info('Encoded token: ' + encoded_token)
        confirmation_link = url_for('main.confirm_email', token=encoded_token, _external=True)
        current_app.logger.info('Vahvistuslinkki: ' + confirmation_link)
        send_email(user.email, 'Vahvista tilisi', 'email/confirm', user=user, confirmation_link=confirmation_link)
        flash('Olet nyt rekisteröitynyt käyttäjä.')
        flash('Vahvistusviesti on lähetetty sähköpostiisi.')

def remember_me_token(user, db):
    token = None
    try:
        token = user.generate_remember_me_token()
        expiration_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=30))
        remember_me_token = RememberMeTokens(token=token,
                                expiration_time=expiration_time.replace(tzinfo=timezone.utc),
                                user_id=user.id)
        current_app.logger.info('Token: ' + token.decode('utf-8'))
        current_app.logger.info('Remember me token: ' + str(remember_me_token))
        db.session.add(remember_me_token)
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Virhe tokenin generoinnissa: {e}")
        db.session.rollback()
        flash('Kirjautumisessa tapahtui virhe. Yritä uudelleen.')
        return False

    
def is_valid_token(decoded_token):
    try:
        expiration_time = get_token_expiration_time(decoded_token)
        return expiration_time > datetime.utcnow()

    except Exception as e:
        current_app.logger.error(f"Tokenin voimassaolon tarkistuksessa tapahtui virhe: {str(e)}")
        return False

def get_token_expiration_time(decoded_token):
    expiration_time_str = decoded_token.split('_')[-1]
    expiration_time = datetime.strptime(expiration_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    return expiration_time + timedelta(days=1)

def check_user_and_redirect(current_user):    
    if current_user.is_authenticated:
        current_app.logger.info('Suoritetaan check_user_and_redirect-funktiota.')
        if check_is_active(current_user):
            current_app.logger.info('Käyttäjä on aktiivinen ehto totautui.')
            return redirect(url_for('auth.home', _external=True))


        else:
            flash('Kirjautuminen epäonnistui. Tarkista sähköposti ja salasana.')
            return redirect(url_for('main.login'))
        
        
def check_is_active(user):
    if user.is_active:
        current_app.logger.info('Käyttäjä on aktiivinen.')
        return True
    else:
        current_app.logger.info('Käyttäjä ei ole aktiivinen.')
        flash('Käyttäjätilisi ei ole aktiivinen.')
        return False
