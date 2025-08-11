import pytest

from backend.app import create_app
from backend.vault.salt_utils import get_or_create_user_salt
import json


# NoOpAuthProvider disables JWT for tests
class NoOpAuthProvider:
    def require_auth(self, fn):
        return fn

    def get_identity(self):
        return 1

    def create_access_token(self, identity):
        return "test-token"


from backend.vault.repository import VaultRepository
from backend.utils.db import SQLiteConnection

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["AUTH_PROVIDER"] = NoOpAuthProvider()
    # Patch VAULT_SERVICE to use a real SQLite connection
    real_conn = SQLiteConnection().get_connection()
    app.config["VAULT_SERVICE"].repo = VaultRepository(real_conn)
    with app.app_context():
        get_or_create_user_salt(1)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def vault_password():
    return "testvaultpass123"


@pytest.fixture
def entry_data():
    return {"service": "github", "username": "octocat", "password": "supersecret"}


def test_add_and_get_entry(client, vault_password, entry_data):
    # Add entry
    resp = client.post(
        "/api/vault/",
        json={"entry": entry_data, "password": vault_password},
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp.status_code == 201
    entry = resp.get_json()
    assert "id" in entry
    entry_id = entry["id"]
    # Get entry (should be decrypted)
    resp2 = client.get(
        f"/api/vault/{entry_id}?password={vault_password}",
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert "decrypted" in data
    assert data["decrypted"]["service"] == entry_data["service"]
    assert data["decrypted"]["username"] == entry_data["username"]
    assert data["decrypted"]["password"] == entry_data["password"]


def test_get_entry_wrong_password(client, vault_password, entry_data):
    # Add entry
    resp = client.post(
        "/api/vault/",
        json={"entry": entry_data, "password": vault_password},
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp.status_code == 201
    entry = resp.get_json()
    entry_id = entry["id"]
    # Try to get with wrong password
    resp2 = client.get(
        f"/api/vault/{entry_id}?password=wrongpass",
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert data["decrypted"] is None


def test_list_entries_with_password(client, vault_password, entry_data):
    # Add entry
    resp = client.post(
        "/api/vault/",
        json={"entry": entry_data, "password": vault_password},
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp.status_code == 201
    # List entries
    resp2 = client.get(
        f"/api/vault/?password={vault_password}",
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert "entries" in data
    assert any(
        e.get("decrypted", {}).get("service") == entry_data["service"]
        for e in data["entries"]
    )


def test_add_entry_missing_password(client, entry_data):
    resp = client.post(
        "/api/vault/",
        json={"entry": entry_data},
        headers={"Authorization": "Bearer testtoken"},
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    assert "password" in data["error"]
