from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Todo, User
from db_ext import db
from utils.email_sender import send_todo_email

todo_bp = Blueprint("todo", __name__)

# Create Todo
@todo_bp.route("/", methods=["POST"])
def debug_create_todo():
    # Step 1 — Log headers and body immediately
    print("📩 HEADERS RECEIVED:", dict(request.headers))
    print("📩 RAW BODY:", request.get_data(as_text=True))

    # Step 2 — Check if Authorization header exists
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "No Authorization header found"}), 401

    # Step 3 — Now let JWT validate the token
    return create_todo_with_jwt()

@jwt_required()
def create_todo_with_jwt():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    title = data.get("title")
    description = data.get("description")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    user_id = get_jwt_identity()

    # ✅ Log todo creation start
    print(f"📝 Creating Todo for user_id={user_id}: {title} - {description}")

    # Save todo to DB
    todo = Todo(title=title, description=description, user_id=user_id)
    db.session.add(todo)
    db.session.commit()
    print("✅ Todo saved to database.")

    # Send email
    user = User.query.get(user_id)
    email_sent = False
    if user and user.email:
        email_sent = send_todo_email(user.email, title, description)
        if email_sent:
            print(f"📧 Email sent to {user.email}")
        else:
            print(f"❌ Failed to send email to {user.email}")
    else:
        print("⚠️ No email address found for this user.")

    return jsonify({
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "message": "Todo created successfully",
        "email_sent": email_sent
    }), 201




# Get all Todos
@todo_bp.route("/", methods=["GET"])
@jwt_required()
def get_todos():
    user_id = get_jwt_identity()
    
    # Get page & limit from query params
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 3, type=int)
    
    # Pagination query
    todos_query = Todo.query.filter_by(user_id=user_id).order_by(Todo.id.desc())
    total_todos = todos_query.count()
    todos = todos_query.offset((page - 1) * limit).limit(limit).all()
    
    # Convert to list of dicts
    todos_data = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description
        } for t in todos
    ]
    
    return jsonify({
        "todos": todos_data,
        "page": page,
        "limit": limit,
        "total": total_todos,
        "hasMore": (page * limit) < total_todos
    }), 200



# Update Todo
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


# Delete Todo
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
