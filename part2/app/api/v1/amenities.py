from flask_jwt_extended import current_user, jwt_required
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace("amenities", description="Amenity operations")

# Define the amenity model for input validation and documentation
amenity_model = api.model(
    "Amenity",
    {"name": fields.String(required=True, description="Name of the amenity")},
    strict=True,
)

amenity_response_model = api.model(
    "AmenityResponse",
    amenity_model.clone(
        "AmenityResponse", {"id": fields.String(description="Amenity ID")}
    ),
)


@api.route("/")
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, "Amenity successfully created", amenity_response_model)
    @api.response(400, "Invalid input data")
    @api.response(403, "Admin privileges required")
    @api.response(409, "Amenity already exists")
    @jwt_required()
    def post(self):
        """Register a new amenity"""
        if not current_user.is_admin:
            return {"error": "Admin privileges required"}, 403

        amenity_data = api.payload

        existing_amenity = facade.get_amenity_by_name(amenity_data["name"])
        if existing_amenity:
            return {
                "message": f"Amenity with the name '{existing_amenity.name}' already exists. ID: {existing_amenity.id}"
            }, 409

        try:
            new_amenity = facade.create_amenity(amenity_data)
        except ValueError as e:
            return {"message": str(e)}, 400

        return {
            "id": new_amenity.id,
            "name": new_amenity.name,
        }, 201

    @api.response(
        200,
        "List of amenities retrieved successfully",
        [amenity_response_model],
    )
    def get(self):
        """Retrieve a list of all amenities"""
        amenities = facade.get_all_amenities()

        return [
            {"id": amenity.id, "name": amenity.name} for amenity in amenities
        ]


@api.route("/<amenity_id>")
class AmenityResource(Resource):
    @api.response(
        200, "Amenity details retrieved successfully", amenity_response_model
    )
    @api.response(404, "Amenity not found")
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)

        if not amenity:
            return {"message": "Amenity not found"}, 404

        return {
            "id": amenity.id,
            "name": amenity.name,
        }

    @api.expect(amenity_model)
    @api.response(200, "Amenity updated successfully", amenity_response_model)
    @api.response(400, "Invalid input data")
    @api.response(403, "Admin privileges required")
    @api.response(404, "Amenity not found")
    @api.response(409, "Amenity already exists")
    @jwt_required()
    def put(self, amenity_id):
        """Update an amenity's information"""
        if not current_user.is_admin:
            return {"error": "Admin privileges required"}, 403

        amenity_data = api.payload

        amenity = facade.get_amenity(amenity_id)

        if not amenity:
            return {"message": "Amenity not found"}, 404

        if amenity_data["name"] == amenity.name:
            return {"message": "No changes detected"}, 200

        if facade.get_amenity_by_name(amenity_data["name"]):
            return {
                "message": f"Amenity with the name '{amenity_data['name']}' already exists. ID: {amenity.id}"
            }, 409

        try:
            updated_amenity = facade.update_amenity(amenity, amenity_data)

        except ValueError as e:
            return {"message": str(e)}, 400

        return {
            "id": updated_amenity.id,
            "name": updated_amenity.name,
        }
