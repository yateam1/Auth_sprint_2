import json
from uuid import uuid4

import pytest

from app.factories import RoleFactory, UserFactory


def test_create_role(test_app, test_db, user_admin_headers):
    client = test_app.test_client()

    role_data = {'name': 'subscriber'}
    resp = client.post(
        '/permissions/roles',
        data=json.dumps(role_data),
        content_type='application/json',
        headers=user_admin_headers
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201
    assert f'Роль {role_data["name"]} добавлена.' == data['message']


def test_create_role_without_required_fields(test_app, test_db, user_admin_headers):
    client = test_app.test_client()
    resp = client.post(
        '/permissions/roles',
        data=json.dumps({}),
        content_type='application/json',
        headers=user_admin_headers
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Input payload validation failed' == data['message']


def test_create_role_with_same_name(test_app, test_db, user_admin_headers):
    client = test_app.test_client()
    resp = client.post(
        '/permissions/roles',
        data=json.dumps({'name': 'admin'}),
        content_type='application/json',
        headers=user_admin_headers
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert f'Роль с именем admin уже существует.' == data['message']


def test_get_correct_role(test_app, test_db, user_admin_headers):
    role = RoleFactory()
    client = test_app.test_client()
    resp = client.get(
        f'/permissions/roles/{role.id}',
        content_type='application/json',
        headers=user_admin_headers
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert {
        'id': str(role.id),
        'name': role.name,
        'users': role.users,
        'created': role.created.isoformat(),
        'updated': role.updated,
    } == data


def test_get_incorrect_role(test_app, test_db, user_admin_headers):
    role_id = uuid4()
    client = test_app.test_client()
    resp = client.get(f'permissions/roles/{role_id}', content_type='application/json', headers=user_admin_headers)
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert f'Роли {role_id} не существует.' == data['message']


def test_patch_role(test_app, test_db, user_admin_headers):
    role = RoleFactory()
    client = test_app.test_client()
    new_role_name = f'{role.name}_'
    resp = client.patch(
        f'/permissions/roles/{role.id}',
        data=json.dumps({'name': new_role_name}),
        content_type='application/json',
        headers=user_admin_headers
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert f'Роль {role.id} обновлена.' == data['message']
    assert role.name == new_role_name


@pytest.mark.parametrize('postfix', ['', '/users'])
def test_patch_incorrect_role(test_app, test_db, postfix, user_admin_headers):
    role_id = uuid4()
    client = test_app.test_client()
    resp = client.patch(
        f'/permissions/roles/{role_id}{postfix}',
        data=json.dumps({'name': 'admin'}),
        content_type='application/json',
        headers=user_admin_headers
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert f'Роли {role_id} не существует.' == data['message']


def test_patch_role_same_name(test_app, test_db, user_admin_headers):
    role = RoleFactory()
    client = test_app.test_client()
    resp = client.patch(
        f'/permissions/roles/{role.id}',
        data=json.dumps({'name': role.name}),
        content_type='application/json',
        headers=user_admin_headers
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert f'Роль с именем {role.name} уже существует.' == data['message']


def test_patch_role_add_and_remove_users(test_app, test_db, user_admin_headers):
    role_users = UserFactory.create_batch(5, password='password')
    role = RoleFactory(users=role_users)
    new_users = UserFactory.create_batch(5, password='password')
    data = {
        'added_users': [user.username for user in new_users[1:]],
        'deleted_users': [user.username for user in role_users[1:]],
    }
    client = test_app.test_client()
    resp = client.patch(
        f'/permissions/roles/{role.id}/users',
        data=json.dumps(data),
        content_type='application/json',
        headers=user_admin_headers)
    assert [role_users[0], *new_users[1:]] == role.users
    assert resp.status_code == 201


@pytest.mark.parametrize('count', [1, 10, 0])
def test_get_list_roles(test_app, test_db, count, user_admin_headers):
    RoleFactory.create_batch(count)
    client = test_app.test_client()
    resp = client.get(f'permissions/roles', content_type='application/json', headers=user_admin_headers)
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert count + 1== len(data)   # + 1    - Добавляем роль из фикстурного admin пользователя
