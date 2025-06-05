import pytest
from app import create_app, db
from app.config import Config
from app.models import Test


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


def test_ensure_career_test_created(app):
    with app.app_context():
        assert Test.query.filter_by(type="career").count() == 1
