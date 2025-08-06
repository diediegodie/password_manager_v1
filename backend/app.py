# Ensure app.py imports the auth blueprint.

from flask import Flask, jsonify
from backend.auth import auth_blueprint
from backend.auth.validators import ValidationError
from backend.auth.exceptions import DuplicateEmailError


def create_app():
    app = Flask(__name__)

    # Register the auth blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    # Centralized error handlers for all blueprints
    def handle_validation_error(error):
        return jsonify({"error": str(error)}), 400

    def handle_duplicate_email_error(error):
        return jsonify({"error": str(error)}), 409

    def handle_generic_error(error):
        # Optionally log error here
        return jsonify({"error": "Internal server error."}), 500

    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(DuplicateEmailError, handle_duplicate_email_error)
    app.register_error_handler(Exception, handle_generic_error)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
    # Run the Flask application
    # This will start the server with debug mode enabled for development purposes.
