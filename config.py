import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    #basic flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    #SQLite DB in project root
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{os.path.join(BASE_DIR, 'threatintel.db')}"
    ) 
    SQLALCHEMY_TRACK_MODIFICATIONS = False