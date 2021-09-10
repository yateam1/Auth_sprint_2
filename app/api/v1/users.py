from flask import request
from flask_restx import Namespace, Resource, fields

from app.api.decorators import login_required
from app.services import UserService

user_service = UserService()
users_namespace = Namespace('users')


user = users_namespace.model(
    'User',
    {
        'id': fields.String(readOnly=True),
        'username': fields.String(required=True),
        'created': fields.DateTime(readOnly=True),
        'updated': fields.DateTime(readOnly=True),
        'active': fields.Boolean(),
        'is_super': fields.Boolean(readOnly=True),
    },
)

user_post = users_namespace.inherit(
    'User post', user, {
        'password': fields.String(required=True),
        'email': fields.String(required=True),
    }
)

passwords = users_namespace.model(
    'Passwords',
    {
        'old_password': fields.String(required=True),
        'new_password': fields.String(required=True),
    },
)

history = users_namespace.model(
    'History',
    {
        'fingerprint': fields.String(readOnly=True),
        'user_agent': fields.String(readOnly=True),
        'created': fields.DateTime(readOnly=True),
    }
)


class UserList(Resource):

    @users_namespace.marshal_with(user, as_list=True)
    def get(self):
        """Возвращает список всех пользователей."""
        return user_service.get_all(), 200

    @users_namespace.expect(user_post, validate=True)
    @users_namespace.response(201, 'Добавлен новый пользователь <user_username>.')
    @users_namespace.response(400, 'Пользователь уже зарегистрирован.')
    def post(self):
        """Добавляет нового пользователя."""
        post_data = request.get_json()
        response_object = {}

        user = user_service.get_user_by_username(post_data.get('username'))
        if user:
            response_object['message'] = 'Такой пользователь уже зарегистрирован.'
            return response_object, 400

        user_service.create(**post_data)
        response_object['message'] = f'Пользователь {post_data["username"]} добавлен.'
        return response_object, 201


class UserDetail(Resource):
    @users_namespace.marshal_with(user)
    @users_namespace.response(200, 'Успех.')
    @users_namespace.response(404, 'Пользователя <user_id> не существует.')
    def get(self, user_id):
        """Возвращает одного пользователя."""
        user = user_service.get_by_pk(user_id)
        if not user:
            users_namespace.abort(404, f'Пользователя {user_id} не существует.')
        return user, 200


class UserChangePassword(Resource):
    @users_namespace.marshal_with(user)
    @users_namespace.expect(passwords, validate=True)
    @users_namespace.response(201, 'Успех.')
    @users_namespace.response(404, 'Пользователя <user_id> не существует.')
    @login_required
    def patch(self, user_id):
        """Меняет у пользователя user_id пароль."""
        user = user_service.get_by_pk(user_id)

        post_data = request.get_json()

        old_password = post_data.get('old_password')
        if not user.check_password(old_password):
            users_namespace.abort(404, 'Неверный пароль.')

        new_password = post_data.get('new_password')
        user_service.update(user, password=new_password)

        return user, 201


class UserHistory(Resource):
    @users_namespace.marshal_with(history, as_list=True)
    @users_namespace.response(200, 'Успех.')
    @users_namespace.response(404, 'Пользователя <user_id> не существует.')
    def get(self, user_id):
        """Возвращает историю логинов пользователя."""
        user = user_service.get_by_pk(user_id)
        if not user:
            users_namespace.abort(404, f'Пользователя {user_id} не существует.')
        return user.history, 200


users_namespace.add_resource(UserList, '')
users_namespace.add_resource(UserDetail, '/<user_id>')
users_namespace.add_resource(UserChangePassword, '/<user_id>/change_password')
users_namespace.add_resource(UserHistory, '/<user_id>/history')

