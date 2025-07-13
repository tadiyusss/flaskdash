from core.models import User
from core.extensions import db
import random
import string

def random_string(length=10):    
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def test_dashboard_home_unauthenticated(client):
    response = client.get('/dashboard/home')
    assert response.status_code == 302

def test_dashboard_logout_unauthenticated(client):
    response = client.get('/dashboard/logout')
    assert response.status_code == 302

def test_register_wrong_email(client):
    response = client.post('/dashboard/register', data={
        'username': 'testuser',
        'email': 'invalid-email',
        'password': 'password123',
        'retype_password': 'password123'
    })
    print(response.get_data(as_text=True))
    assert 'Invalid email address.' in response.get_data(as_text=True)

def test_register_password_mismatch(client):
    response = client.post('/dashboard/register', data={
        'username': 'testuser',
        'email': 'valid_email_test@gmail.com',
        'password': 'password123',
        'retype_password': 'differentpassword'
    })
    print(response.get_data(as_text=True))
    assert 'Passwords do not match.' in response.get_data(as_text=True)

def test_create_user(client):
    response = client.post('/dashboard/register', data={
        'username': 'newuser',
        'email': 'john_doe@example.com',
        'password': 'securepassword',
        'retype_password': 'securepassword'
    })
    assert response.status_code == 302  # Should redirect after successful registration
    assert User.query.filter_by(username='newuser').first() is not None

def test_existing_user_registration(client):
    # First create a user
    username = f'user_{random_string(5)}'
    email = f'{random_string(4)}.{random_string(4)}@gmail.com'
    password = f'securepassword_{random_string(4)}'
    client.post('/dashboard/register', data={
        'username': username,
        'email': email,
        'password': password,
        'retype_password': password
    })

    client.get('/dashboard/logout')  # Ensure the user is logged out

    # Attempt to register the same user again
    response = client.post('/dashboard/register', data={
        'username': username,
        'email': email,
        'password': password,
        'retype_password': password
    })
    assert 'Username already exists.' in response.get_data(as_text=True)

def test_existing_email_registration(client):
    # First create a user
    username = f'user_{random_string(5)}'
    email = f'{random_string(4)}.{random_string(4)}@gmail.com'
    password = f'securepassword_{random_string(4)}'
    client.post('/dashboard/register', data={
        'username': username,
        'email': email,
        'password': password,
        'retype_password': password
    })

    client.get('/dashboard/logout')  # Ensure the user is logged out

    # Attempt to register with the same email but different username
    response = client.post('/dashboard/register', data={
        'username': f'new_{username}',
        'email': email,
        'password': password,
        'retype_password': password
    })
    assert 'Email already exists.' in response.get_data(as_text=True)

def test_login_with_invalid_credentials(client):
    client.get('/dashboard/logout')  # Ensure the user is logged out
    response = client.post('/dashboard/', data={
        'email': 'random@gmail.com',
        'password': 'wrongpassword'
    })
    print(response.get_data(as_text=True))
    assert 'Invalid email or password.' in response.get_data(as_text=True)

def test_login_with_valid_credentials(client):
    # First create a user
    client.get('/dashboard/logout')  # Ensure the user is logged out
    username = f'user_{random_string(5)}'
    email = f'{random_string(4)}.{random_string(4)}@gmail.com'
    password = f'securepassword_{random_string(4)}'
    client.post('/dashboard/register', data={
        'username': username,
        'email': email,
        'password': password,
        'retype_password': password
    })
    
    client.get('/dashboard/logout')  # Ensure the user is logged out

    # Now try to log in with the created user
    response = client.post('/dashboard/', data={
        'email': email,
        'password': password
    })
    assert response.status_code == 302  # Should redirect after successful login
    assert User.query.filter_by(email=email).first() is not None
