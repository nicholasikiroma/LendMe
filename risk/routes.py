from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
    NoResultFound,
)
from psycopg2 import OperationalError
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError

from schema import ReportSchema, ProfileSchema
from utils.risk_assessment import risk_assessment, generate_report_summary
from db import db
from models import FinancialProfile, RiskAssessmentReport
from flask import jsonify

blp = Blueprint(
    "Risk Assessment",
    "risks",
    description="\
               Operations on Risk Assessment Service",
)


@blp.route("/<uuid:borrower_id>/profile")
class BorrowerProfile(MethodView):
    """Models Operations on Financial Profile"""

    # fetch profile
    @blp.response(200, ProfileSchema)
    @jwt_required()
    def get(self, borrower_id):
        """Fetch Financial profile for borrower"""
        try:
            profile = FinancialProfile.query.filter_by(
                borrower_id=borrower_id
            ).one_or_none()

            if profile is not None:
                return profile

            profile = jsonify(message="Profile not found")
            profile.status_code = 404
            return profile

        except OperationalError:
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError:
            abort(503, message="Service unavailable")

        except SQLAlchemyError as err:
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            print(str(err))
            abort(500, message="Something went wrong")

    # create profile
    @blp.arguments(ProfileSchema, location="form")
    @blp.response(201, ProfileSchema)
    @jwt_required()
    def post(self, user_data, borrower_id):
        """Create a financial profile"""
        profile = FinancialProfile()

        profile.borrower_id = borrower_id
        profile.credit_score = user_data["credit_score"]
        profile.monthly_income = user_data["monthly_income"]
        profile.debt_payments = user_data.get("debt_payments", None)
        profile.employment_status = user_data["employment_status"]

        try:
            db.session.add(profile)
            db.session.commit()

        except IntegrityError:
            abort(400, message="profile exists for user")

        except OperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError:
            abort(503, message="Service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            abort(500, message="Something went wrong")

        return profile

    # delete profile
    @jwt_required()
    def delete(self, borrower_id):
        """delete financial profile for borrower"""
        try:
            profile = FinancialProfile.query.filter_by(borrower_id=borrower_id).first()
            if profile:
                db.session.delete(profile)
                db.session.commit()
            else:
                abort(404)

        except OperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="something went wrong")

        except Exception as err:
            print(str(err))
            abort(500, message="Something went wrong")

        return {"message": "profile deleted"}, 202


@blp.route("/<uuid:borrower_id>/report")
class AssessmentReport(MethodView):
    """Models operations on assessment reports"""

    @blp.response(200, ReportSchema)
    @jwt_required()
    def get(self, borrower_id):
        """Fetch risk assessment report for a user"""
        try:
            report = RiskAssessmentReport.query.filter_by(
                borrower_id=borrower_id
            ).first()

        except NoResultFound:
            abort(404, message="Report not found.")

        except OperationalError:
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError:
            abort(503, message="Service unavailable")

        except SQLAlchemyError as err:
            print(str(err))
            abort(500, message="something went wrong")

        except Exception as err:
            print(str(err))
            abort(500, message="Something went wrong")

        return report

    @blp.arguments(ReportSchema)
    @blp.response(200, ReportSchema)
    @jwt_required()
    def post(self, user_data, borrower_id):
        """Generate a risk assessment report"""
        finance_profile = FinancialProfile.query.filter_by(
            borrower_id=borrower_id
        ).first()
        profile = {
            "monthly_income": finance_profile.monthly_income,
            "debt_payments": finance_profile.debt_payments,
            "employment_status": finance_profile.employment_status,
            "credit_score": finance_profile.credit_score,
            "is_defaulter": finance_profile.is_defaulter,
        }

        # generate risk assessment for user
        assessment = risk_assessment(user_data["loan_amount"], profile)

        # generate assessment report
        report_summary = generate_report_summary(assessment)

        report = RiskAssessmentReport()

        report.borrower_id = borrower_id
        report.loan_id = user_data["loan_id"]
        report.is_eligible = assessment["is_eligible"]
        report.risk_score = assessment["risk_score"]
        report.debt_to_income_ratio = assessment["debt_to_income_ratio"]
        report.report_summary = report_summary

        try:
            db.session.add(report)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="something went wrong")

        except Exception as err:
            print(str(err))
            abort(500, message="Something went wrong")

        return report
