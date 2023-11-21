from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..auth import auth
from .forms import UserForm
from .. import db, bcrypt
from ..models import Users
from ..email import send_email
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from ..decorators import admin_required

@auth.route('/auth', methods=['GET', 'POST'])
@login_required
def home():
    current_app.logger.info('home-reitille tultiin')
    if current_user.role == 1:
        return render_template('admin/dashboard.html')
    return render_template('auth/home.html')

@auth.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    current_app.logger.info('admin_dashboard-reitille tultiin')
    
    users = Users.query.all()
    user_forms = []
    
    for user in users:
        form = UserForm()
        form.populate_obj(user)
        user_forms.append(form)
    
    if request.method == 'POST':
        for form in user_forms:
            if form.validate_on_submit():
                form.populate_obj(form.user)
                flash(f'User {form.user.username} updated successfully', 'success')

    return render_template('admin/dashboard.html', users=users, user_forms=user_forms)
    