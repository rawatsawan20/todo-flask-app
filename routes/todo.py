from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Todo, User
from db_ext import db
from utils.email_sender import send_todo_email

todo_bp = Blueprint("todo", __name__)

@todo_bp.route("/", methods=["POST"])
@jwt_required()
def create_todo():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    title = data.get("title")
    description = data.get("description")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    user_id = get_jwt_identity()

    todo = Todo(title=title, description=description, user_id=user_id)
    db.session.add(todo)
    db.session.commit()

    email_sent = False
    user = User.query.get(user_id)
    if user and user.email:
        email_sent = send_todo_email(user.email, title, description)

    return jsonify({
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "message": "Todo created successfully",
        "email_sent": email_sent
    }), 201

@todo_bp.route("/", methods=["GET"])
@jwt_required()
def get_todos():
    user_id = get_jwt_identity()

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 3, type=int)

    todos_query = Todo.query.filter_by(user_id=user_id).order_by(Todo.id.desc())
    total_todos = todos_query.count()
    todos = todos_query.offset((page - 1) * limit).limit(limit).all()

    todos_data = [
        {"id": t.id, "title": t.title, "description": t.description}
        for t in todos
    ]

    return jsonify({
        "todos": todos_data,
        "page": page,
        "limit": limit,
        "total": total_todos,
        "hasMore": (page * limit) < total_todos
    }), 200

@todo_bp.route("/<int:todo_id>", methods=["PUT"])
@jwt_required()
def update_todo(todo_id):
    user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    data = request.get_json()
    todo.title = data.get("title", todo.title)
    todo.description = data.get("description", todo.description)
    db.session.commit()

    return jsonify({"message": "Todo updated successfully"})

@todo_bp.route("/<int:todo_id>", methods=["DELETE"])
@jwt_required()
def delete_todo(todo_id):
    user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "Todo deleted successfully"})
