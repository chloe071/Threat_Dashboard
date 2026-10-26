"""Security regression tests: protected pages require login."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app, db
from models import User


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="test-user").first():
            u = User(username="test-user")
            u.set_password("correct-password")
            db.session.add(u)
            db.session.commit()
    with app.test_client() as c:
        yield c
    with app.app_context():
        User.query.filter_by(username="test-user").delete()
        db.session.commit()


def test_dashboard_redirects_anonymous_users(client):
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_indicator_detail_requires_login(client):
    resp = client.get("/indicator/1")
    assert resp.status_code in (302, 401)


def test_wrong_password_is_rejected(client):
    resp = client.post("/login", data={"username": "test-user", "password": "wrong"})
    assert resp.status_code == 200
    assert b"Invalid credentials" in resp.data


def test_correct_password_logs_in(client):
    resp = client.post("/login", data={"username": "test-user", "password": "correct-password"})
    assert resp.status_code == 302
