from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
import logging
from flask_bcrypt import Bcrypt

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    from .models import Users
    return Users.query.get(int(user_id))

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    app.config['TIMEZONE'] = 'Europe/Helsinki'
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    log_file = 'sovellusloki.log'
    logging.basicConfig(filename=log_file, level=logging.INFO)

    return app

from .main import views
from .auth import views
