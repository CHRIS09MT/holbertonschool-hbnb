from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    current_user,
    jwt_required,
)
from app.services import facade

api = Namespace("auth", description="Authentication operations")

# Model for input validation
login_model = api.model(
    "Login",
    {
        "email": fields.String(required=True, description="User email"),
        "password": fields.String(required=True, description="User password"),
    },
    strict=True,
)

response_model = api.model(
    "LoginResponse",
    {
        "access_token": fields.String(description="JWT token"),
    },
)


@api.route("/login")
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, "User successfully authenticated", response_model)
    @api.response(400, "Invalid input data")
    @api.response(401, "Invalid credentials")
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload

        user = facade.get_user_by_email(credentials["email"])

        if not user or not user.verify_password(credentials["password"]):
            return {"error": "Invalid credentials"}, 401

        access_token = create_access_token(
            identity={"id": user.id, "is_admin": user.is_admin},
            expires_delta=False,
        )

        return {"access_token": access_token}, 200


@api.route("/protected")
class ProtectedResource(Resource):
    @api.response(200, "User successfully authenticated")
    @api.response(401, "Invalid token")
    @jwt_required()
    def get(self):
        """A protected endpoint that requires a valid JWT token"""
        return {"message": f"Hello, user {current_user.id}"}, 200
