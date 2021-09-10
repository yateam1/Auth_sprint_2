import pytest

from app import create_app, db
from app.services import JWTService

from app.factories import HeaderFactory, UserFactory, RoleFactory


@pytest.fixture(scope="module")
def test_app():
    app = create_app()
    app.config.from_object("app.settings.TestingConfig")
    with app.app_context():
        yield app


@pytest.fixture
def test_db():
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture
def auth_headers():
    return HeaderFactory().headers


@pytest.fixture
def user_headers(auth_headers):
    user = UserFactory(password='password')
    auth_headers['Authorization'] = JWTService.encode_token(user=user)
    return auth_headers


@pytest.fixture
def user_admin_headers(auth_headers):
    role = RoleFactory(name='admin')
    user = UserFactory(password='password', roles=[role, ])
    auth_headers['Authorization'] = JWTService.encode_token(user=user)

    return auth_headers


def get_user_id_from_token(token: str) -> dict:
    return JWTService.decode_token(token)['user_id']
