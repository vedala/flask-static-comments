from flask import Flask
from config import Config
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)

if not app.debug:
    #
    # Logging errors email notifications
    #
    if app.config['LOGGING_EMAIL_NOTIFY'] == 'yes':
        auth = None
        secure = None

        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        if app.config['MAIL_USE_TLS']:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no_reply@flask_static_comments.com',
            toaddrs=[app.config['LOGGING_EMAIL_TO']],
            subject='Error encountered in flask static comments',
            credentials=auth,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    #
    # Logging INFO level messages to file
    #
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(
        'logs/flask_static_comments.log',
        maxBytes=51200,
        backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)sL%(lineno)d'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask Static Comments startup')

from static_comments_app import routes
