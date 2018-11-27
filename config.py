import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME')
    GITHUB_REPO_NAME = os.environ.get('GITHUB_REPO_NAME')
    SERVICE_TOKEN = os.environ.get('SERVICE_TOKEN')

    # Variables for sending email notifications on comment submission
    EMAIL_NOTIFICATION = os.environ.get('EMAIL_NOTIFICATION') or 'no'
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    EMAIL_TO = os.environ.get('EMAIL_TO')

    # Variables for SMTP emailing of logging errors
    LOGGING_EMAIL_NOTIFY = os.environ.get('LOGGING_EMAIL_NOTIFY') or 'no'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = int(os.environ.get('MAIL_USE_TLS')) or 0
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    LOGGING_EMAIL_TO = os.environ.get('LOGGING_EMAIL_TO')
