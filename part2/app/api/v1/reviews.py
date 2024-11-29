from flask_jwt_extended import current_user, jwt_required
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace("reviews", description="Review operations")

# Define the review model for input validation and documentation
review_model = api.model(
    "Review",
    {
        "text": fields.String(required=True, description="Text of the review"),
        "rating": fields.Integer(
            required=True,
            description="Rating of the place (1-5)",
            min=1,
            max=5,
        ),
        "place_id": fields.String(
            required=True, description="ID of the place"
        ),
    },
    strict=True,
)

review_response_model = api.model(
    "ReviewResponse",
    review_model.clone(
        "ReviewResponse", {"user_id": fields.String(), "id": fields.String()}
    ),
)


@api.route("/reviews")
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, "Review successfully created", review_response_model)
    @api.response(400, "Invalid input data")
    @api.response(401, "Invalid token")
    @api.response(404, "Place not found")
    @jwt_required()
    def post(self):
        """Register a new review"""
        review_data = api.payload

        place = facade.get_place(review_data["place_id"])

        if not place:
            return {"error": "Place not found"}, 400

        if place.owner.id == current_user.id:
            return {"error": "You cannot review your own place."}, 400

        has_reviewed = False

        for review in place.reviews:
            if review.user.id == current_user.id:
                has_reviewed = True
                break

        if has_reviewed:
            return {"error": "You have already reviewed this place."}, 400

        review_data["place"] = place
        review_data["user"] = current_user
        review_data.pop("place_id")

        try:
            new_review = facade.create_review(review_data)
        except ValueError as e:
            return {"message": str(e)}, 400

        return {
            "id": new_review.id,
            "text": new_review.text,
            "rating": new_review.rating,
            "user_id": new_review.user.id,
            "place_id": new_review.place.id,
        }, 201

    @api.response(
        200, "List of reviews retrieved successfully", [review_response_model]
    )
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()

        return [
            {
                "id": review.id,
                "text": review.text,
                "rating": review.rating,
                "user_id": review.user.id,
                "place_id": review.place.id,
            }
            for review in reviews
        ]


@api.route("/reviews/<review_id>")
class ReviewResource(Resource):
    @api.response(
        200, "Review details retrieved successfully", review_response_model
    )
    @api.response(404, "Review not found")
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)

        if not review:
            return {"message": "Review not found"}, 404

        return {
            "id": review.id,
            "text": review.text,
            "rating": review.rating,
            "user_id": review.user.id,
            "place_id": review.place.id,
        }

    @api.expect(review_model)
    @api.response(200, "Review updated successfully", review_response_model)
    @api.response(400, "Invalid input data")
    @api.response(401, "Invalid token")
    @api.response(403, "Unauthorized action")
    @api.response(404, "Review not found")
    @jwt_required()
    def put(self, review_id):
        """Update a review's information"""
        review_data = api.payload

        review = facade.get_review(review_id)

        if not review:
            return {"message": "Review not found"}, 404

        if not current_user.is_admin and review.user.id != current_user.id:
            return {"message": "Unauthorized action"}, 403

        review_data.pop("place_id", None)

        try:
            updated_review = facade.update_review(review, review_data)
        except ValueError as e:
            return {"message": str(e)}, 400

        return {
            "id": updated_review.id,
            "text": updated_review.text,
            "rating": updated_review.rating,
            "user_id": updated_review.user.id,
            "place_id": updated_review.place.id,
        }

    @api.response(204, "Review deleted successfully")
    @api.response(401, "Invalid token")
    @api.response(403, "Unauthorized action")
    @api.response(404, "Review not found")
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        review = facade.get_review(review_id)

        if not review:
            return {"message": "Review not found"}, 404

        if not current_user.is_admin and review.user.id != current_user.id:
            return {"message": "Unauthorized action"}, 403

        facade.delete_review(review)
        return "", 204


@api.route("/places/<place_id>/reviews")
class PlaceReviewList(Resource):
    @api.response(
        200,
        "List of reviews for the place retrieved successfully",
        [review_response_model],
    )
    @api.response(404, "Place not found")
    def get(self, place_id):
        """Get all reviews for a specific place"""
        place = facade.get_place(place_id)

        if not place:
            return {"message": "Place not found"}, 404

        reviews = facade.get_reviews_by_place(place_id)

        return [
            {
                "id": review.id,
                "text": review.text,
                "rating": review.rating,
                "user_id": review.user.id,
                "place_id": review.place.id,
            }
            for review in reviews
        ]
