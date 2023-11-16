from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import main, auth
from .. import db
from ..models import User


@auth.route('/auth/home', methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    current_app.logger.info('Sovellus avattu pääsivulle.')
    user = User.query.filter_by(username=session['username']).first()
    #cards = Card.query.filter_by(country_id=user.country).all()
