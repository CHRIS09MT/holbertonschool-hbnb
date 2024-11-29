from typing import TYPE_CHECKING
from app.models.base import BaseModel
from sqlalchemy.orm import validates
from app import db

if TYPE_CHECKING:
    from app.models.place import Place
    from app.models.user import User


class Review(BaseModel, db.Model):
    text = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    place_id = db.Column(
        db.String(36), db.ForeignKey("place.id"), nullable=False
    )
    user_id = db.Column(
        db.String(36), db.ForeignKey("user.id"), nullable=False
    )

    user = db.relationship("User", back_populates="reviews")
    place = db.relationship("Place", back_populates="reviews")

    def __init__(self, text, rating, place, user) -> None:
        super().__init__()
        self.text: str = text
        self.rating: int = rating
        self.place: Place = place
        self.user: User = user

    @validates("text")
    def validate_text(self, key, text):
        """Setter for text."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not text or len(text) > 500:
            raise ValueError(
                "text cannot be empty and must be less than 500 characters"
            )

        return text

    @validates("rating")
    def validate_rating(self, key, rating):
        """Setter for rating."""
        if not isinstance(rating, (int, float)):
            raise TypeError("rating must be an integer")
        if rating < 1 or rating > 5:
            raise ValueError("rating must be between 1 and 5")

        return rating

    @validates("place")
    def validate_place(self, key, place):
        """Setter for place."""
        from app.models.place import Place

        if not isinstance(place, Place):
            raise ValueError("place must be a Place instance")

        return place

    @validates("user")
    def validate_user(self, key, user):
        """Setter for user."""
        from app.models.user import User

        if not isinstance(user, User):
            raise ValueError("user must be a User instance")

        return user
