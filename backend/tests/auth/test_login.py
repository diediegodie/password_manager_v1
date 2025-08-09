"""
Tests for the /api/auth/login endpoint.
Covers: normal (valid login), edge (non-existent email), failure (wrong password, invalid email, missing fields).
Uses pytest and unittest.mock for DB mocking.
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "testsecretkey"
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def mock_user():
    return {
        "id": 1,
        "email": "user@example.com",
        "password_hash": "$2b$12$abcdefghijklmnopqrstuv",  # bcrypt hash stub
    }


def test_valid_login(app, client):
    mock_user_obj = mock_user()
    mock_user_repo = MagicMock()
    mock_user_repo.get_user_by_email.return_value = mock_user_obj
    mock_verify_password = MagicMock(return_value=True)

    with app.app_context():
        app.config["USER_REPOSITORY"] = mock_user_repo
        # Patch verify_password in the route's module context
        with patch("backend.auth.routes.verify_password", mock_verify_password):
            resp = client.post(
                "/api/auth/login",
                json={"email": "user@example.com", "password": "correctpassword"},
            )
            assert resp.status_code == 200
            data = resp.get_json()
            assert "access_token" in data
            assert data["user"]["email"] == "user@example.com"


def test_login_nonexistent_email(app, client):
    mock_user_repo = MagicMock()
    mock_user_repo.get_user_by_email.return_value = None
    with app.app_context():
        app.config["USER_REPOSITORY"] = mock_user_repo
        with patch("backend.auth.routes.verify_password", MagicMock()):
            resp = client.post(
                "/api/auth/login",
                json={"email": "notfound@example.com", "password": "irrelevant"},
            )
            assert resp.status_code == 401
            data = resp.get_json()
            assert "error" in data
            assert "Invalid email or password." in data["error"]


def test_login_wrong_password(app, client):
    mock_user_obj = mock_user()
    mock_user_repo = MagicMock()
    mock_user_repo.get_user_by_email.return_value = mock_user_obj
    mock_verify_password = MagicMock(return_value=False)
    with app.app_context():
        app.config["USER_REPOSITORY"] = mock_user_repo
        with patch("backend.auth.routes.verify_password", mock_verify_password):
            resp = client.post(
                "/api/auth/login",
                json={"email": "user@example.com", "password": "wrongpassword"},
            )
            assert resp.status_code == 401
            data = resp.get_json()
            assert "error" in data
            assert "Invalid email or password." in data["error"]


def test_login_invalid_email_format(client):
    resp = client.post(
        "/api/auth/login", json={"email": "notanemail", "password": "irrelevant"}
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    assert "Invalid email" in data["error"] or "format" in data["error"]


def test_login_missing_fields(client):
    resp = client.post("/api/auth/login", json={"email": "user@example.com"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    assert "Missing" in data["error"] or "required" in data["error"]
