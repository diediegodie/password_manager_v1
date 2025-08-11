import pytest
from backend.app import create_app
from backend.vault.services import VaultService
from unittest.mock import patch


class DummyAuthProvider:
    """Simulates real JWT checks for negative/edge cases."""

    def __init__(self, fail=False, expired=False):
        self.fail = fail
        self.expired = expired

    def require_auth(self, fn):
        def wrapper(*args, **kwargs):
            if self.fail:
                from flask import jsonify

                return jsonify({"msg": "Missing or invalid token"}), 401
            if self.expired:
                from flask import jsonify

                return jsonify({"msg": "Token expired"}), 401
            return fn(*args, **kwargs)

        return wrapper

    def get_identity(self):
        return 1

    def create_access_token(self, identity):
        return "test-token"


@pytest.fixture
def app_auth():
    app = create_app()
    app.config["TESTING"] = True
    return app


def test_vault_access_normal(app_auth):
    app_auth.config["AUTH_PROVIDER"] = DummyAuthProvider()
    client = app_auth.test_client()
    with patch.object(VaultService, "list_entries", return_value=[]):
        resp = client.get("/api/vault/")
        assert resp.status_code == 200


def test_vault_access_unauthenticated(app_auth):
    app_auth.config["AUTH_PROVIDER"] = DummyAuthProvider(fail=True)
    client = app_auth.test_client()
    resp = client.get("/api/vault/")
    assert resp.status_code == 401
    assert "invalid" in resp.get_json()["msg"]


def test_vault_access_expired_token(app_auth):
    app_auth.config["AUTH_PROVIDER"] = DummyAuthProvider(expired=True)
    client = app_auth.test_client()
    resp = client.get("/api/vault/")
    assert resp.status_code == 401
    assert "expired" in resp.get_json()["msg"]
