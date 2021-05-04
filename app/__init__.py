import logging
from flask import Flask, render_template
from flask_ask import Ask
from config.config import Config


app = Flask(__name__)
app.config.from_object(Config)
ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)
log = logging.getLogger()

from app import routes
