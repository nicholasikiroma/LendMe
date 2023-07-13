"""Defines schema and validations for RESTFUL API"""
from enum import Enum
from marshmallow import Schema, fields


class TransactionStatus(Enum):
    SUCCESSFUL = "successful"
    FAILED = "failed"
    PENDING = "pending"


class TransactionType(Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    FUND = "fund"


class FundTransactionSchema(Schema):
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    wallet_id = fields.UUID(dump_only=True)
    amount = fields.Decimal(required=True)
    reference_id = fields.UUID(dump_only=True)


class TransactionSchema(Schema):
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime()
    sender_id = fields.UUID(required=True)
    receiver_id = fields.UUID(required=True)
    transaction_type = fields.Enum(TransactionType, dump_only=True)
    status = fields.Enum(TransactionStatus, dump_only=True)
    narration = fields.Str(required=True)
    amount = fields.Decimal(required=True)
    reference_id = fields.UUID(dump_only=True)


class WalletSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(required=True)
    balance = fields.Decimal(dump_only=True)
    transactions = fields.Nested(TransactionSchema, many=True, dump_only=True)
