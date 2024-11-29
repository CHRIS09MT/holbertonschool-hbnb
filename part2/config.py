import os


class Config:
    DEBUG = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "default_jwt_secret")

    SWAGGER_UI_DOC_EXPANSION = "list"
    RESTX_VALIDATE = True


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///development.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {"development": DevelopmentConfig, "default": DevelopmentConfig}
