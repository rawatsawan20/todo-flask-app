from flask import jsonify
from flask_jwt_extended import JWTManager

# Store revoked token IDs
BLACKLIST = set()

jwt = JWTManager()

def register_jwt_callbacks(app):
    jwt.init_app(app)

    # 🔹 Token revocation check
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLACKLIST

    # 🔹 Token expired
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print("⚠️ Token expired for user:", jwt_payload.get("sub"))
        return jsonify({"msg": "Token has expired"}), 401

    # 🔹 Invalid token
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print("❌ Invalid token:", error)
        return jsonify({"msg": "Invalid token"}), 401

    # 🔹 Missing token
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print("🚫 Missing token:", error)
        return jsonify({"msg": "Missing token"}), 401
