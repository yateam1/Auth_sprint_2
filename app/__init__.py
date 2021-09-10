from flask import Flask
from flask_migrate import Migrate

from app.api import api
from app.bcrypt import bcrypt
from app.db import db
from app.settings import config

migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app_settings = (
        config('APP_SETTINGS')
        if config('APP_SETTINGS', default=None)
        else f"app.settings.{config('FLASK_ENV').title()}Config"
    )
    app.config.from_object(app_settings)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    api.init_app(app)

    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app
