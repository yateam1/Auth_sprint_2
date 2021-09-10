import json
from uuid import uuid4

import pytest

from app.factories import HistoryFactory, UserFactory
from app.tests.conftest import get_user_id_from_token


def test_create_user(test_app, test_db):
        client = test_app.test_client()
        user_data = {
            'username': 'we1tkind',
            'email': 'sa@prg.re',
            'password': 'qwerty',
        }
        resp = client.post(
            '/users',
            data=json.dumps(user_data),
            content_type='application/json',
        )
        data = json.loads(resp.data.decode())
        assert resp.status_code == 201
        assert f'Пользователь {user_data["username"]} добавлен.' == data['message']


def test_create_user_with_same_username(test_app, test_db):
    client = test_app.test_client()
    user = UserFactory(password='123', username='user')
    resp = client.post(
        '/users',
        data=json.dumps(
            {
                'username': user.username,
                'email': 'sa@prg.re',
                'password': 'qwerty',
            }
        ),
        content_type='application/json',
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Такой пользователь уже зарегистрирован.' == data['message']


@pytest.mark.parametrize(
    'payload',
    [{'email': 'sa@prg.re', 'password': 'qwerty'},
     {'email': 'sa@prg.re', 'username': 'qwerty'},
     {},
     {'username': 'qwerty'},
     ],
)
def test_create_user_without_required_data(test_app, test_db, payload):
    client = test_app.test_client()
    resp = client.post(
        '/users',
        data=json.dumps(payload),
        content_type='application/json',
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Input payload validation failed' == data['message']


def test_random_password(test_app, test_db):
    password = 'password'
    first_user = UserFactory(password=password)
    second_user = UserFactory(password=password)
    assert first_user.password != password
    assert first_user.password != second_user.password


def test_get_correct_user(test_app, test_db):
    user = UserFactory(password='password')
    client = test_app.test_client()
    resp = client.get(f'/users/{user.id}', content_type='application/json')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert {
        'id': str(user.id),
        'active': user.active,
        'created': user.created.isoformat(),
        'updated': user.updated,
        'is_super': user.is_super,
        'username': user.username,
           } == data


def test_get_incorrect_user(test_app, test_db):
    user_id = uuid4()
    client = test_app.test_client()
    resp = client.get(f'/users/{user_id}', content_type='application/json')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert f'Пользователя {user_id} не существует.' == data['message']


@pytest.mark.parametrize('count', [1, 10, 0])
def test_get_list_users(test_app, test_db, count):
    UserFactory.create_batch(count, password='password')
    client = test_app.test_client()
    resp = client.get(f'/users', content_type='application/json')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert count == len(data)


def test_correct_change_password(test_app, test_db, user_headers):
    client = test_app.test_client()
    user_data = {
        'old_password': 'password',
        'new_password': 'new_password',
    }


    resp = client.patch(
        f'/users/{get_user_id_from_token(user_headers["Authorization"])}/change_password',
        data=json.dumps(user_data),
        content_type='application/json',
        headers=user_headers,
    )

    assert resp.status_code == 201


def test_incorrect_change_password(test_app, test_db, user_headers):
    client = test_app.test_client()
    user_data = {
        'old_password': 'abracadabra',
        'new_password': 'new_password',
    }

    resp = client.patch(
        f'/users/{get_user_id_from_token(user_headers["Authorization"])}/change_password',
        data=json.dumps(user_data),
        content_type='application/json',
        headers=user_headers,
    )

    assert resp.status_code == 404


def test_history_correct_user(test_app, test_db):
    client = test_app.test_client()
    user = UserFactory(password='password')
    history = HistoryFactory(user=user)
    resp = client.get(
        f'/users/{user.id}/history',
        content_type='application/json',
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert data[0]['fingerprint'] == history.fingerprint
    assert len(user.history) == 1


def test_history_inorrect_user(test_app, test_db):
    client = test_app.test_client()
    user_id = uuid4()
    resp = client.get(
        f'/users/{user_id}/history',
        content_type='application/json',
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert f'Пользователя {user_id} не существует.' == data['message']
