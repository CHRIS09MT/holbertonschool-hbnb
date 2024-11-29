from flask import Flask, abort
from flask_cors import CORS
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()


def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    # CORS(app, origins=['http://localhost:3000'])
    CORS(app)
    app.url_map.strict_slashes = False

    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.services import facade

        user = facade.get_user(jwt_data["sub"]["id"])

        if not user:
            abort(404, "User not found")

        return user

    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        authorizations={
            "apiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
            }
        },
        security="apiKey",
        doc="/api/v1",
    )

    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns

    # Register the users namespace
    api.add_namespace(users_ns, path="/api/v1/users")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(reviews_ns, path="/api/v1")
    api.add_namespace(auth_ns, path="/api/v1")

    return app
