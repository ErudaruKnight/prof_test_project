import pytest
from flask import url_for
from app import create_app, db
from app.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


def register(client, username="testuser", password="password123", email="test@example.com"):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm": password,
            "birth_date": "2000-01-01",
            "is_student": "0",
        },
        follow_redirects=True,
    )


def test_login_success(client, app):
    register(client)
    resp = client.post(
        "/login",
        data={"username": "testuser", "password": "password123", "confirm": "password123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with app.test_request_context():
        assert resp.headers["Location"].endswith(url_for("main.index"))
