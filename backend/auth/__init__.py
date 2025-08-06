from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__)

# Import routes to register them with the blueprint (if routes.py exists)
try:
    from . import routes  # noqa: F401
except ImportError:
    pass