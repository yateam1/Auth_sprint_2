from flask_restx import Namespace, Resource, fields

from app.services import SessionService, UserService, AuthService


auth_namespace = Namespace('auth')

user_service = UserService()
session_service = SessionService()
auth_service = AuthService()


user = auth_namespace.model(
    'User',
    {
        'username': fields.String(required=True),
        'password': fields.String(required=True),
        'email': fields.String(required=True),
    }
)

login = auth_namespace.model(
    'Login User',
    {
        'username': fields.String(required=True),
        'password': fields.String(required=True),
    },
)

refresh_token = auth_namespace.model(
    'Refresh token', {'refresh_token': fields.String(required=True)}
)

tokens = auth_namespace.model(
    'Tokens',
    {
        'access_token': fields.String(required=True),
        'refresh_token': fields.String(required=True)
    }
)


class Register(Resource):
    @auth_namespace.marshal_with(tokens)
    @auth_namespace.expect(user, validate=True)
    @auth_namespace.response(201, 'Успех.')
    @auth_namespace.response(400, 'Не переданы обязательные заголовки.')
    @auth_namespace.response(400, 'Пользователь уже зарегистрирован.')
    def post(self):
        """Регистрация нового пользователя."""
        return auth_service.register()


class Auth(Resource):
    @auth_namespace.marshal_with(tokens)
    @auth_namespace.expect(login, validate=True)
    @auth_namespace.response(200, 'Успех.')
    @auth_namespace.response(400, 'Не переданы обязательные заголовки.')
    @auth_namespace.response(404, 'Неверный пароль.')
    def post(self):
        """Аутентификация пользователя."""
        return auth_service.auth()


class Refresh(Resource):
    @auth_namespace.marshal_with(tokens)
    @auth_namespace.expect(refresh_token, validate=True)
    @auth_namespace.response(201, 'Успех')
    @auth_namespace.response(400, 'Не переданы обязательные заголовки.')
    @auth_namespace.response(400, 'Refresh-токен истек, либо не существует')
    def post(self):
        """Генерация новых access и refresh токенов в обмен на корректный refresh-токен"""
        return auth_service.refresh()


auth_namespace.add_resource(Register, '/register')
auth_namespace.add_resource(Auth, '/login')
auth_namespace.add_resource(Refresh, '/refresh')
