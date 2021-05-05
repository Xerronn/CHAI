import logging
from flask import Flask, render_template
from flask_ask import Ask
from config.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
ask = Ask(app, "/")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# logging.getLogger("flask_ask").setLevel(logging.DEBUG)
# log = logging.getLogger()

from app import routes, models
