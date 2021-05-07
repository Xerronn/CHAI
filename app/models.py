from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    #initalizes the id, username, password, grades, echo information and token
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    grades_password = db.Column(db.Integer)
    echo = db.Column(db.Integer, db.ForeignKey('echo.id'))
    token = db.Column(db.String(128))

    #sets the password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    #makes sure that the password is correct
    def auth_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

   
class Echo(db.Model):
    #initializes the echo for use with the canvas applicaiton
    id = db.Column(db.Integer, primary_key=True)
    echo_id = db.Column(db.String(256), unique=True)
    code = db.Column(db.Integer)
    verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Echo {self.echo_id}>'
    
#for login session
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
