"""
Vault API routes: CRUD for password entries. JWT-protected.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.vault.services import VaultService
from backend.vault.repository import VaultRepository
from backend.utils.db import get_db

vault_bp = Blueprint("vault", __name__, url_prefix="/api/vault")

# Dependency injection
vault_service = VaultService(VaultRepository(get_db()))


@vault_bp.route("/", methods=["GET"])
@jwt_required()
def list_entries():
    user_id = get_jwt_identity()
    entries = vault_service.list_entries(user_id)
    # Each entry: {id, encrypted_entry}
    return jsonify({"entries": entries}), 200


@vault_bp.route("/", methods=["POST"])
@jwt_required()
def add_entry():
    user_id = get_jwt_identity()
    data = request.get_json()
    # Expect data['encrypted_entry'] (string)
    if "encrypted_entry" not in data:
        return jsonify({"error": "Missing encrypted_entry"}), 400
    entry = vault_service.add_entry(user_id, data)
    return jsonify(entry), 201


@vault_bp.route("/<int:entry_id>", methods=["GET"])
@jwt_required()
def get_entry(entry_id):
    user_id = get_jwt_identity()
    entry = vault_service.get_entry(user_id, entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    return jsonify(entry), 200


@vault_bp.route("/<int:entry_id>", methods=["PUT"])
@jwt_required()
def update_entry(entry_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    if "encrypted_entry" not in data:
        return jsonify({"error": "Missing encrypted_entry"}), 400
    entry = vault_service.update_entry(user_id, entry_id, data)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    return jsonify(entry), 200


@vault_bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def delete_entry(entry_id):
    user_id = get_jwt_identity()
    success = vault_service.delete_entry(user_id, entry_id)
    if not success:
        return jsonify({"error": "Entry not found"}), 404
    return "", 204
