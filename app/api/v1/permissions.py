from flask import request
from flask_restx import Namespace, Resource, fields

from app.api.decorators import login_required, does_user_have_role
from app.services import RoleService, UserService
from app.api.v1.users import user

role_service = RoleService()
user_service = UserService()

permissions_namespace = Namespace('permissions')


role = permissions_namespace.model(
    'Role',
    {
        'id': fields.String(readOnly=True),
        'name': fields.String(required=True),
        'users': fields.List(fields.Nested(user), readonly=True),
        'created': fields.DateTime(readOnly=True),
        'updated': fields.DateTime(readOnly=True),
    },
)

updated_users = permissions_namespace.model(
    'Updated Users',
    {
        'added_users': fields.List(fields.String(required=True)),
        'deleted_users': fields.List(fields.String(required=True)),
    }
)


class RoleList(Resource):
    @permissions_namespace.marshal_with(role, as_list=True)
    @login_required
    @does_user_have_role('admin')
    def get(self):
        """Список всех ролей."""
        return role_service.get_all(), 200

    @permissions_namespace.expect(role, validate=True)
    @permissions_namespace.response(201, 'Добавлена новая роль <role_name>.')
    @permissions_namespace.response(400, 'Роль уже существует.')
    @login_required
    @does_user_have_role('admin')
    def post(self):
        """Добавление новой роли."""
        post_data = request.get_json()
        response = {}

        role = role_service.get_role_by_name(post_data.get('name'))
        if role:
            response['message'] = f'Роль с именем {post_data["name"]} уже существует.'
            return response, 400

        role_service.create(**post_data)
        response['message'] = f'Роль {post_data["name"]} добавлена.'
        return response, 201


class RoleDetail(Resource):
    @permissions_namespace.marshal_with(role)
    @permissions_namespace.response(200, 'Успех.')
    @permissions_namespace.response(404, 'Роли <role_id> не существует.')
    @login_required
    @does_user_have_role('admin')
    def get(self, role_id):
        """Возвращает одну роль."""
        role = role_service.get_by_pk(role_id)
        if not role:
            permissions_namespace.abort(404, f'Роли {role_id} не существует.')
        return role, 200

    @permissions_namespace.expect(role, validate=True)
    @permissions_namespace.response(200, "Роль <role_id> обновлёна.")
    @permissions_namespace.response(400, "Роль с именем <name> уже существует.")
    @permissions_namespace.response(404, "Роли <role_id> не существует.")
    @login_required
    @does_user_have_role('admin')
    def patch(self, role_id):
        """Обновление роли."""
        post_data = request.get_json()
        name = post_data.get('name')
        response_object = {}

        role = role_service.get_by_pk(role_id)
        if not role:
            permissions_namespace.abort(404, f'Роли {role_id} не существует.')

        if role_service.get_role_by_name(name):
            response_object['message'] = f'Роль с именем {name} уже существует.'
            return response_object, 400

        role_service.update(role, name=name)

        response_object['message'] = f'Роль {role_id} обновлена.'
        return response_object, 200


class RoleUsers(Resource):
    @permissions_namespace.marshal_with(role)
    @permissions_namespace.expect(updated_users, validate=True)
    @permissions_namespace.response(201, 'Пользователи обновлены.')
    @permissions_namespace.response(404, 'Роли <role_id> не существует.')
    @login_required
    @does_user_have_role('admin')
    def patch(self, role_id):
        """Добавляет/удаляет пользователей к роли."""
        role = role_service.get_by_pk(role_id)
        if not role:
            permissions_namespace.abort(404, f'Роли {role_id} не существует.')
        data = request.get_json()
        actual_usernames = {user.username for user in role.users}
        updated_usernames = (
            actual_usernames.union(set(data.get('added_users', [])))
                            .difference(set(data.get('deleted_users', [])))
        )
        users = user_service.get_by_usernames(updated_usernames)
        role_service.update(role, users=list(users))
        return role, 201


permissions_namespace.add_resource(RoleList, '/roles')
permissions_namespace.add_resource(RoleDetail, '/roles/<role_id>')
permissions_namespace.add_resource(RoleUsers, '/roles/<role_id>/users')
