"""Defines schema and validations for RESTFUL API"""
from enum import Enum
from marshmallow import Schema, fields

class UserRole(Enum):
    LENDER = "lender"
    BORROWER = "borrower"
    BOTH = "both"

class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Enum(UserRole)
    access_token = fields.Str(dump_only=True)
    wallet_id = fields.UUID(dump_only=True)


class LoginSchema(Schema):
    email = fields.Str(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True)
    access_token = fields.Str(dump_only=True)
