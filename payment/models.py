from datetime import datetime
from uuid import uuid4
from db import db
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID


class TransactionStatus(Enum):
    SUCCESSFUL = "successful"
    FAILED = "failed"
    PENDING = "pending"


class TransactionType(Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    FUND = "fund"


class Wallet(db.Model):
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    user_id = db.Column(UUID(as_uuid=True), unique=True,nullable=False)
    balance = db.Column(
        db.Numeric(asdecimal=True, precision=10, scale=2), nullable=False, default=0
    )
    transactions = db.relationship(
        "Transactions", backref="wallet", cascade="all, delete-orphan", lazy=True
    )


class Transactions(db.Model):
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    wallet_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("wallet.id"), nullable=False
    )
    sender_id = db.Column(UUID(as_uuid=True), nullable=False)
    receiver_id = db.Column(UUID(as_uuid=True), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    status = db.Column(db.Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING.value)
    narration = db.Column(db.Text)
    amount = db.Column(
        db.Numeric(asdecimal=True, precision=10, scale=2), nullable=False
    )
    reference_id = db.Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid4)


class FundTransaction(db.Model):
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    wallet_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("wallet.id"), nullable=False
    )
    amount = db.Column(
        db.Numeric(asdecimal=True, precision=10, scale=2), nullable=False
    )
    reference_id = db.Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid4)