import pytest


def test_get_authors_no_records(client):
    response = client.get('/api/v1/authors')
    expected_result = {
        'success': True,
        'data': [],
        'number_of_records': 0,
        'pagination': {
            'total_pages': 0,
            'total_records': 0,
            'current_page': '/api/v1/authors?page=1'
        }
    }
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.get_json() == expected_result


def test_get_authors(client, sample_data):
    response = client.get('/api/v1/authors')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['number_of_records'] == 5
    assert len(response_data['data']) == 5
    assert response_data['pagination'] == {
        'total_pages': 3,
        'total_records': 11,
        'current_page': '/api/v1/authors?page=1',
        'next_page': '/api/v1/authors?page=2'
    }


def test_get_authors_with_params(client, sample_data):
    response = client.get('/api/v1/authors?fields=first_name&sort=-id&page=2&limit=2')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['number_of_records'] == 2
    assert response_data['pagination'] == {
        "total_pages": 6,
        "total_records": 11,
        "current_page": "/api/v1/authors?page=2&fields=first_name&sort=-id&limit=2",
        "next_page": "/api/v1/authors?page=3&fields=first_name&sort=-id&limit=2",
        "previous_page": "/api/v1/authors?page=1&fields=first_name&sort=-id&limit=2"
    }
    assert response_data['data'] == [
        {
            "first_name": 'Andrzej'
        },
        {
            "first_name": 'Alice'
        }
    ]


def test_get_single_author(client, sample_data):
    response = client.get('/api/v1/authors/8')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['first_name'] == 'Alice'
    assert response_data['data']['last_name'] == 'Sebold'
    assert response_data['data']['birth_date'] == '06-09-1963'
    assert len(response_data['data']['books']) == 1


def test_get_single_author_not_found(client, sample_data):
    response = client.get('/api/v1/authors/15')
    response_data = response.get_json()
    assert response.status_code == 404
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data


def test_create_author(client, token, author):
    response = client.post('/api/v1/authors',
                           json=author,
                           headers={
                               "Authorization": f'Bearer {token}'
                           })
    response_data = response.get_json()
    expected_result = {
        "success": True,
        "data": {
            **author,
            "id": 1,
            "books": []
        }
    }
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data == expected_result

    response = client.get('/api/v1/authors/1')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data == expected_result


@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'first_name': 'Tomasz', 'last_name': 'Niemasz'}, 'birth_date'),
        ({'first_name': 'Tomasz', 'birth_date': '03-08-1998'}, 'last_name'),
        ({'last_name': 'Niemasz', 'birth_date': '03-08-1998'}, 'first_name')
    ]
)
def test_create_author_invalid_data(client, token,  data, missing_field):
    response = client.post('/api/v1/authors',
                           json=data,
                           headers={
                               "Authorization": f'Bearer {token}'
                           })
    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_create_author_missing_token(client, author):
    response = client.post('/api/v1/authors', json=author)
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data


def test_create_author_invalid_content_type(client, token, author):
    response = client.post('/api/v1/authors',
                           data=author,
                           headers={
                               'Authorization': f'Bearer {token}'
                           })
    response_data = response.get_json()
    assert response.status_code == 415
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert "Content Type must be application/json" in response_data['message']
