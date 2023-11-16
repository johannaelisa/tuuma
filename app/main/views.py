from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import main
from .forms import LoginForm, RegistrationForm
from .. import db
#from ..models import User
#from flask_login import login_user, logout_user, login_required

@main.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        session['email'] = form.email.data
        session['password'] = form.password.data
        session['remember_me'] = form.remember_me.data
        session['known'] = form.known.data
        session['current_time'] = datetime.utcnow()

        return redirect(url_for('main.login'))
   
    return render_template('/auth/login.html', form=form)

# tehdään reitti signupille

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        session['firstname'] = form.firstname.data
        session['lastname'] = form.lastname.data
        session['phone'] = form.phone.data
        session['country'] = form.country.data
        session['email'] = form.email.data
        session['password'] = form.password.data
        session['known'] = form.known.data
        session['current_time'] = datetime.utcnow()

        return redirect(url_for('main.signup'))
   
    return render_template('/auth/signup.html', form=form)

    

#@main.route('/login', methods=['GET', 'POST'])
#def login():
#    form = LoginForm()
#    if form.validate_on_submit():
#        user = User.query.filter_by(email=form.email.data).first()
#        if user is not None and user.verify_password(form.password.data):
#            login_user(user, form.remember_me.data)
#            return redirect(request.args.get('next') or url_for('main.index'))
#        flash('Invalid username or password.')
#        return redirect(url_for('.login'))
#    return render_template('login.html', form=form)
