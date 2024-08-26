from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import (
    SQLAlchemyError,
    OperationalError as SQLAlchemyOperationalError,
)
from psycopg2 import OperationalError

from schema import ReportSchema, ProfileSchema
from utils.risk_assessment import risk_assessment, generate_report_summary
from db import db
from models import FinancialProfile, RiskAssessmentReport
from flask import jsonify

blp = Blueprint(
    "Risk Assessment", "risks", description="Operations on Risk Assessment Service"
)


def handle_db_errors(fn):
    """Decorator to handle common database errors."""

    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (OperationalError, SQLAlchemyOperationalError):
            db.session.rollback()
            abort(503, message="Service unavailable")
        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")
        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Unexpected error")

    return wrapper


@blp.route("/<uuid:borrower_id>/profile")
class BorrowerProfile(MethodView):
    """Models operations on financial profile."""

    @blp.response(200, ProfileSchema)
    @jwt_required()
    @handle_db_errors
    def get(self, borrower_id):
        """Fetch financial profile for a borrower."""
        profile = FinancialProfile.query.filter_by(
            borrower_id=borrower_id
        ).one_or_none()
        if profile is None:
            return jsonify(message="Profile not found"), 404
        return profile

    @blp.arguments(ProfileSchema, location="form")
    @blp.response(201, ProfileSchema)
    @jwt_required()
    @handle_db_errors
    def post(self, user_data, borrower_id):
        """Create a financial profile."""
        profile = FinancialProfile(
            borrower_id=borrower_id,
            credit_score=user_data["credit_score"],
            monthly_income=user_data["monthly_income"],
            debt_payments=user_data.get("debt_payments"),
            employment_status=user_data["employment_status"],
        )
        db.session.add(profile)
        db.session.commit()
        return profile

    @jwt_required()
    @handle_db_errors
    def delete(self, borrower_id):
        """Delete financial profile for a borrower."""
        profile = FinancialProfile.query.filter_by(borrower_id=borrower_id).first()
        if profile:
            db.session.delete(profile)
            db.session.commit()
            return {"message": "Profile deleted"}, 202
        abort(404, message="Profile not found")


@blp.route("/<uuid:borrower_id>/report")
class AssessmentReport(MethodView):
    """Models operations on assessment reports."""

    @blp.response(200, ReportSchema)
    @jwt_required()
    @handle_db_errors
    def get(self, borrower_id):
        """Fetch risk assessment report for a borrower."""
        report = RiskAssessmentReport.query.filter_by(borrower_id=borrower_id).first()
        if report is None:
            abort(404, message="Report not found")
        return report

    @blp.arguments(ReportSchema)
    @blp.response(200, ReportSchema)
    @jwt_required()
    @handle_db_errors
    def post(self, user_data, borrower_id):
        """Generate a risk assessment report."""
        finance_profile = FinancialProfile.query.filter_by(
            borrower_id=borrower_id
        ).first()
        if finance_profile is None:
            abort(404, message="Financial profile not found")

        profile = {
            "monthly_income": finance_profile.monthly_income,
            "debt_payments": finance_profile.debt_payments,
            "employment_status": finance_profile.employment_status,
            "credit_score": finance_profile.credit_score,
            "is_defaulter": finance_profile.is_defaulter,
        }
        assessment = risk_assessment(user_data["loan_amount"], profile)
        report_summary = generate_report_summary(assessment)

        report = RiskAssessmentReport(
            borrower_id=borrower_id,
            loan_id=user_data["loan_id"],
            is_eligible=assessment["is_eligible"],
            risk_score=assessment["risk_score"],
            debt_to_income_ratio=assessment["debt_to_income_ratio"],
            report_summary=report_summary,
        )

        db.session.add(report)
        db.session.commit()
        return report
