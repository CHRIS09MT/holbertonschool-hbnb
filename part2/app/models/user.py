from app import bcrypt, db
from app.models.base import BaseModel
from sqlalchemy.orm import validates


class User(BaseModel, db.Model):
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    places = db.relationship("Place", back_populates="owner")
    reviews = db.relationship("Review", back_populates="user")

    def __init__(
        self,
        first_name,
        last_name,
        email,
        password,
        is_admin=False,
    ) -> None:
        super().__init__()
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.email: str = email
        self.password: str = password
        self.is_admin: bool = is_admin

    @validates("first_name")
    def validate_first_name(self, key, value: str):
        if not isinstance(value, str):
            raise ValueError("First name must be a string")
        if not value or len(value) > 50:
            raise ValueError(
                "First name cannot be emtpy and must be less than 50 characters"
            )

        return value

    @validates("last_name")
    def validate_last_name(self, key, value: str):
        if not isinstance(value, str):
            raise ValueError("Last name must be a string")
        if not value or len(value) > 50:
            raise ValueError(
                "Last name cannot be emtpy and must be less than 50 characters"
            )

        return value

    @validates("email")
    def validate_email(self, key, value: str):
        if (
            "@" not in value
            or "." not in value.split("@")[-1]
            or value.endswith(".")
        ):
            raise ValueError("Invalid email address")

        return value

    @validates("password")
    def validate_password(self, key, password: str):
        """Hashes the password before storing it."""
        if not isinstance(password, str):
            raise ValueError("Password must be a string")

        return bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)
