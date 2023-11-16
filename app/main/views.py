from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import main
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from ..email import send_email
import secrets
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


#from flask_login import login_user, logout_user, login_required

@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        form.email.data = form.email.data.strip()
        form.password.data = form.password.data.strip()
        
        user = User.query.filter_by(email=form.email.data).first()
        
        if user.verify_password(form.password.data):
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
                return redirect(url_for('admin.index'))
            elif user.role == 8:
                return redirect(url_for('moderator.index'))
            else:
                return redirect(url_for('user.index'))

        return redirect(url_for('main.login'))
   
    return render_template('/auth/login.html', form=form)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
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
        send_email(user.email, 'Vahvista tilisi',
                     'auth/email/confirm', user=user, token=token)
        flash('Olet nyt rekisteröitynyt käyttäjä.')
        flash('Vahvistusviesti on lähetetty sähköpostiisi.')
        
        return redirect(url_for('main.thankyou'))
   
    return render_template('/auth/signup.html', form=form)

    

