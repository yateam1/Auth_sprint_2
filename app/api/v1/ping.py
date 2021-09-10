import datetime

from flask_restx import Namespace, Resource

from app.settings import config

ping_namespace = Namespace("ping")


class Ping(Resource):
    def get(self):
        return {
            'env': config('FLASK_ENV'),
            'now': str(datetime.datetime.now()),
            'message': 'pong',
            'status': 'success',
        }


ping_namespace.add_resource(Ping, "")
