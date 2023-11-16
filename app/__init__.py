from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # Tarkista, onko db-muuttuja jo alustettu
    global db
    if db is None:
        db = SQLAlchemy(app)
    else:
        db.init_app(app)

    # Määritä tietokantataulut ja niiden mallit tässä
    with app.app_context():
        db.create_all()

    # Copilot, attach routes and custom error pages here
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
