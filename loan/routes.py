from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort

from sqlalchemy.orm import joinedload
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from psycopg2 import OperationalError


from schema import LoanOperationsSchema, LoanSchema, LoanApplicationSchema, StartEndLoan,RepaymentSchema
from utils.interest_calculator import loan_cal
from models import Loan, LoanApplication
from db import db

blp = Blueprint(
    "Loans",
    "loans",
    description="\
               Operations on Loan Management Service",
)


@blp.route("/")
class Loans(MethodView):
    @blp.response(200, LoanSchema(many=True))
    def get(self):
        """Fetch all loans"""
        try:
            return Loan.query.order_by(Loan.created_at.desc()).all()
        
        except OperationalError:
            abort(503, message="service unavailable")

        except SQLAlchemyOperationalError:
            abort(503, message="service unavailable")
        
        except NoResultFound:
            abort(404, message="loans not found")

        except SQLAlchemyError as err:
            abort(500, message=str(err))
        
        except Exception as err:
            abort(500, message="Something went wrong.")

    @blp.arguments(LoanSchema, location="form")
    @blp.response(201, LoanSchema)
    @jwt_required()
    def post(self, user_data):
        """Create a loan"""
        loan = Loan()
        loan.lender_id = user_data["lender_id"]
        loan.interest = user_data["interest"]
        loan.duration = user_data["duration"]
        loan.amount = user_data["amount"]

        try:
            db.session.add(loan)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return loan


@blp.route("/<uuid:loan_id>")
class LoanOperations(MethodView):
    @blp.response(200, LoanSchema)
    @jwt_required()
    def get(self, loan_id):
        """Retrieve details about a loan"""
        try:
            loan = Loan.query.get_or_404(loan_id)

        except OperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return loan

    @blp.response(202, LoanOperationsSchema)
    @jwt_required()
    def delete(self, loan_id):
        """Delete a loan"""
        loan = Loan.query.get_or_404(loan_id)

        try:
            db.session.delete(loan)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return {"message": "loan deleted"}


@blp.route("/<uuid:loan_id>/repayments")
class LoanRepayments(MethodView):
    @blp.response(200, RepaymentSchema)
    @jwt_required()
    def get(self, loan_id):
        """Generate repayment details"""
        loan = Loan.query.get_or_404(loan_id)

        lender_id = loan.lender_id
        borrower_id = loan.borrower_id
        interest = loan.interest
        start_date = loan.start_date
        end_date = loan.due_date
        amount = loan.amount
        duration = loan.duration

        amount_due = loan_cal(
            amount=amount,
            duration=duration,
            interest=interest,
            start_date=start_date,
            end_date=end_date,
        )

        repayment_detail = {
            "amount_due": amount_due,
            "lender_id": lender_id,
            "borrower_id": borrower_id,
            "loan_id": loan_id,
            "interest": interest,
            "start_date": start_date,
            "end_date": end_date,
        }

        return repayment_detail


@blp.route("/<uuid:application_id>/applications")
class LoanApplications(MethodView):
    @blp.response(202, LoanApplicationSchema)
    @jwt_required()
    def get(self, application_id):
        """Accept a loan application"""
        application = LoanApplication.query.get_or_404(application_id)
        loan_id = application.loan_id

        application.is_accepted = True
        try:
            db.session.add(application)
            db.session.commit()
        
        except OperationalError:
            db.session.rollback()
            abort(503, message="service unavailable")
        
        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        loan = Loan.query.get_or_404(loan_id)
        loan.status = "CLOSED"
        loan.borrower_id = application.borrower_id

        try:
            db.session.add(loan)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return {"message": "successful"}


@blp.route("/<uuid:loan_id>/start-date")
class StartDate(MethodView):
    @blp.arguments(StartEndLoan, location='json')
    @blp.response(200, LoanSchema)
    @jwt_required()
    def put(self, user_data, loan_id):
        """Update start date in database"""
        loan = Loan.query.get_or_404(loan_id)
        loan.start_date = user_data["start_date"]
        try:
            db.session.add(loan)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return loan


@blp.route("/<uuid:loan_id>/end-date")
class EndDate(MethodView):
    @blp.arguments(StartEndLoan, location='json')
    @blp.response(200, LoanSchema)
    @jwt_required()
    def put(self, user_data, loan_id):
        """Update end date in database"""
        loan = Loan.query.get_or_404(loan_id)
        loan.due_date = user_data["end_date"]
        try:
            db.session.add(loan)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return loan


@blp.route("/<uuid:loan_id>/applications")
class Apply(MethodView):
    @blp.arguments(LoanApplicationSchema, location="json")
    @blp.response(201, LoanApplicationSchema)
    @jwt_required()
    def post(self, user_data, loan_id):
        """Apply to loan"""
        borrower_id = user_data["borrower_id"]
        lender_id = user_data["lender_id"]

        if borrower_id == lender_id:
            abort(403, message="You cannot borrow from yourself.")

        try:
            loan = Loan.query.get_or_404(loan_id)

        except NoResultFound:
            abort(404, message="Loan not found.")
        

        application = LoanApplication.query.filter_by(
            loan_id=loan_id, borrower_id=borrower_id).one_or_none()

        if application:
            abort(401, message="Already applied to this loan.")

        else:
            loan_application = LoanApplication(
                borrower_id=borrower_id, lender_id=lender_id, loan_id=loan_id
            )

            try:
                db.session.add(loan_application)
                db.session.commit()

            except OperationalError:
                db.session.rollback()
                abort(503, message="Service unavailable. Try again later.")

            except SQLAlchemyOperationalError as err:
                db.session.rollback()
                abort(503, message="service unavailable")

            except SQLAlchemyError as err:
                db.session.rollback()
                print(str(err))
                abort(500, message="Something went wrong")

            except Exception as err:
                db.session.rollback()
                print(str(err))
                abort(500, message="Something went wrong")

        return {"message": "Application successful!"}


@blp.route("/user/<uuid:user_id>/applications")
class UserApplications(MethodView):
    @blp.response(200, LoanSchema(many=True))
    @jwt_required()
    def get(self, user_id):
        """Fetch all loans a user has submitted applications to,"""
        try:
            loans = (
                Loan.query.join(LoanApplication)
                .options(joinedload(Loan.applications))
                .filter(LoanApplication.borrower_id == user_id)
                .all()
            )

        except NoResultFound:
            abort(404, message="No loans associated with user.")

        except OperationalError:
            abort(503, message="Service temporarily unavailable")

        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return loans


@blp.route("/user/<uuid:user_id>/loans")
class UserLoans(MethodView):
    @blp.response(200, LoanSchema(many=True))
    @jwt_required()
    def get(self, user_id):
        """Fetch all loans associated with a user,"""
        try:
            loans = Loan.query.filter_by(lender_id=user_id).all()

        except NoResultFound:
            abort(404, message="No loans associated with user.")

        except OperationalError:
            abort(503, message="Service temporarily unavailable")
        
        except SQLAlchemyOperationalError as err:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return loans
