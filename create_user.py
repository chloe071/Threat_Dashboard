"""Create a local dashboard user. Usage: python create_user.py <username>"""
import sys
from getpass import getpass

from app import app, db
from models import User

if len(sys.argv) != 2:
    sys.exit("Usage: python create_user.py <username>")

username = sys.argv[1]
password = getpass("Password: ")
if len(password) < 8:
    sys.exit("Password must be at least 8 characters.")

with app.app_context():
    if User.query.filter_by(username=username).first():
        sys.exit(f"User {username!r} already exists.")
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print("Created user:", user.username)
