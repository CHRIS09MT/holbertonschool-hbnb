from flask_jwt_extended import current_user, jwt_required
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace("users", description="User operations")

# Define the user model for input validation and documentation
base_user_model = api.model(
    "UserModel",
    {
        "first_name": fields.String(
            required=True, description="First name of the user"
        ),
        "last_name": fields.String(
            required=True, description="Last name of the user"
        ),
        "email": fields.String(required=True, description="Email of the user"),
    },
)

user_response_model = api.model(
    "UserResponseModel",
    base_user_model.clone(
        "UserResponseModel",
        {
            "id": fields.String(description="User ID"),
        },
    ),
)

user_payload_model = api.model(
    "UserPayloadModel",
    base_user_model.clone(
        "UserPayloadModel",
        {"password": fields.String(required=True, description="Password")},
    ),
    strict=True,
)


@api.route("/")
class UserList(Resource):
    @api.expect(user_payload_model)
    @api.response(201, "User successfully created", user_response_model)
    @api.response(409, "Email already registered")
    @api.response(400, "Invalid input data")
    @api.response(401, "Invalid token")
    @api.response(403, "Admin privileges required")
    @jwt_required()
    def post(self):
        """Register a new user"""
        if not current_user.is_admin:
            return {"error": "Admin privileges required"}, 403

        user_data = api.payload

        existing_user = facade.get_user_by_email(user_data["email"])

        if existing_user:
            return {"message": "Email already registered"}, 409

        try:
            new_user = facade.create_user(user_data)
        except ValueError as e:
            return {"message": str(e)}, 400

        return {
            "id": new_user.id,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
        }, 201

    @api.response(
        200, "List of users retrieved successfully", [base_user_model]
    )
    def get(self):
        """Get a list of all users"""
        users = facade.get_users()

        return [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
            for user in users
        ]


@api.route("/<user_id>")
class UserResource(Resource):
    @api.response(
        200, "User details retrieved successfully", user_response_model
    )
    @api.response(404, "User not found")
    def get(self, user_id):
        """Get user details by ID"""

        user = facade.get_user(user_id)

        if not user:
            return {"message": "User not found"}, 404

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }, 200

    @api.expect(user_payload_model)
    @api.response(
        200, "User details updated successfully", user_response_model
    )
    @api.response(400, "Invalid input data")
    @api.response(401, "Invalid token")
    @api.response(403, "Unauthorized action")
    @api.response(404, "User not found")
    @jwt_required()
    def put(self, user_id):
        """Update user details by ID"""
        user_data: dict = api.payload

        user = facade.get_user(user_id)

        if not user:
            return {"message": "User not found"}, 404

        if user.id != current_user.id and not current_user.is_admin:
            return {"message": "Unauthorized action"}, 403

        data = {
            "first_name": user_data.get("first_name", user.first_name),
            "last_name": user_data.get("last_name", user.last_name),
            "email": user_data.get("email", user.email),
            "password": user_data.get("password", user.password),
        }

        if not current_user.is_admin:
            data.pop("email", None)
            data.pop("password", None)

        try:
            updated_user = facade.update_user(user, data)
        except (ValueError, TypeError) as e:
            return {"message": str(e)}, 400

        return {
            "id": updated_user.id,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "email": updated_user.email,
        }, 200
