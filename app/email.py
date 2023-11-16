from flask_mail import Message
from . import mail
from config import Config
from flask import render_template


def send_email(to, subject, template, **kwargs):
    msg = Message(Config.FLASKY_MAIL_SUBJECT_PREFIX + subject,
                  sender=Config.FLASKY_MAIL_SENDER, recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    msg.body = render_template(template + '.txt', **kwargs)
    mail.send(msg)