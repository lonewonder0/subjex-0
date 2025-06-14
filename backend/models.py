from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'admin' or 'regular'
    
    # Tickets created by this user (if they are an admin)
    created_tickets = db.relationship('Ticket', foreign_keys='Ticket.creator_id', backref='creator', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Open')
    # The admin who created the ticket.
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # A ticket may have many comments.
    comments = db.relationship('Comment', backref='ticket', lazy=True)
    
    # The ticket assignments (many-to-many-like relationship)
    assignments = db.relationship('TicketAssignment', backref='ticket', cascade="all, delete-orphan", lazy=True)

class TicketAssignment(db.Model):
    __tablename__ = 'ticket_assignments'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Establish a relationship so that each assignment knows its user.
    user = db.relationship("User", backref=db.backref("ticket_assignments", cascade="all, delete-orphan", lazy=True))

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
