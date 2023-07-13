from uuid import uuid4
from db import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship



class FinancialProfile(db.Model):
    """Models the financial profile of a borrower"""

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid4
    )
    borrower_id = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    employment_status = db.Column(db.Enum("EMPLOYED", "UNEMPLOYED", "SELF_EMPLOYED", name="employmentstatus"), nullable=False)
    debt_payments = db.Column(
        db.Numeric(asdecimal=True, precision=10, scale=2), nullable=True
    )
    credit_score = db.Column(db.Integer(), nullable=False)
    monthly_income = db.Column(
        db.Numeric(asdecimal=True, precision=10, scale=2), nullable=False
    )
    is_defaulter = db.Column(db.Boolean(), default=False)

    risk_assessment = relationship(
        "RiskAssessmentReport",
        backref="financial_profile",
        cascade="all, delete",
    )


class RiskAssessmentReport(db.Model):
    """Report Based on Risk Assessment"""

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid4
    )
    borrower_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("financial_profile.borrower_id"), nullable=False
    )
    loan_id = db.Column(UUID(as_uuid=True), nullable=False)
    debt_to_income_ratio = db.Column(db.Float, nullable=True)
    is_eligible = db.Column(db.Boolean, nullable=False, default=False)
    risk_score = db.Column(db.Float, nullable=False)
    report_summary = db.Column(db.Text, nullable=False)
