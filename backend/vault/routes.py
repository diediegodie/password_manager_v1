"""
Vault API routes: CRUD for password entries. JWT-protected.
"""

from flask import Blueprint, request, jsonify, current_app


vault_bp = Blueprint("vault", __name__, url_prefix="/api/vault")


@vault_bp.route("/", methods=["GET"])
def list_entries():
    auth = current_app.config["AUTH_PROVIDER"]
    vault_service = current_app.config["VAULT_SERVICE"]

    @auth.require_auth
    def inner():
        user_id = auth.get_identity()
        password = request.args.get("password")
        entries = vault_service.list_entries(user_id, password=password)
        return jsonify({"entries": entries}), 200

    return inner()


@vault_bp.route("/", methods=["POST"])
def add_entry():
    auth = current_app.config["AUTH_PROVIDER"]
    vault_service = current_app.config["VAULT_SERVICE"]

    @auth.require_auth
    def inner():
        user_id = auth.get_identity()
        try:
            data = request.get_json(force=True, silent=True)
            print("[DEBUG] POST /api/vault/ data:", data)
            if not data:
                return jsonify({"error": "Request body must be JSON."}), 400
            password = data.get("password")
            entry_data = data.get("entry") or data
            if not password:
                return jsonify({"error": "Missing password for encryption"}), 400
            entry = vault_service.add_entry(user_id, entry_data, password=password)
            return jsonify(entry), 201
        except Exception as e:
            print("[DEBUG] Exception in POST /api/vault/:", e)
            raise

    return inner()


@vault_bp.route("/<int:entry_id>", methods=["GET"])
def get_entry(entry_id):
    auth = current_app.config["AUTH_PROVIDER"]
    vault_service = current_app.config["VAULT_SERVICE"]

    @auth.require_auth
    def inner():
        user_id = auth.get_identity()
        password = request.args.get("password")
        entry = vault_service.get_entry(user_id, entry_id, password=password)
        if not entry:
            return jsonify({"error": "Entry not found"}), 404
        return jsonify(entry), 200

    return inner()


@vault_bp.route("/<int:entry_id>", methods=["PUT"])
def update_entry(entry_id):
    auth = current_app.config["AUTH_PROVIDER"]
    vault_service = current_app.config["VAULT_SERVICE"]

    @auth.require_auth
    def inner():
        user_id = auth.get_identity()
        try:
            data = request.get_json(force=True, silent=True)
            print(f"[DEBUG] PUT /api/vault/{{entry_id}} data:", data)
            if not data:
                return jsonify({"error": "Request body must be JSON."}), 400
            password = data.get("password")
            entry_data = data.get("entry") or data
            if not password:
                return jsonify({"error": "Missing password for encryption"}), 400
            entry = vault_service.update_entry(
                user_id, entry_id, entry_data, password=password
            )
            if not entry:
                return jsonify({"error": "Entry not found"}), 404
            return jsonify(entry), 200
        except Exception as e:
            print(f"[DEBUG] Exception in PUT /api/vault/{{entry_id}}:", e)
            raise

    return inner()


@vault_bp.route("/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    auth = current_app.config["AUTH_PROVIDER"]
    vault_service = current_app.config["VAULT_SERVICE"]

    @auth.require_auth
    def inner():
        user_id = auth.get_identity()
        success = vault_service.delete_entry(user_id, entry_id)
        if not success:
            return jsonify({"error": "Entry not found"}), 404
        return "", 204

    return inner()
