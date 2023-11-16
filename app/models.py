from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False) 
    firstname = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    country = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    confirmed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    role = db.Column(db.Integer, default=0)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, nullable=False)
    type_id = db.Column(db.Integer, nullable=False)
    card_class = db.Column(db.String(20), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Card('{self.question}', '{self.timestamp}')"