#wipes all entries from the database

#this is needed to import from a different directory
import sys
sys.path.append('..')
try:
    from app import db
    from app.models import User, Echo
except:
    print("ERROR: Please navigate into tools directory before use.")
    raise 

users = User.query.all()
echos = Echo.query.all()

for u in users:
    db.session.delete(u)

for e in echos:
    db.session.delete(e)

db.session.commit()