import json
import logging
import jwt
from datetime import datetime, timezone, timedelta
from app.rabbitmq import publish_event
from ariadne import QueryType, MutationType
from app.middleware import jwt_required
from app.extensions import db, bcrypt
from app.models import User
from config import Config

query = QueryType()
mutation = MutationType()


def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.now().astimezone(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(
        payload, Config.JWT_SECRET_KEY, algorithm='HS256'
    )
    logging.info(f"created user token: {token}")
    return token

# fetch all the users stored in database


@query.field("users")
@jwt_required
def fetch_users(*_):
    try:
        users = User.query.all()
        logging.info(f"users fetched successfully: {users}")

        # Serialize the users
        user_list = [user.to_dict() for user in users]
        logging.info(f"serialized all the users: {user_list}")

        return {
            "success": True,
            "message": "Users fetched successfully.",
            "users": user_list
        }
    except Exception as error:
        logging.error(f"Error fetching users: {error}")
        return {
            "success": False,
            "message": str(error),
            "users": []
        }

# fetch a user by its id


@query.field("user")
@jwt_required
def fetch_user(_, info, id):
    try:
        user = User.query.get(id)
        if not user:
            raise Exception(f"User with id {id} not found")
        return {
            "success": True,
            "message": "User fetched successfully.",
            "users": [user]
        }
    except Exception as error:
        logging.error(f"Error while fetching user: {error}")
        return {
            "success": False,
            "message": str(error),
            "users": []
        }

# handle user registration


@mutation.field("registerUser")
def handle_user_registration(_, info, input):
    email = input.get('email')
    username = input.get('username')
    password = input.get('password')
    address = input.get('address'),
    contact = input.get('contact')

    if not email or not password or not username or not address or not contact:
        raise Exception(
            "Email, username, password, address and contact is required")

    try:
        if User.query.filter_by(email=email).first():
            raise Exception('User with this email already exists!')

        hashed_password = (
            bcrypt.generate_password_hash(password).decode('utf-8')
        )
        new_user = User(username=username, email=email,
                        password=hashed_password, address=address, contact=contact)
        logging.info(f"new user created: {str(new_user)}")

        db.session.add(new_user)
        db.session.commit()
        logging.info(f"new user stored in database")

        event_data = json.dumps({
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "address": new_user.address,
            "contact": new_user.contact,
        })
        publish_event(exchange_name="event_exchange",
                      routing_key=Config.USER_REGISTERED_QUEUE, message=event_data)

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
        token = generate_jwt(user)
        logging.info(f"create new access token for user: {user.id}")

        return {
            "success": True,
            "token": token
        }

    except Exception as e:
        logging.error(f"Error while logging in user: {e}")
        raise Exception("Failed to login user.")


@mutation.field("updateUser")
@jwt_required
def handle_user_update(_, info, user_id, user_name=None, email=None, password=None, address=None, contact=None):
    try:
        # Firstly to update a user, find the user by its ID
        user = User.query.get(user_id)
        if not user:
            return {
                "success": False,
                "message": "User not found",
                "user": None
            }

        if user_name:
            user.username = user_name
        if email:
            user.email = email
        if password:
            user.password = bcrypt.generate_password_hash(
                password).decode('utf-8')
        if address:
            user.address = address
        if contact:
            user.contact = contact

        # Commit the changes to the db
        db.session.commit()

        # publish an event to the queue
        updated_event_data = json.dumps({
            "event": Config.USER_PROFILE_UPDATED_QUEUE,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "address": user.address,
            "contact": user.contact,
            "updated_timestamp": str(datetime.now().astimezone(timezone.utc))
        })
        publish_event(exchange_name="event_exchange",
                      routing_key=Config.USER_PROFILE_UPDATED_QUEUE, message=updated_event_data)

        return {
            "success": True,
            "message": "User updated successfully",
            "user": user
        }
    except Exception as error:
        db.session.rollback()  # Rollback to previous state in case of error
        return {
            "success": False,
            "message": str(error),
            "user": None
        }
