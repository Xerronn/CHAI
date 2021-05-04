import os

#loaded in __init__.py
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chai-is-the-best-tea'