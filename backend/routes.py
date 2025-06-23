from flask import request, jsonify
from . import db
from .models import User, Ticket, Comment, TicketAssignment
from flask_login import login_required, current_user, login_user, logout_user
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

# ----------------------------
# Custom Decorator for Admin-Only Endpoints
# ----------------------------
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


# --------------------------------
# Developer Only Routes, For administrative functions.
# --------------------------------
@login_required
@app.route('/api/dev/elevate-user', methods=['POST'])
def elevate_user():
    # Only allow in development mode
    if app.config['FLASK_ENV'] != 'development':
        return jsonify({'error': 'Not allowed in production.'}), 403

    data = request.get_json()
    if not data or 'user_id' not in data or 'dev_password' not in data:
        return jsonify({'error': 'user_id and password required'}), 400

    if data['dev_password'] != os.getenv('ELEVATE_ADMIN_SECRET'):
        return jsonify({'error': 'Invalid password'}), 401

    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.role = 'admin'
    db.session.commit()

    return jsonify({'message': f"User {user.username} elevated to admin."}), 200




# --------------------------------
# User Authentication Endpoints
# --------------------------------

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=8)
    new_user = User(
        username=data['username'],
        password=hashed_password,
        role="standard" # Roles are either "standard", "admin" or "master", a standard account can be elevated to admin by the master account only.
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/api/login', methods=['POST'])
def login_user_endpoint():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        login_user(user)
        
        return jsonify({"message": "Logged in successfully!"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout_user_endpoint():
    logout_user()
    return jsonify({"message": "Logged out successfully!"}), 200

@app.route('/api/session', methods=['GET'])
@login_required
def get_session_info():
    return jsonify({
        "username": current_user.username,
        "role": current_user.role,
        "user_id" : current_user.id
    }), 200

# ----------------------
# Ticket Endpoints
# ----------------------

# GET all tickets.
# Admins see all; non-admins see only tickets where they have an assignment.
@app.route('/api/tickets', methods=['GET'])
@login_required
def get_tickets():
    if current_user.role == "admin":
        tickets = Ticket.query.all()
    else:
        # For standard users, only include tickets where they have an assignment.
        assigned_ticket_ids = [assign.ticket_id for assign in current_user.ticket_assignments]
        tickets = Ticket.query.filter(Ticket.id.in_(assigned_ticket_ids)).all()
    
    results = []
    for ticket in tickets:

        assigned_users = TicketAssignment.query.filter_by(ticket_id=ticket.id).all()
        assigned_users_list = [{"user_id": assign.user_id, "username": assign.user.username} for assign in assigned_users]

        results.append({
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'status': ticket.status,
            'creator_id': ticket.creator_id,
            'assigned_users' : assigned_users_list
        })
    return jsonify(results), 200

# POST: Create a new ticket.
# Only admins can create tickets. When creating, they must include an assignment to at least one user.
@app.route('/api/tickets', methods=['POST'])
@admin_required
def create_ticket():
    data = request.get_json()
    if not data or 'title' not in data or 'assigned_user_ids' not in data:
        return jsonify({"error": "Title and assigned_user_ids (as a list) are required"}), 400

    # Validate that each assigned user exists.
    assigned_users = []
    for user_id in data.get("assigned_user_ids"):
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with id {user_id} not found"}), 404
        assigned_users.append(user)

    new_ticket = Ticket(
        title=data.get("title"),
        description=data.get("description", ""),
        status=data.get("status", "Open"),
        creator_id=current_user.id  # The admin creating the ticket.
    )
    db.session.add(new_ticket)
    db.session.flush()  # to generate a ticket id

    # Create a TicketAssignment record for each assigned user.
    for user in assigned_users:
        assignment = TicketAssignment(
            ticket_id=new_ticket.id,
            user_id=user.id
        )
        db.session.add(assignment)

    db.session.commit()
    return jsonify({
        "message": "Ticket created",
        "ticket": {
            'id': new_ticket.id,
            'title': new_ticket.title,
            'description': new_ticket.description,
            'status': new_ticket.status,
            'creator_id': new_ticket.creator_id
        }
    }), 201

# GET: A single ticket by its id.
# Non-admins must be assigned to the ticket to access it.
@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Deny access for non-admins if no assignment exists.
    if current_user.role != "admin":
        assignment = TicketAssignment.query.filter_by(ticket_id=ticket_id, user_id=current_user.id).first()
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403

    assigned_users = TicketAssignment.query.filter_by(ticket_id=ticket_id).all()
    assigned_users_list = [{"user_id": assign.user_id, "username": assign.user.username} for assign in assigned_users]

    return jsonify({
        'id': ticket.id,
        'title': ticket.title,
        'description': ticket.description,
        'status': ticket.status,
        'creator_id': ticket.creator_id,
        "assigned_users" : assigned_users_list
    }), 200

# PATCH: Update a ticket.
# Only admins can update ticket details, and only for tickets they own.
@app.route('/api/tickets/<int:ticket_id>', methods=['PATCH'])
@admin_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    # Ensure the admin is the creator of the ticket
    if current_user.role == "admin" and ticket.creator_id != current_user.id:
        return jsonify({'error': 'You can only edit tickets you created'}), 403

    data = request.get_json()
    if 'title' in data:
        ticket.title = data['title']
    if 'description' in data:
        ticket.description = data['description']
    if 'status' in data:
        ticket.status = data['status']
    # Optionally, update assignments separately.
    
    db.session.commit()
    return jsonify({'message': 'Ticket updated successfully'}), 200

# POST: Update the users assigned to a specific ticket
# Only admins can update ticket details, and only for tickets they own.
@app.route('/api/tickets/<int:ticket_id>/assignments', methods=['POST'])
@admin_required
def assign_user_to_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    # Ensure the admin is the creator of the ticket
    if current_user.role == "admin" and ticket.creator_id != current_user.id:
        return jsonify({'error': 'You can only edit tickets you created'}), 403

    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if user is already assigned to this ticket
    existing_assignment = TicketAssignment.query.filter_by(ticket_id=ticket_id, user_id=user.id).first()
    if existing_assignment:
        return jsonify({"error": "User is already assigned to this ticket"}), 400

    # Create a new assignment
    new_assignment = TicketAssignment(ticket_id=ticket_id, user_id=user.id)
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({
        "message": "User assigned successfully",
        "assignment": {
            "ticket_id": ticket_id,
            "user_id": user.id,
            "username": user.username
        }
    }), 201

# DELETE: Removes a user assigned to a ticket
# Only admins can change ticket details, and only tickets they own.
@app.route('/api/tickets/<int:ticket_id>/assignments/<int:user_id>', methods=['DELETE'])
@admin_required
def remove_user_from_ticket(ticket_id, user_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Ensure the admin is the creator of the ticket
    if current_user.role == "admin" and ticket.creator_id != current_user.id:
        return jsonify({'error': 'You can only edit tickets you created'}), 403

    assignment = TicketAssignment.query.filter_by(ticket_id=ticket_id, user_id=user_id).first()
    if not assignment:
        return jsonify({"error": "User is not assigned to this ticket"}), 404

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({"message": "User removed from ticket successfully"}), 200


# DELETE: Delete a ticket.
# Only admins can delete tickets, and only tickets they own.
@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
@admin_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    # Ensure the admin is the creator of the ticket
    if current_user.role == "admin" and ticket.creator_id != current_user.id:
        return jsonify({'error': 'You can only edit tickets you created'}), 403
    
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket deleted successfully'}), 200

# ----------------------
# Comment Endpoints
# ----------------------

# GET all comments for a specific ticket.
@app.route('/api/tickets/<int:ticket_id>/comments', methods=['GET'])
@login_required
def get_ticket_comments(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    # Standard users see comments only if they are assigned.
    if current_user.role != "admin":
        assignment = TicketAssignment.query.filter_by(ticket_id=ticket_id, user_id=current_user.id).first()
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403

    results = []
    for comment in ticket.comments:
        results.append({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at,
            'author_id': comment.user_id
        })
    return jsonify(results), 200

# POST a comment on a ticket.
@app.route('/api/tickets/<int:ticket_id>/comments', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    # Standard users must be assigned to the ticket.
    if current_user.role != "admin":
        assignment = TicketAssignment.query.filter_by(ticket_id=ticket_id, user_id=current_user.id).first()
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Content is required"}), 400

    new_comment = Comment(
        content=data.get("content"),
        ticket_id=ticket.id,
        user_id=current_user.id
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({
        "message": "Comment added",
        "comment": {
            'id': new_comment.id,
            'content': new_comment.content
        }
    }), 201

# DELETE a comment.
# Allowed if the current user is the comment owner OR
# if the current user is an admin and they are the creator of the associated ticket.
@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    ticket = comment.ticket  # the ticket linked to the comment
    if comment.user_id == current_user.id:
        # Comment owner can delete their comment.
        pass
    elif current_user.role == "admin" and ticket.creator_id == current_user.id:
        # Admin can delete comments on tickets they created.
        pass
    else:
        return jsonify({"error": "You are not authorized to delete this comment"}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Comment deleted successfully"}), 200

# -----------------------------
# Ticket Assignment Endpoints
# -----------------------------

# GET assignments for a ticket.
# - If the current user is an admin, return all assignments for the ticket.
# - If a standard user, return only their own assignment (if any).
@app.route('/api/tickets/<int:ticket_id>/assignments', methods=['GET'])
@login_required
def get_ticket_assignments(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    if current_user.role != 'admin':
        assignment = TicketAssignment.query.filter_by(ticket_id=ticket_id, user_id=current_user.id).first()
        if not assignment:
            return jsonify({'error': 'Access denied'}), 403
        return jsonify({
            'assignments': [{
                'id': assignment.id,
                'ticket_id': assignment.ticket_id,
                'user_id': assignment.user_id,
                'assignment_note': assignment.assignment_note
            }]
        }), 200

    # For admin, return all assignments.
    assignments = TicketAssignment.query.filter_by(ticket_id=ticket_id).all()
    results = []
    for assign in assignments:
        results.append({
            'id': assign.id,
            'ticket_id': assign.ticket_id,
            'user_id': assign.user_id,
            'assignment_note': assign.assignment_note
        })
    return jsonify({'assignments': results}), 200

# POST: Create a new assignment for a ticket.
# Only admins can assign users to tickets.
@app.route('/api/tickets/<int:ticket_id>/assignments', methods=['POST'])
@admin_required
def create_ticket_assignment(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Prevent duplicate assignments.
    existing = TicketAssignment.query.filter_by(ticket_id=ticket_id, user_id=user.id).first()
    if existing:
        return jsonify({"error": "User is already assigned to this ticket"}), 400

    new_assignment = TicketAssignment(
        ticket_id=ticket_id,
        user_id=user.id,
        assignment_note=data.get("assignment_note", "")
    )
    db.session.add(new_assignment)
    db.session.commit()
    return jsonify({
        "message": "User assigned to ticket successfully",
        "assignment": {
            "id": new_assignment.id,
            "ticket_id": new_assignment.ticket_id,
            "user_id": new_assignment.user_id,
            "assignment_note": new_assignment.assignment_note
        }
    }), 201

# PATCH: Update an assignment (for example, change the assignment_note).
# Only admins may update assignments.
@app.route('/api/tickets/<int:ticket_id>/assignments/<int:assignment_id>', methods=['PATCH'])
@admin_required
def update_ticket_assignment(ticket_id, assignment_id):
    assignment = TicketAssignment.query.filter_by(id=assignment_id, ticket_id=ticket_id).first()
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    data = request.get_json()
    if "assignment_note" in data:
        assignment.assignment_note = data.get("assignment_note")
    db.session.commit()
    return jsonify({"message": "Assignment updated successfully"}), 200

# DELETE: Remove an assignment from a ticket.
# Only admins can remove an assignment.
@app.route('/api/tickets/<int:ticket_id>/assignments/<int:assignment_id>', methods=['DELETE'])
@admin_required
def delete_ticket_assignment(ticket_id, assignment_id):
    assignment = TicketAssignment.query.filter_by(id=assignment_id, ticket_id=ticket_id).first()
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    db.session.delete(assignment)
    db.session.commit()
    return jsonify({"message": "Assignment deleted successfully"}), 200

#-----------------
# Users
#-----------------


# GET: All users
@app.route('/api/users', methods=['GET'])
@admin_required
def get_all_users():
    users = User.query.with_entities(User.id, User.username).all()
    user_list = [{"user_id": user.id, "username": user.username} for user in users]
    return jsonify(user_list), 200

# GET: A user's username by their UID
@app.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_username(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user_id': user.id, 'username': user.username}), 200
