import pytest


from unittest.mock import patch


@patch("backend.vault.services.VaultService.list_entries")
def test_list_entries(mock_list, client):
    mock_list.return_value = [
        {"id": 1, "encrypted_entry": "abc"},
        {"id": 2, "encrypted_entry": "def"},
    ]
    resp = client.get("/api/vault/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "entries" in data
    assert len(data["entries"]) == 2


@patch("backend.vault.services.VaultService.add_entry")
def test_add_entry(mock_add, client):
    mock_add.return_value = {"id": 3, "encrypted_entry": "xyz"}
    resp = client.post("/api/vault/", json={"encrypted_entry": "xyz"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["encrypted_entry"] == "xyz"


@patch("backend.vault.services.VaultService.get_entry")
def test_get_entry_found(mock_get, client):
    mock_get.return_value = {"id": 1, "encrypted_entry": "abc"}
    resp = client.get("/api/vault/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == 1


def test_get_entry_not_found(client):
    with patch(
        "backend.vault.services.VaultService.get_entry", return_value=None
    ), patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda *a, **kw: None,
    ), patch(
        "flask_jwt_extended.get_jwt_identity", return_value=1
    ):
        resp = client.get("/api/vault/999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data


@patch("backend.vault.services.VaultService.update_entry")
def test_update_entry_found(mock_update, client):
    mock_update.return_value = {"id": 1, "encrypted_entry": "updated"}
    with patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda *a, **kw: None,
    ), patch("flask_jwt_extended.get_jwt_identity", return_value=1):
        resp = client.put("/api/vault/1", json={"encrypted_entry": "updated"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["encrypted_entry"] == "updated"


def test_update_entry_not_found(client):
    with patch(
        "backend.vault.services.VaultService.update_entry", return_value=None
    ), patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda *a, **kw: None,
    ), patch(
        "flask_jwt_extended.get_jwt_identity", return_value=1
    ):
        resp = client.put("/api/vault/999", json={"encrypted_entry": "nope"})
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data


@patch("backend.vault.services.VaultService.delete_entry")
def test_delete_entry_found(mock_delete, client):
    mock_delete.return_value = True
    with patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda *a, **kw: None,
    ), patch("flask_jwt_extended.get_jwt_identity", return_value=1):
        resp = client.delete("/api/vault/1")
        assert resp.status_code == 204


def test_delete_entry_not_found(client):
    with patch(
        "backend.vault.services.VaultService.delete_entry", return_value=False
    ), patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda *a, **kw: None,
    ), patch(
        "flask_jwt_extended.get_jwt_identity", return_value=1
    ):
        resp = client.delete("/api/vault/999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data
