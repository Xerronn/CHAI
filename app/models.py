from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    echo_id = db.Column(db.String(128))
    grades_password = db.Column(db.Integer)

    def __repr__(self):
        return f'<User {self.username}>' 