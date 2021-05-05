from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    grades_password = db.Column(db.Integer)
    echos = db.relationship('Echo', backref="owner", lazy="dynamic")

    def __repr__(self):
        return f'<User {self.username}>'

class Echo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    echo_id = db.Column(db.String(256), unique=True)
    code = db.Column(db.Integer)
    verified = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Echo {self.echo_id}>'