from flask_jwt_extended import create_access_token
from uuid import uuid4
from db import db
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID


class UserRole(Enum):
    LENDER = "lender"
    BORROWER = "borrower"
    BOTH = "both"


class User(db.Model):
    """Model a user"""

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid4
    )
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    access_token = db.Column(db.String(), unique=True, nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.BOTH, nullable=False)
    wallet_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)

    def update_access_token(self):
        self.access_token = create_access_token(self.email, expires_delta=False)
