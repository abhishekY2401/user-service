# User Model

from app.extensions import db
from datetime import datetime, timezone


class User(db.Model):
    '''
        User Schema
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    contact = db.Column(db.String(15), nullable=True)

    total_orders = db.Column(db.Integer, default=0)
    last_order_date = db.Column(db.DateTime, nullable=True)
    total_spent = db.Column(db.Float, default=0.0)

    created_at = db.Column(
        db.DateTime, default=datetime.now().astimezone(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=datetime.now(), onupdate=datetime.now().astimezone(timezone.utc))

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "address": self.address,
            "contact": self.contact
        }
