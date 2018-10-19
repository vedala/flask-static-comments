from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from static_comments_app import routes
