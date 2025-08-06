from flask import request, jsonify, Blueprint, current_app
from backend.auth.validators import (
    RegistrationValidator,
    EmailValidator,
    PasswordValidator,
    ValidationError,
)
from .repository import UserRepository
from .hashing import BcryptPasswordHasher
from ..utils.db import SQLiteConnection
from .interfaces import IRegistrationValidator, IUserRepository, IPasswordHasher
from backend.auth.exceptions import DuplicateEmailError, DatabaseError, HashingError

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register_user_route():
    """
    User registration endpoint.
    Expects JSON: { "email": "...", "password": "..." }
    Returns:
        201: Success
        400: Validation error or malformed input
        409: Email already exists
        500: Internal error
    """
    validator = current_app.config.get(
        "REGISTRATION_VALIDATOR"
    ) or RegistrationValidator(EmailValidator(), PasswordValidator())
    user_repo = current_app.config.get("USER_REPOSITORY") or UserRepository(
        SQLiteConnection()
    )
    hasher = current_app.config.get("PASSWORD_HASHER") or BcryptPasswordHasher()

    try:
        data = request.get_json(silent=True)
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Missing email or password."}), 400

        email = data["email"]
        password = data["password"]

        # Validate input
        try:
            validator.validate(email, password)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        # Check if email exists
        if user_repo.is_email_taken(email):
            return jsonify({"error": "Email already registered."}), 409

        # Hash password and create user
        password_hash = hasher.hash(password)
        user_repo.create_user(email, password_hash)

        return jsonify({"message": "User registered successfully."}), 201

    except DuplicateEmailError:
        return jsonify({"error": "Email already registered."}), 409
    except (DatabaseError, HashingError) as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"error": f"Registration error: {str(e)}"}), 500
