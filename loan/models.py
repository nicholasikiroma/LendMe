from datetime import datetime
from uuid import uuid4
from db import db
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID


class LoanStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


class Loan(db.Model):
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    lender_id = db.Column(UUID(as_uuid=True), nullable=False)
    borrower_id = db.Column(UUID(as_uuid=True), nullable=True)
    status = db.Column(db.Enum(LoanStatus), nullable=False, default=LoanStatus.OPEN)
    start_date = db.Column(db.Date, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    is_paid = db.Column(db.Boolean, nullable=False, default=False)
    interest = db.Column(
        db.Numeric(asdecimal=True, precision=10, scale=2), nullable=False
    )
    amount = db.Column(
        db.Numeric(asdecimal=True, precision=10, scale=2), nullable=False
    )
    applications = db.relationship(
        "LoanApplication", backref="loan", cascade="all, delete-orphan"
    )


class LoanApplication(db.Model):
    __tablename__ = "loan_application"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_accepted = db.Column(db.Boolean, nullable=False, default=False)
    lender_id = db.Column(UUID(as_uuid=True), nullable=False)
    borrower_id = db.Column(UUID(as_uuid=True), nullable=False)

    loan_id = db.Column(UUID(as_uuid=True), db.ForeignKey("loan.id"), nullable=False)
