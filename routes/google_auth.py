from datetime import timedelta
from flask import Blueprint, jsonify, redirect
from flask_dance.contrib.google import google
from flask_jwt_extended import create_access_token
from models import User
from db_ext import db

google_auth_bp = Blueprint("google_auth", __name__)

@google_auth_bp.route("/google/authorized")
def google_authorized():
    if not google.authorized:
        return jsonify({"error": "Google authorization failed"}), 401

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return jsonify({"error": "Failed to fetch Google user info"}), 400

    google_data = resp.json()
    email = google_data.get("email")
    name = google_data.get("name")

    if not email:
        return jsonify({"error": "No email returned by Google"}), 400

    # Create or fetch user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.commit()

    # ✅ Always use string identity for JWT
    token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
    print(f"✅ Created Google token for {email}")

    # Redirect to React with token in query
    return redirect(f"http://localhost:5173/todos?token={token}")
