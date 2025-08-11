# Ensure app.py imports the auth blueprint.


import os
from flask import Flask, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from backend.auth.routes import auth_bp as auth_blueprint
from backend.auth.validators import (
    ValidationError,
    EmailValidator,
    PasswordValidator,
    RegistrationValidator,
)
from backend.auth.exceptions import DuplicateEmailError
from backend.auth.hashing import BcryptPasswordHasher
from backend.auth.repository import UserRepository
from backend.utils.db import SQLiteConnection
from backend.vault.repository import VaultRepository
from backend.vault.services import VaultService
from backend.vault.interfaces import IVaultRepository, IVaultService

app = Flask(__name__)

# --- Dependency Wiring ---
# Database connection (shared for all repositories)
db_connection = SQLiteConnection()

# Repositories
user_repo = UserRepository(db_connection)
vault_repo = VaultRepository(db_connection)

# Services
vault_service = VaultService(vault_repo)

# Validators
email_validator = EmailValidator()
password_validator = PasswordValidator()
registration_validator = RegistrationValidator(email_validator, password_validator)

# Hasher
password_hasher = BcryptPasswordHasher()

# Auth Provider abstraction (simple wrapper for now)


# Auth Provider abstraction (simple wrapper for now)
class FlaskJWTAuthProvider:
    def require_auth(self, fn):
        return jwt_required()(fn)

    def get_identity(self):
        return get_jwt_identity()

    def create_access_token(self, identity):
        return create_access_token(identity=identity)


def create_app():
    app = Flask(__name__)

    # --- Dependency Wiring ---
    # Database connection (shared for all repositories)
    db_connection = SQLiteConnection()

    # Repositories
    user_repo = UserRepository(db_connection)
    vault_repo = VaultRepository(db_connection)

    # Services
    vault_service = VaultService(vault_repo)

    # Validators
    email_validator = EmailValidator()
    password_validator = PasswordValidator()
    registration_validator = RegistrationValidator(email_validator, password_validator)

    # Hasher
    password_hasher = BcryptPasswordHasher()

    # Auth Provider abstraction (simple wrapper for now)
    auth_provider = FlaskJWTAuthProvider()

    # Inject dependencies into app config
    app.config["USER_REPOSITORY"] = user_repo
    app.config["VAULT_SERVICE"] = vault_service
    app.config["PASSWORD_HASHER"] = password_hasher
    app.config["REGISTRATION_VALIDATOR"] = registration_validator
    app.config["AUTH_PROVIDER"] = auth_provider

    # Register blueprints
    app.register_blueprint(auth_blueprint, url_prefix="/api/auth")
    from backend.vault.routes import vault_bp

    app.register_blueprint(vault_bp)

    # Debug: print all registered routes
    print("\n[DEBUG] Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule}")
    print()

    # Load JWT secret from environment
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    jwt = JWTManager(app)

    # Centralized error handlers for all blueprints
    def handle_validation_error(error):
        app.logger.warning(f"Validation error: {error}")
        return jsonify({"error": str(error)}), 400

    def handle_duplicate_email_error(error):
        app.logger.info(f"Duplicate email error: {error}")
        return jsonify({"error": str(error)}), 409

    from backend.auth.exceptions import InvalidCredentialsError

    def handle_invalid_credentials_error(error):
        app.logger.info(f"Invalid credentials: {error}")
        return jsonify({"error": "Invalid email or password."}), 401

    def handle_generic_error(error):
        app.logger.error(f"Unhandled exception: {error}")
        return jsonify({"error": "Internal server error."}), 500

    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(DuplicateEmailError, handle_duplicate_email_error)
    app.register_error_handler(
        InvalidCredentialsError, handle_invalid_credentials_error
    )
    app.register_error_handler(Exception, handle_generic_error)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
    # Run the Flask application
    # This will start the server with debug mode enabled for development purposes.
