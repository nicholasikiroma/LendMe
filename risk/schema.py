"""Defines schema and validations for RESTFUL API"""
from enum import Enum
from marshmallow import Schema, fields


class EmploymentStatus(Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"


class ReportSchema(Schema):
    id = fields.UUID(dump_only=True)
    borrower_id = fields.UUID(dump_only=True)
    loan_amount = fields.Decimal(load_only=True, required=True)
    loan_id = fields.UUID(required=True)
    debt_to_income_ratio = fields.Decimal(dump_only=True)
    is_eligible = fields.Boolean(dump_only=True)
    risk_score = fields.Decimal(dump_only=True)
    report_summary = fields.Str(dump_only=True)


class ProfileSchema(Schema):
    id = fields.UUID(dump_only=True)
    borrower_id = fields.UUID(dump_only=True)
    employment_status = fields.Str(required=True)
    credit_score = fields.Decimal()
    monthly_income = fields.Decimal(required=True)
    debt_payments = fields.Decimal(required=True)
    is_defaulter = fields.Boolean()
