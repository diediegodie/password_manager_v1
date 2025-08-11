from flask import request, jsonify, Blueprint, current_app
from backend.auth.validators import (
    ValidationError,
    validate_login_data,
)
from backend.auth.exceptions import DuplicateEmailError, DatabaseError, HashingError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login_user_route():
    """
    User login endpoint.
    Expects JSON: { "email": "...", "password": "..." }
    Returns:
        200: Success, returns JWT
        400: Validation error or malformed input
        401: Invalid credentials
        500: Internal error
    """
    user_repo = current_app.config["USER_REPOSITORY"]
    hasher = current_app.config["PASSWORD_HASHER"]
    auth_provider = current_app.config["AUTH_PROVIDER"]
    try:
        data = request.get_json(silent=True)
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Missing email or password."}), 400

        email = data["email"]
        password = data["password"]

        # Validate input
        try:
            validate_login_data(email, password)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        # Fetch user
        from backend.auth.exceptions import InvalidCredentialsError

        user = user_repo.get_user_by_email(email)
        if not user or not hasher.verify(password, user["password_hash"]):
            raise InvalidCredentialsError("Invalid email or password.")

        # Create JWT via auth provider abstraction
        access_token = auth_provider.create_access_token(identity=user["id"])
        return (
            jsonify(
                {
                    "access_token": access_token,
                    "user": {"id": user["id"], "email": user["email"]},
                }
            ),
            200,
        )

    except DatabaseError as e:
        current_app.logger.error(f"Login DB error: {str(e)}")
        return jsonify({"error": f"Login error: {str(e)}"}), 500


@auth_bp.route("/register", methods=["POST"])
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
    validator = current_app.config["REGISTRATION_VALIDATOR"]
    user_repo = current_app.config["USER_REPOSITORY"]
    hasher = current_app.config["PASSWORD_HASHER"]

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
