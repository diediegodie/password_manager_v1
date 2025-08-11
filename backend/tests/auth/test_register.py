"""
Tests for user registration functionality.

This module contains tests for the user registration endpoint,
covering normal cases, edge cases, and failure cases.
"""


import pytest
import unittest.mock as mock
from backend.auth.validators import ValidationError
from backend.auth.interfaces import (
    IRegistrationValidator,
    IUserRepository,
    IPasswordHasher,
)
from backend.auth.exceptions import DuplicateEmailError, DatabaseError, HashingError





def test_register_success(app, client):
    """Normal case: Register with valid email/password."""
    # Mock dependencies
    mock_validator = mock.Mock(spec=IRegistrationValidator)
    mock_repo = mock.Mock(spec=IUserRepository)
    mock_hasher = mock.Mock(spec=IPasswordHasher)

    # Set up mock return values
    mock_repo.is_email_taken.return_value = False
    mock_hasher.hash.return_value = "hashed_password"

    # Inject mocks into the Flask app
    with app.app_context():
        app.config["REGISTRATION_VALIDATOR"] = mock_validator
        app.config["USER_REPOSITORY"] = mock_repo
        app.config["PASSWORD_HASHER"] = mock_hasher
    # Send request
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "Password123"},
    )
    # Assert API response
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully."
    # Assert mocked methods were called with correct values
    mock_validator.validate.assert_called_once_with(
        "test@example.com", "Password123"
    )
    mock_repo.is_email_taken.assert_called_once_with("test@example.com")
    mock_hasher.hash.assert_called_once_with("Password123")
    mock_repo.create_user.assert_called_once_with(
        "test@example.com", "hashed_password"
    )


def test_register_duplicate_email(app, client):
    """Edge case: Register with existing email."""
    # Mock dependencies
    mock_validator = mock.Mock(spec=IRegistrationValidator)
    mock_repo = mock.Mock(spec=IUserRepository)
    mock_hasher = mock.Mock(spec=IPasswordHasher)

    # Set up mock return values
    mock_repo.is_email_taken.return_value = True  # Email already exists

    # Inject mocks into the Flask app
    with app.app_context():
        app.config["REGISTRATION_VALIDATOR"] = mock_validator
        app.config["USER_REPOSITORY"] = mock_repo
        app.config["PASSWORD_HASHER"] = mock_hasher

        # Send request
        response = client.post(
            "/api/auth/register",
            json={"email": "existing@example.com", "password": "Password123"},
        )

        # Assert API response
        assert response.status_code == 409
        assert "already registered" in response.get_json()["error"].lower()

        # Assert validator was called but hasher and create_user were not
        mock_validator.validate.assert_called_once()
        mock_repo.is_email_taken.assert_called_once()
        mock_hasher.hash.assert_not_called()
        mock_repo.create_user.assert_not_called()


def test_register_invalid_data(app, client):
    """Failure case: Register with invalid email/weak password."""
    # Mock dependencies
    mock_validator = mock.Mock(spec=IRegistrationValidator)
    mock_repo = mock.Mock(spec=IUserRepository)
    mock_hasher = mock.Mock(spec=IPasswordHasher)

    # Set up validator to raise validation error
    mock_validator.validate.side_effect = ValidationError("Invalid email format")

    # Inject mocks into the Flask app
    with app.app_context():
        app.config["REGISTRATION_VALIDATOR"] = mock_validator
        app.config["USER_REPOSITORY"] = mock_repo
        app.config["PASSWORD_HASHER"] = mock_hasher

        # Send request
        response = client.post(
            "/api/auth/register",
            json={"email": "invalid-email", "password": "weak"},
        )

        # Assert API response
        assert response.status_code == 400
        assert "invalid email format" in response.get_json()["error"].lower()

        # Assert only validator was called
        mock_validator.validate.assert_called_once()
        mock_repo.is_email_taken.assert_not_called()
        mock_hasher.hash.assert_not_called()
        mock_repo.create_user.assert_not_called()


def test_register_database_error(app, client):
    """Test handling of database errors during registration."""
    # Mock dependencies
    mock_validator = mock.Mock(spec=IRegistrationValidator)
    mock_repo = mock.Mock(spec=IUserRepository)
    mock_hasher = mock.Mock(spec=IPasswordHasher)

    # Set up mock behavior
    mock_repo.is_email_taken.return_value = False
    mock_hasher.hash.return_value = "hashed_password"
    mock_repo.create_user.side_effect = DatabaseError("Database connection failed")

    # Inject mocks into the Flask app
    with app.app_context():
        app.config["REGISTRATION_VALIDATOR"] = mock_validator
        app.config["USER_REPOSITORY"] = mock_repo
        app.config["PASSWORD_HASHER"] = mock_hasher

        # Send request
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "Password123"},
        )

        # Assert API response
        assert response.status_code == 500
        assert "database connection failed" in response.get_json()["error"].lower()

        # Assert all methods were called as expected
        mock_validator.validate.assert_called_once()
        mock_repo.is_email_taken.assert_called_once()
        mock_hasher.hash.assert_called_once()
        mock_repo.create_user.assert_called_once()


def test_register_missing_fields(app, client):
    """Failure case: missing email or password in request data."""
    # Mock dependencies
    mock_validator = mock.Mock(spec=IRegistrationValidator)
    mock_repo = mock.Mock(spec=IUserRepository)
    mock_hasher = mock.Mock(spec=IPasswordHasher)

    # Inject mocks into the Flask app
    with app.app_context():
        app.config["REGISTRATION_VALIDATOR"] = mock_validator
        app.config["USER_REPOSITORY"] = mock_repo
        app.config["PASSWORD_HASHER"] = mock_hasher

        # Send request with missing password
        response = client.post(
            "/api/auth/register", json={"email": "user@example.com"}  # Missing password
        )

        # Assert API response
        assert response.status_code == 400
        assert "missing email or password" in response.get_json()["error"].lower()

        # Ensure no mock methods were called
        mock_validator.validate.assert_not_called()
        mock_repo.is_email_taken.assert_not_called()
        mock_hasher.hash.assert_not_called()
        mock_repo.create_user.assert_not_called()

        # Send request with missing email
        response = client.post(
            "/api/auth/register", json={"password": "Password123"}  # Missing email
        )

        # Assert API response
        assert response.status_code == 400
        assert "missing email or password" in response.get_json()["error"].lower()


def test_register_hashing_error(app, client):
    """Test handling of hashing errors during registration."""
    # Mock dependencies
    mock_validator = mock.Mock(spec=IRegistrationValidator)
    mock_repo = mock.Mock(spec=IUserRepository)
    mock_hasher = mock.Mock(spec=IPasswordHasher)

    # Set up mock behavior
    mock_repo.is_email_taken.return_value = False
    mock_hasher.hash.side_effect = HashingError("Failed to hash password")

    # Inject mocks into the Flask app
    with app.app_context():
        app.config["REGISTRATION_VALIDATOR"] = mock_validator
        app.config["USER_REPOSITORY"] = mock_repo
        app.config["PASSWORD_HASHER"] = mock_hasher

        # Send request
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "Password123"},
        )

        # Assert API response
        assert response.status_code == 500
        assert "failed to hash password" in response.get_json()["error"].lower()

        # Assert methods were called correctly
        mock_validator.validate.assert_called_once()
        mock_repo.is_email_taken.assert_called_once()
        mock_hasher.hash.assert_called_once()
        mock_repo.create_user.assert_not_called()
