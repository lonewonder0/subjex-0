import os
import tempfile
import pytest
from flask import json
from . import create_app, db
from .models import User, Ticket, Comment, TicketAssignment

@pytest.fixture(scope='function')
def client():
    from . import create_app, db
    from werkzeug.security import generate_password_hash
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test',
        'ELEVATE_ADMIN_SECRET': 'devsecret',
        'FLASK_ENV': 'development',
    })

    with app.app_context():
        db.create_all()
        from .models import User
        admin = User(username="admin", password=generate_password_hash("adminpass"), role="admin")
        user = User(username="user", password=generate_password_hash("userpass"), role="standard")
        db.session.add_all([admin, user])
        db.session.commit()
        with app.test_client() as client:
            yield client

def login(client, username, password):
    return client.post('/api/login', json={"username": username, "password": password})

def register(client, username, password):
    return client.post('/api/register', json={"username": username, "password": password})

def logout(client):
    return client.post('/api/logout')

def test_register_and_login(client):
    rv = register(client, "testuser", "testpass")
    assert rv.status_code == 200 or rv.status_code == 201
    rv = login(client, "testuser", "testpass")
    assert rv.status_code == 200

def test_elevate_user(client):
    # Login as admin and check login success
    rv = login(client, "admin", "adminpass")
    assert rv.status_code == 200
    rv = client.post('/api/dev/elevate-user', json={"user_id": 2, "dev_password": os.getenv("ELEVATE_ADMIN_SECRET")})
    assert rv.status_code == 200

def test_get_session_info(client):
    login(client, "admin", "adminpass")
    rv = client.get('/api/session')
    assert rv.status_code == 200

def test_create_ticket(client):
    login(client, "admin", "adminpass")
    # Assign to user with id 2
    rv = client.post('/api/tickets', json={
        "title": "Test Ticket",
        "description": "A ticket",
        "assigned_user_ids": [2]
    })
    assert rv.status_code == 200 or rv.status_code == 201

def test_get_tickets(client):
    login(client, "admin", "adminpass")
    rv = client.get('/api/tickets')
    assert rv.status_code == 200

def test_get_ticket(client):
    login(client, "admin", "adminpass")
    # Create ticket
    client.post('/api/tickets', json={
        "title": "Ticket2",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    rv = client.get('/api/tickets/1')
    assert rv.status_code == 200

def test_update_ticket(client):
    login(client, "admin", "adminpass")
    client.post('/api/tickets', json={
        "title": "Ticket3",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    rv = client.patch('/api/tickets/1', json={"title": "Updated"})
    assert rv.status_code == 200

def test_assign_user_to_ticket(client):
    login(client, "admin", "adminpass")
    client.post('/api/tickets', json={
        "title": "Ticket4",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    # Only assign user 2 once
    rv = client.post('/api/tickets/1/assignments', json={"user_id": 2})
    assert rv.status_code == 200 or rv.status_code == 201

def test_remove_user_from_ticket(client):
    login(client, "admin", "adminpass")
    client.post('/api/tickets', json={
        "title": "Ticket5",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    client.post('/api/tickets/1/assignments', json={"user_id": 2})
    rv = client.delete('/api/tickets/1/assignments/2')
    assert rv.status_code == 200

def test_delete_ticket(client):
    login(client, "admin", "adminpass")
    client.post('/api/tickets', json={
        "title": "Ticket6",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    rv = client.delete('/api/tickets/1')
    assert rv.status_code == 200

def test_add_and_get_comment(client):
    login(client, "admin", "adminpass")
    client.post('/api/tickets', json={
        "title": "Ticket7",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    rv = client.post('/api/tickets/1/comments', json={"content": "A comment"})
    assert rv.status_code == 200 or rv.status_code == 201
    rv = client.get('/api/tickets/1/comments')
    assert rv.status_code == 200

def test_delete_comment(client):
    login(client, "admin", "adminpass")
    client.post('/api/tickets', json={
        "title": "Ticket8",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    client.post('/api/tickets/1/comments', json={"content": "To delete"})
    # Get comment id
    comment = Comment.query.filter_by(content="To delete").first()
    rv = client.delete(f'/api/comments/{comment.id}')
    assert rv.status_code == 200

def test_get_ticket_assignments(client):
    login(client, "admin", "adminpass")
    client.post('/api/tickets', json={
        "title": "Ticket9",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    rv = client.get('/api/tickets/1/assignments')
    assert rv.status_code == 200

def test_assign_user_to_ticket(client):
    login(client, "admin", "adminpass")
    rv = client.post('/api/tickets', json={
        "title": "Ticket4",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    rv = register(client, "test", "password123");
    assert rv.status_code == 200 or rv.status_code == 201

    rv = client.post('/api/tickets/1/assignments', json={"user_id": 3})
    assert rv.status_code == 200 or rv.status_code == 201

def test_delete_ticket_assignment(client):
    login(client, "admin", "adminpass")
    client.post('/api/tickets', json={
        "title": "Ticket12",
        "description": "desc",
        "assigned_user_ids": [2]
    })
    
    rv = client.delete(f'/api/tickets/1/assignments/2')
    assert rv.status_code == 200

def test_get_all_users(client):
    login(client, "admin", "adminpass")
    rv = client.get('/api/users')
    assert rv.status_code == 200

def test_get_username(client):
    login(client, "admin", "adminpass")
    rv = client.get('/api/users/1')
    assert rv.status_code == 200