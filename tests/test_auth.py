import pytest


def test_registration(client):
    response = client.post('/api/v1/auth/register',
                           json={
                               "username": 'test',
                               "password": '123456',
                               "email": "test@gmail.com"
                           })
    response_data = response.get_json()
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['token']


@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'username': 'test', 'password': '123456'}, 'email'),
        ({'username': 'test', 'email': 'test@gmail.com'}, 'password'),
        ({'password': '123456', 'email': 'test@gmail.com'}, 'username')
    ]
)
def test_registration_invalid_data(client, data, missing_field):
    response = client.post('/api/v1/auth/register',
                           json=data)
    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_registration_invalid_content_type(client):
    response = client.post('/api/v1/auth/register',
                           data={
                               "username": 'test',
                               "password": '123456',
                               "email": "test@gmail.com"
                           })
    response_data = response.get_json()
    assert response.status_code == 415
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert 'Content Type must be application/json' in response_data['message']


def test_already_used_username(client, user):
    response = client.post('/api/v1/auth/register',
                           json={
                               "username": user['username'],
                               "password": '123456',
                               "email": "123@gmail.com"
                           })
    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data


def test_already_used_email(client, user):
    response = client.post('/api/v1/auth/register',
                           json={
                               "username": 'new_username',
                               "password": '123456',
                               "email": user['email']
                           })
    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data


def test_get_current_user(client, user, token):
    response = client.get('/api/v1/auth/me',
                          headers=dict(Authorization=f'bearer {token}'))
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['username'] == user['username']
    assert response_data['data']['email'] == user['email']
    assert 'id' in response_data['data']
    assert 'creation_date' in response_data['data']


def test_get_current_user_missing_token(client):
    response = client.get('/api/v1/auth/me')
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data


def test_update_user_password(client, user, token):
    response = client.put('/api/v1/auth/update/password', headers={'Authorization': f'bearer {token}'},
                          json={
                              "current_password": user['password'],
                              "new_password": '03081998'
                          })

    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert 'creation_date' in response_data['data']
    assert 'email' in response_data['data']
    assert 'id' in response_data['data']
    assert 'username' in response_data['data']


def test_update_user_incorrect_password(client, user, token):
    response = client.put('/api/v1/auth/update/password', headers={'Authorization': f'bearer {token}'},
                          json={
                              "current_password": user['password'],
                              "new_password": '0308'
                          })

    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'Length must be between 6 and 255.' in response_data['message']['new_password']


def test_update_user_data(client, user, token):
    response = client.put('/api/v1/auth/update/data', headers={'Authorization': f'bearer {token}'},
                          json={
                              "username": '03081998',
                              "email": 'test12345@gmial.com'
                          })

    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert 'creation_date' in response_data['data']
    assert 'email' in response_data['data']
    assert 'id' in response_data['data']
    assert 'username' in response_data['data']


def test_update_user_data_existing_username(client, user, token):
    response = client.put('/api/v1/auth/update/data', headers={'Authorization': f'bearer {token}'},
                          json={
                              "username": user['username'],
                              "email": 'test12345@gmial.com'
                          })

    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert f'User with username {user["username"]} already exists' in response_data['message']


def test_update_user_data_existing_email(client, user, token):
    response = client.put('/api/v1/auth/update/data', headers={'Authorization': f'bearer {token}'},
                          json={
                              "username": 'test123',
                              "email": user['email']
                          })

    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert f'User with email {user["email"]} already exists' in response_data['message']
