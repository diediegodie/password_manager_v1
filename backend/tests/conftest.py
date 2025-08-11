# conftest.py -- shared test fixtures for dependency injection
import pytest
from backend.app import create_app


class NoOpAuthProvider:
    """A test double for IAuthProvider that disables auth and returns a fixed user id."""

    def require_auth(self, fn):
        return fn

    def get_identity(self):
        return 1  # or any test user id

    def create_access_token(self, identity):
        return "test-token"


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["AUTH_PROVIDER"] = NoOpAuthProvider()
    return app


@pytest.fixture
def client(app):
    return app.test_client()
