from typing import TYPE_CHECKING
from app.models.base import BaseModel
from sqlalchemy.orm import validates
from app import db

if TYPE_CHECKING == True:
    from app.models.user import User
    from app.models.review import Review
    from app.models.amenity import Amenity


class Place(BaseModel, db.Model):
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    owner_id = db.Column(
        db.String(36), db.ForeignKey("user.id"), nullable=False
    )

    owner = db.relationship("User", back_populates="places")
    reviews = db.relationship("Review", back_populates="place")

    amenities = db.relationship("Amenity", secondary="place_amenity")

    def __init__(
        self, title, price, latitude, longitude, owner, description=""
    ):
        super().__init__()
        self.title: str = title
        self.description: str = description
        self.price: float = price
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.owner: User = owner
        self.reviews: list[Review] = []
        self.amenities: list[Amenity] = []

    @validates("title")
    def validate_title(self, key, title):
        """Setter for title."""
        if not isinstance(title, str):
            raise TypeError("title must be a string")

        if not title or len(title) > 50:
            raise ValueError(
                "title cannot be empty and must be less than 50 characters"
            )

        return title

    @validates("description")
    def validate_description(self, key, description):
        """Setter for description."""
        if not isinstance(description, str):
            raise TypeError("description must be a string")

        if len(description) > 500:
            raise ValueError("description must be less than 500 characters")

        return description

    @validates("owner")
    def validate_owner(self, key, owner):
        """Setter for owner."""
        from app.models.user import User

        if not isinstance(owner, User):
            raise ValueError("owner must be a User instance")

        return owner

    @validates("price")
    def validate_price(self, key, price):
        """Setter for price."""
        if not isinstance(price, (int, float)):
            raise TypeError("price must be an int or float")

        if price < 0:
            raise ValueError("price must be a positive number")

        return price

    @validates("latitude")
    def validate_latitude(self, key, latitude):
        """Setter for latitude."""
        if not isinstance(latitude, (int, float)):
            raise TypeError("latitude must be an int or float")

        if latitude < -90 or latitude > 90:
            raise ValueError("latitude must be between -90 and 90")

        return latitude

    @validates("longitude")
    def validate_longitude(self, key, longitude):
        """Setter for longitude."""
        if not isinstance(longitude, (int, float)):
            raise TypeError("longitude must be an int or float")

        if longitude < -180 or longitude > 180:
            raise ValueError("longitude must be between -180 and 180")

        return longitude

    def add_review(self, review):
        """Add a review to the place."""
        from app.models.review import Review

        if not isinstance(review, Review):
            raise ValueError("review must be a Review instance")

        self.reviews.append(review)

        return review

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        from app.models.amenity import Amenity

        if not isinstance(amenity, Amenity):
            raise ValueError("amenity must be an Amenity instance")

        self.amenities.append(amenity)

        return amenity
