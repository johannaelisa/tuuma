from flask import current_app
from datetime import datetime, timedelta
from . import db, login_manager, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import unquote
from flask_login import UserMixin
from itsdangerous import URLSafeSerializer as Serializer
from flask_sqlalchemy import SQLAlchemy
import pytz
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Enum

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False) 
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    country = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    confirmed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    role = db.Column(db.Integer, default=1)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.role}', '{self.id}', '{self.country}', '{self.is_active}')"
    
    def generate_confirmation_token(self):
            s = Serializer(current_app.config['SECRET_KEY'], salt='some_salt_value')
            expiration_time = datetime.utcnow() + timedelta(days=1)
            expiration_time_utc = expiration_time.replace(tzinfo=pytz.UTC)
            return s.dumps({'confirm': self.id, 'exp': expiration_time_utc.isoformat()}).encode('utf-8')

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class SignupTokens(db.Model):
    __tablename__ = 'signup_tokens'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expiration_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=1).replace(tzinfo=pytz.UTC))

    def __repr__(self):
        return f"SignupToken('{self.id}', '{self.email}, '{self.token}, '{self.expiration_time}')"

class RememberMeTokens(db.Model):
    __tablename__ = 'remember_me_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expiration_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=30).replace(tzinfo=pytz.UTC))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"RememberMeToken('{self.id}', '{self.token}, '{self.expiration_time}')"

class PasswordResetTokens(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expiration_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"PasswordResetToken('{self.id}', '{self.token}', '{self.expiration_time}')"

class Cards(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(120), db.ForeignKey('users.country'), nullable=False)
    type_id = db.Column(db.Integer, nullable=False)
    primary_category = db.Column(Enum(
        "aikajaavaruus",
        "luonnontieteet",
        "Ihmiselämä",
        "ihmisetjayhteiskunta",
        "filosofiajauskonto",
        "politiikkajaoikeus",
        "tulevaisuudentutkimus",
        "liiketoimintajatalous",
        "teknologia",
        "ymparisto",
        "taidejaviihde",
        "urheilujavapaa-aika",
        name="primary_category"
    ), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="False")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_parent = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, nullable=True)
    children = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f"Card('{self.id}', '{self.value}, '{self.status}, '{self.children}')"
