"""Defines schema and validations for RESTFUL API"""
from enum import Enum
from marshmallow import Schema, fields

class LoanStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"



class BorrowerApplicationsSchema(Schema):
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    lender_id = fields.UUID(dump_only=True)
    borrower_id = fields.UUID(dump_only=True)
    is_accepted = fields.Bool()
    loan_id = fields.UUID(dump_only=True)


class LoanSchema(Schema):
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(load_only=True)
    lender_id = fields.UUID(required=True)
    borrower_id = fields.UUID()
    status = fields.Enum(LoanStatus)
    duration = fields.Integer(required=True)
    start_date = fields.Date()
    due_date = fields.Date()
    is_paid = fields.Bool()
    interest = fields.Decimal(required=True)
    amount = fields.Decimal(required=True)
    applications = fields.Nested(BorrowerApplicationsSchema, many=True, dump_only=True)


class StartEndLoan(Schema):
    start_date = fields.Date(loan_only=True)
    end_date = fields.Date(loan_only=True)


class LoanOperationsSchema(Schema):
    message = fields.Str(dump_only=True)
    loan_id = fields.UUID(required=True, load_only=True)


class LoanApplicationSchema(Schema):
    message = fields.Str(dump_only=True)
    lender_id = fields.UUID(required=True, load_only=True)
    borrower_id = fields.UUID(required=True, load_only=True)


class RepaymentSchema(Schema):
    amount_due = fields.Decimal(dump_ony=True)
    lender_id = fields.UUID(dump_only=True)
    borrower_id = fields.UUID(dump_only=True)
    loan_id = fields.UUID(dump_only=True)
    interest = fields.Decimal(dump_only=True)
    start_date = fields.Date(dump_only=True)
    end_date = fields.Date(dump_only=True)
