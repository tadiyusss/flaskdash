import random, string

def random_string(length=10):    
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

user = {
    'username': f'user_{random_string(5)}',
    'email': f'{random_string(4)}.{random_string(4)}@gmail.com',
    'password': f'securepassword_{random_string(4)}'
}

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

    # Now attempt to log in with the created user
    response = client.post('/dashboard/', data={
        'email': email,
        'password': password
    })
    
    assert response.status_code == 302  # Should redirect to dashboard
    assert response.location.endswith('/dashboard/home')  # Check redirect location

def test_dashboard_pages(client):

    client.post('/dashboard/register', data={
        'username': user['username'],
        'email': user['email'],
        'password': user['password'],
        'retype_password': user['password']
    })
    
    response = client.get('/dashboard/home')
    assert response.status_code == 200

    response = client.get('/dashboard/profile')
    assert response.status_code == 200

    response = client.get('/dashboard/settings')
    assert response.status_code == 200

    response = client.get('/dashboard/users')
    assert response.status_code == 200

    response = client.get('/dashboard/extensions')
    assert response.status_code == 200

    response = client.get('/dashboard/logout')
    assert response.status_code == 302  # Should redirect to login page