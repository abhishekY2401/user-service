import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    RABBITMQ_URL = os.environ['RABBITMQ_URI']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    USER_REGISTERED_QUEUE = 'user.registered'
    USER_PROFILE_UPDATED_QUEUE = 'user.profile.updated'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
