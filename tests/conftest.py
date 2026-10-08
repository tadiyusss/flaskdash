import pytest
from core import create_app, db
from core.models import User
from config import TestingConfig
from faker import Faker

fake = Faker()

@pytest.fixture
def app():
    app, _socket = create_app(TestingConfig)
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

@pytest.fixture
def admin_user(db_session):
    admin_username = fake.user_name()
    admin_firstname = fake.first_name()
    admin_lastname = fake.last_name()
    admin_email = fake.email()
    admin_password = fake.password()

    admin_user = User(firstname=admin_firstname, lastname=admin_lastname, email=admin_email, password=admin_password, username=admin_username)
    db_session.add(admin_user)
    db_session.commit()
    admin_user.set_roles(['Administrator'])

    return admin_user

@pytest.fixture
def normal_user(db_session):
    normal_username = fake.user_name()
    normal_firstname = fake.first_name()
    normal_lastname = fake.last_name()
    normal_email = fake.email()
    normal_password = fake.password()

    normal_user = User(firstname=normal_firstname, lastname=normal_lastname, email=normal_email, password=normal_password, username=normal_username)
    db_session.add(normal_user)
    db_session.commit()

    normal_user.set_roles(['User'])

    return normal_user