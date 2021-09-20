from _pytest.monkeypatch import resolve
from flask.wrappers import Response
import pytest
from app import app as flask_app
import pytest


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope='module')
def test_client():
    with app.test_client() as testing_client:
        yield testing_client

def test_async_login(test_client):
    response = test_client.get('/login')
    assert response.status_code == 200