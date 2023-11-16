from flask_mail import Message

# Haetaan app/__init__.py tiedostosta luotu app-olio
from app import app, mail

# Haetaan config.py tiedostosta Flasky Adminin sähköpostiosoite ja lähettäjän nimi
from config import Config

# Haetaan render_template funktio, jolla voidaan lähettää sähköposti html-muodossa
from flask import render_template

# Luodaan funktio, joka lähettää sähköpostin
def send_email(to, subject, template, **kwargs):
    msg = Message(Config.FLASKY_MAIL_SUBJECT_PREFIX + subject,
                  sender=Config.FLASKY_MAIL_SENDER, recipients=[to])
    # Lähetetään sähköposti html-muodossa
    msg.html = render_template(template + '.html', **kwargs)
    # Lähetetään sähköposti teksti-muodossa
    msg.body = render_template(template + '.txt', **kwargs)
    # Lähetetään sähköposti
    mail.send(msg)