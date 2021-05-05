import logging
from config.config import Config
from flask import Flask, render_template
from flask_ask import Ask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
ask = Ask(app, "/ask")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

# logging.getLogger("flask_ask").setLevel(logging.DEBUG)
# log = logging.getLogger()

from app import routes, models
