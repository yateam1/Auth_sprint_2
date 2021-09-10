from flask_restx import Api

from app.api.v1 import (
    auth_namespace,
    permissions_namespace,
    ping_namespace,
    users_namespace,
)
api = Api(version='1.0', title='Auth API')

api.add_namespace(ping_namespace, path='/ping')
api.add_namespace(users_namespace, path='/users')
api.add_namespace(auth_namespace, path='/auth')
api.add_namespace(permissions_namespace, path='/permissions')
