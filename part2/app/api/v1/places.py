from flask_jwt_extended import current_user, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace("places", description="Place operations")

# Define the models for related entities
amenity_model = api.model(
    "PlaceAmenity",
    {
        "id": fields.String(description="Amenity ID"),
        "name": fields.String(description="Name of the amenity"),
    },
)

user_model = api.model(
    "PlaceUser",
    {
        "id": fields.String(description="User ID"),
        "first_name": fields.String(description="First name of the owner"),
        "last_name": fields.String(description="Last name of the owner"),
        "email": fields.String(description="Email of the owner"),
    },
)

review_model = api.model(
    "PlaceReview",
    {
        "id": fields.String(description="Review ID"),
        "text": fields.String(description="Text of the review"),
        "rating": fields.Integer(
            description="Rating of the place (1-5)", min=1, max=5
        ),
        "user_id": fields.String(description="ID of the user"),
    },
)

# Define the place model for input validation and documentation
place_model = api.model(
    "Place",
    {
        "title": fields.String(
            required=True, description="Title of the place"
        ),
        "description": fields.String(description="Description of the place"),
        "price": fields.Float(
            required=True, description="Price per night", min=0
        ),
        "latitude": fields.Float(
            required=True, description="Latitude of the place", min=-90, max=90
        ),
        "longitude": fields.Float(
            required=True,
            description="Longitude of the place",
            min=-180,
            max=180,
        ),
        "amenities": fields.List(
            fields.String, description="List of amenities ID's"
        ),
    },
    strict=True,
)

place_response_model = api.model(
    "PlaceResponse",
    place_model.clone(
        "PlaceResponse",
        {
            "id": fields.String(description="Place ID"),
            "owner": fields.Nested(user_model),
            "amenities": fields.List(fields.Nested(amenity_model)),
            "reviews": fields.List(fields.Nested(review_model)),
        },
    ),
)


@api.route("/")
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, "Place successfully created", place_response_model)
    @api.response(400, "Invalid input data")
    @api.response(401, "Invalid token")
    @api.response(404, "Owner not found")
    @jwt_required()
    def post(self):
        """Register a new place"""
        place_data: dict = api.payload

        place_data["owner"] = current_user
        amenities = place_data.pop("amenities", [])

        try:
            new_place = facade.create_place(place_data)
        except ValueError as e:
            return {"message": str(e)}, 400

        has_added = False

        for amenity in amenities:
            exists = facade.get_amenity(amenity)

            if exists:
                new_place.add_amenity(exists)
                has_added = True

        if has_added:
            new_place.save()

        return {
            "id": new_place.id,
            "title": new_place.title,
            "description": new_place.description,
            "price": new_place.price,
            "latitude": new_place.latitude,
            "longitude": new_place.longitude,
            "owner": {
                "id": new_place.owner.id,
                "first_name": new_place.owner.first_name,
                "last_name": new_place.owner.last_name,
                "email": new_place.owner.email,
            },
            "amenities": [
                {
                    "id": amenity.id,
                    "name": amenity.name,
                }
                for amenity in new_place.amenities
            ],
        }, 201

    @api.response(
        200, "List of places retrieved successfully", [place_response_model]
    )
    def get(self):
        """Retrieve a list of all places"""
        places = facade.get_all_places()

        return [
            {
                "id": place.id,
                "title": place.title,
                "description": place.description,
                "price": place.price,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "owner": {
                    "id": place.owner.id,
                    "first_name": place.owner.first_name,
                    "last_name": place.owner.last_name,
                    "email": place.owner.email,
                },
                "amenities": [
                    {"id": amenity.id, "name": amenity.name}
                    for amenity in place.amenities
                ],
            }
            for place in places
        ]


@api.route("/<place_id>")
class PlaceResource(Resource):
    @api.response(
        200, "Place details retrieved successfully", place_response_model
    )
    @api.response(404, "Place not found")
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)

        if not place:
            return {"error": "Place not found"}, 404

        return {
            "id": place.id,
            "title": place.title,
            "description": place.description,
            "price": place.price,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "owner": {
                "id": place.owner.id,
                "first_name": place.owner.first_name,
                "last_name": place.owner.last_name,
                "email": place.owner.email,
            },
            "amenities": [
                {"id": amenity.id, "name": amenity.name}
                for amenity in place.amenities
            ],
            "reviews": [
                {"id": review.id, "text": review.text, "rating": review.rating}
                for review in place.reviews
            ],
        }

    @api.expect(place_model)
    @api.response(200, "Place updated successfully", place_response_model)
    @api.response(400, "Invalid input data")
    @api.response(401, "Invalid token")
    @api.response(404, "Place not found")
    @jwt_required()
    def put(self, place_id):
        """Update a place's information"""
        place_data = api.payload

        existing_place = facade.get_place(place_id)

        if not existing_place:
            return {"error": "Place not found"}, 404

        if (
            not current_user.is_admin
            and existing_place.owner.id != current_user.id
        ):
            return {"error": "Unauthorized action"}, 403

        place_data.pop("amenities", None)

        try:
            updated_place = facade.update_place(existing_place, place_data)
        except ValueError as e:
            return {"message": str(e)}, 400

        return {
            "id": updated_place.id,
            "title": updated_place.title,
            "description": updated_place.description,
            "price": updated_place.price,
            "latitude": updated_place.latitude,
            "longitude": updated_place.longitude,
            "owner": {
                "id": updated_place.owner.id,
                "first_name": updated_place.owner.first_name,
                "last_name": updated_place.owner.last_name,
                "email": updated_place.owner.email,
            },
            "amenities": [
                {"id": amenity.id, "name": amenity.name}
                for amenity in updated_place.amenities
            ],
        }
