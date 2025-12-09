from app import app, db
from models import User

with app.app_context():
    print("Before:", User.query.all())

    u = User(username="analyst")
    u.set_password("test123")
    db.session.add(u)
    db.session.commit()

    print("After:", User.query.all())