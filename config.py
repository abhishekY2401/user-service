import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_PASSWORD = os.environ['DB_PASSWORD']
    RABBITMQ_URL = os.environ['RABBITMQ_URI']
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://postgres:{DB_PASSWORD}@localhost:5432/users_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'supersecretkey')
    USER_REGISTERED_QUEUE = 'user.registered'
    USER_PROFILE_UPDATED_QUEUE = 'user.profile.updated'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
