import json
import logging
from datetime import datetime, timezone
from app.rabbitmq import publish_event
from ariadne import QueryType, MutationType
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db, bcrypt
from app.models import User
from config import Config

query = QueryType()
mutation = MutationType()

# fetch all the users stored in database


@query.field("users")
def fetch_users():
    try:
        users = User.query.all()
        return [{"id": user.id, "username": user.username, "email": user.email, "total_orders": user.total_orders, "last_order_date": user.last_order_date, "total_spent": user.total_spent, "created": user.created_at, "updated": user.updated_at} for user in users]
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return []

# fetch a user by its id


@query.field("user")
def fetch_user(_, info, id):
    try:
        user = User.query.get(id)
        if not user:
            raise Exception(f"User with id {id} not found")
        return user
    except Exception as e:
        logging.error(f"Error while fetching user: {e}")
        return None

# handle user registration


@mutation.field("registerUser")
def handle_user_registration(_, info, input):
    email = input.get('email')
    username = input.get('username')
    password = input.get('password')

    if not email or not password or not username:
        raise Exception("Email, username and password is required")

    try:
        if User.query.filter_by(email=email).first():
            raise Exception('User with this email already exists!')

        hashed_password = (
            bcrypt.generate_password_hash(password).decode('utf-8')
        )
        new_user = User(username=username, email=email,
                        password=hashed_password)
        logging.info(f"new user created: {str(new_user)}")

        db.session.add(new_user)
        db.session.commit()
        logging.info(f"new user stored in database")

        event_data = json.dumps({
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "timestamp": str(datetime.now().astimezone(timezone.utc))
        })
        publish_event(Config.USER_REGISTERED_QUEUE, event_data)

        return new_user

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error registering user: {e}")
        raise Exception("Failed to register user.")


@mutation.field("loginUser")
def handle_user_authentication(_, info, input):
    email = input.get("email")
    password = input.get("password")
    if not email or not password:
        raise Exception("Email and password is required.")

    try:
        user = User.query.filter_by(email=email).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            raise Exception("Invalid email or password.")

        # generate jwt token
        access_token = create_access_token(identity=user.id)
        logging.info(f"create new access token for user: {user.id}")

        return {
            "message": "Login successful",
            "token": access_token
        }

    except Exception as e:
        logging.error(f"Error while logging in user: {e}")
        raise Exception("Failed to login user.")


@mutation.field("updateUser")
def handle_user_update(_, info, userId, firstName=None, lastName=None, email=None):
    try:
        # Firstly to update a user, find the user by its ID
        user = User.query.get(userId)
        if not user:
            return {
                "success": False,
                "message": "User not found",
                "user": None
            }

        # Update fields if provided
        if firstName:
            user.first_name = firstName
        if lastName:
            user.last_name = lastName
        if email:
            user.email = email

        # Commit the changes to the database
        db.session.commit()

        # publish an event to the queue
        updated_event_data = json.dumps({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "updated_timestamp": str(datetime.now().astimezone(timezone.utc))
        })
        publish_event(Config.USER_PROFILE_UPDATED_QUEUE, updated_event_data)

        return {
            "success": True,
            "message": "User updated successfully",
            "user": user
        }
    except Exception as e:
        db.session.rollback()  # Rollback to previous state in case of error
        return {
            "success": False,
            "message": str(e),
            "user": None
        }
