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
    EMAIL_NOTIFICATION = os.environ.get('EMAIL_NOTIFICATION') or "no"
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    EMAIL_TO = os.environ.get('EMAIL_TO')
