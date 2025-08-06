# Ensure app.py imports the auth blueprint.
from flask import Flask
from backend.auth import auth_blueprint


def create_app():
    app = Flask(__name__)
    
    # Register the auth blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    # Run the Flask application
    # This will start the server with debug mode enabled for development purposes.