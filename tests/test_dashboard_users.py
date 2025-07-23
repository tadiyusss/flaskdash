from core.models import User

TestUser = {
    'username': 'deborahhouse',
    'firstname': 'Paul',
    'lastname': 'Fields',
    'email': 'vsanders@example.net',
    'password': 'bo*H3Wdovf',
    'role': 'admin'
}

def test_users_table(client):
    response = client.post('/dashboard/', data={
        'email': TestUser['email'],
        'password': TestUser['password']
    })

    response = client.get('/dashboard/users')
    assert response.status_code == 200

    assert TestUser['username'] in response.data.decode('utf-8')
    assert TestUser['firstname'] in response.data.decode('utf-8')
    assert TestUser['lastname'] in response.data.decode('utf-8')
    assert TestUser['email'] in response.data.decode('utf-8')

def test_users_create(client, db_session):
    response = client.post('/dashboard/users/create', data={
        'username': TestUser['username'],
        'firstname': TestUser['firstname'],
        'lastname': TestUser['lastname'],
        'email': TestUser['email'],
        'password': TestUser['password'],
        'role': TestUser['role']
    })

    assert response.status_code == 302  # Redirect after successful creation
    assert User.query.filter_by(username=TestUser['username']).first() is not None