from pathlib import Path

from decouple import AutoConfig

BASE_DIR = Path(__file__).parent

config = AutoConfig(search_path=BASE_DIR.joinpath('config'))


class BasicConfig:
    SECRET_KEY = config('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (f'postgresql://{config("POSTGRES_USER")}:'
                               f'{config("POSTGRES_PASSWORD")}'
                               f'@db/{config("POSTGRES_DB")}')
    TESTING = False


class DevelopmentConfig(BasicConfig):
    DEBUG = True


class TestingConfig(BasicConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (f'postgresql://{config("POSTGRES_USER")}:'
                               f'{config("POSTGRES_PASSWORD")}'
                               f'@db/{config("POSTGRES_DB")}_test')


class ProductionConfig(BasicConfig):
    pass
