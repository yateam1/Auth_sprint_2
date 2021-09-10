from functools import wraps

import jwt
from flask import request
from flask_restx import namespace

from app.services import UserService, RoleService, JWTService

user_service = UserService()
role_service = RoleService()


def login_required(method):
    """
    Проверяем валидность access_token
    :param method:
    :return:
    """
    @wraps(method)
    def wrapper(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        try:
            JWTService.decode_token(access_token)
        except jwt.exceptions.DecodeError:
            return namespace.abort(401, 'Неверный формат токена.')
        except jwt.exceptions.ExpiredSignatureErro:
            return namespace.abort(401, 'Срок действия токен истек.')

        return method(args, **kwargs)
    return wrapper


def does_user_have_role(role_name):
    """
    Проверяем принадлежность пользователя роли.
    Данный декоратор применять после декоратора login_required.
    :param role_name:
    :return:
    """
    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            access_token = request.headers.get('Authorization')
            decode_token = JWTService.decode_token(access_token)
            if role_name not in decode_token['roles']:
                return namespace.abort(403, f'Пользователю не назначена роль {role_name}')

            return method(args, **kwargs)
        return wrapper
    return decorator
