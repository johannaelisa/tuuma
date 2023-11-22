from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..auth import auth
from .forms import UserEditForm
from .. import db, bcrypt
from ..models import Users
from ..email import send_email
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from ..decorators import admin_required

@auth.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    current_app.logger.info('home-reitille tultiin')
    if current_user.role == 1:
        return render_template('admin/dashboard.html')
    return render_template('auth/home.html')


@auth.route('/dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@auth.route('/editusers', methods=['GET', 'POST'])
@login_required
@admin_required
def editusers():
    users = Users.query.all()
    form = UserEditForm()

    if form.validate_on_submit():
        for user in users:
            user_form = UserEditForm(obj=user)
            if user_form.validate_on_submit():
                user_form.populate_obj(user)
                db.session.commit()
                flash('Käyttäjätiedot päivitetty.')
            else:
                flash('Lomakkeen validointi epäonnistui.', 'error')
                print(f'Virheet käyttäjälle {user.id}: {user_form.errors}')

        return redirect(url_for('auth.editusers'))

    return render_template('admin/editusers.html', form=form, users=users)

