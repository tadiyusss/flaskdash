from core.models import User

TestUser = {
    'username': 'deborahhouse',
    'firstname': 'Paul',
    'lastname': 'Fields',
    'email': 'vsanders@example.net',
    'password': 'bo*H3Wdovf',
    'role': 'Administrator'
}

SecondUser = {
    'username': 'jamesjohnson',
    'firstname': 'James',
    'lastname': 'Johnson',
    'email': 'jjohnson@example.net',
    'password': 'james123',
    'role': 'Viewer'
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
    response = client.post('/dashboard/', data={
        'email': TestUser['email'],
        'password': TestUser['password']
    })


    response = client.post('/dashboard/users/create', data={
        'username': SecondUser['username'],
        'firstname': SecondUser['firstname'],
        'lastname': SecondUser['lastname'],
        'email': SecondUser['email'],
        'password': SecondUser['password'],
        'role': SecondUser['role']
    })

    
    assert "User created successfully." in response.data.decode('utf-8')