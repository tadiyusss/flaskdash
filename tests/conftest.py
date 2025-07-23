import pytest
from core import create_app, db
from core.models import User
from config import TestingConfig
from faker import Faker

fake = Faker()

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.rollback()

@pytest.fixture
def fake_user(db_session):
    username = fake.user_name()
    firstname = fake.first_name()
    lastname = fake.last_name()
    email = fake.email()
    password = fake.password()

    user = User(firstname=firstname, lastname=lastname, email=email, password=password, username=username)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def client(app):
    return app.test_client()