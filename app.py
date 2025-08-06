from flask import Flask
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint
import os

from config import Config
from db_ext import db, mail
from jwt_callbacks import register_jwt_callbacks


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config["SECRET_KEY"]

    # Extensions
    db.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # JWT handlers
    register_jwt_callbacks(app)

    # Google OAuth
    google_bp = make_google_blueprint(
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        scope=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ],
        redirect_to="google_auth.google_authorized"
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    # Routes
    from routes.todo import todo_bp
    from routes.google_auth import google_auth_bp
    from routes.auth import auth_bp
    app.register_blueprint(todo_bp, url_prefix="/todos")
    app.register_blueprint(google_auth_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run()
