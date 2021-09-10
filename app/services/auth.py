from random import randint
from typing import Optional
from datetime import datetime, timedelta

from flask_restx import namespace
from flask import request
import jwt

from app.settings import config
from app.models import User
from app.services.sessions import SessionService
from app.services.users import UserService


session_service = SessionService()
user_service = UserService()


class JWTService:

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, config("SECRET_KEY"), algorithms="HS256")

    @staticmethod
    def is_token_valid(token: str) -> bool:
        try:
            JWTService.decode_token(token)
        except jwt.exceptions.DecodeError:
            return False
        except jwt.exceptions.ExpiredSignatureError:
            return False
        return True

    @staticmethod
    def encode_token(user: Optional[User] = None,
                     expires: int = config('ACCESS_TOKEN_EXPIRATION', cast=int),
                     **kwargs) -> str:
        data = {
            'user_id': str(user.id),
            'roles': [role.name for role in user.roles],
            'is_super': user.is_super,
        } if user else kwargs

        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=expires),
            'iat': datetime.utcnow(),
            'jti': randint(1, 99999999999),
            **data,
        }
        return jwt.encode(
            payload, config('SECRET_KEY'), algorithm='HS256'
        )


def auth_decorator(method_to_decorate):
    def wrapper(self):
        self.get_headers()
        if not all((self.fingerprint, self.user_agent)):
            return namespace.abort(400, 'Не переданы обязательные заголовки.')
        return method_to_decorate(self) or self.generate_tokens(), self.code
    return wrapper


def refresh_decorator(method_to_decorate):
    def wrapper(self):
        post_data = request.get_json()
        refresh_token = post_data.get('refresh_token')
        print(refresh_token)
        if refresh_token and not JWTService.is_token_valid(refresh_token):
            return namespace.abort(400, f'Refresh-токен истек. Нужно залогиниться')
        return method_to_decorate(self)
    return wrapper


class AuthService:
    def __init__(self):
        self.fingerprint = None
        self.auth_header = None
        self.user = None
        self.user_agent = None
        self.code = 200

    def get_headers(self):
        self.fingerprint = request.headers.get('Fingerprint')
        self.user_agent = request.headers.get('User-Agent')
        self.auth_header = request.headers.get('Authorization')

    def generate_tokens(self):
        access_token = JWTService.encode_token(user=self.user)
        refresh_token = JWTService.encode_token(user=self.user, expires=config('REFRESH_TOKEN_EXPIRATION', cast=int))
        session = {
            'refresh_token': refresh_token,
            'user': self.user,
            'fingerprint': self.fingerprint,
            'user_agent': self.user_agent,
        }
        session_service.create(**session)
        return {'access_token': access_token, 'refresh_token': refresh_token}

    @auth_decorator
    def register(self):
        post_data = request.get_json()
        user = user_service.get_user_by_username(post_data.get('username'))
        if user:
            return namespace.abort(400, f'Пользователь {post_data["username"]} уже зарегистрирован.')
        self.user = user_service.create(**post_data)
        self.code = 201

    @auth_decorator
    def auth(self):
        post_data = request.get_json()
        username = post_data.get('username')
        password = post_data.get('password')
        self.user = user_service.get_user_by_username(username)
        if not (self.user and self.user.check_password(password)):
            return namespace.abort(404, f'Неверный пароль.')
        self.code = 200

    @auth_decorator
    @refresh_decorator
    def refresh(self):
        post_data = request.get_json()
        refresh_token = post_data.get('refresh_token')
        session = session_service.get_by_refresh_token(refresh_token=refresh_token,
                                                       fingerprint=self.fingerprint,
                                                       user_agent=self.user_agent)
        if not session:
            return namespace.abort(400, f'Refresh-токен истек, либо не существует. Нужно залогиниться')
        self.user = session.user
        self.code = 201
