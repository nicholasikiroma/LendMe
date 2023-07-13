from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from psycopg2.errors import OperationalError


from schema import WalletSchema, TransactionSchema, FundTransactionSchema
from models import Transactions, Wallet, FundTransaction
from db import db

blp = Blueprint(
    "Payments",
    "payments",
    description="\
               Operations on Payment Management Service",
)


@blp.route("/")
class CreateWallet(MethodView):
    """Models CRUD operations on wallets"""

    @blp.arguments(WalletSchema)
    @blp.response(201, WalletSchema)
    def post(self, user_data):
        """Create wallet"""
        wallet = Wallet()

        wallet.user_id = user_data["user_id"]

        try:
            db.session.add(wallet)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            abort(403, message="wallet exits for user")

        except OperationalError:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            abort(500, message=str(err))

        return wallet


@blp.route("/<uuid:wallet_id>")
class FetchWallet(MethodView):
    """Models CRUD operations on wallets"""

    @blp.response(200, WalletSchema)
    @jwt_required()
    def get(self, wallet_id):
        """fetch wallet"""
        try:
            wallet = Wallet.query.get_or_404(wallet_id)

        except OperationalError:
            abort(503, "service unavailable")

        return wallet

    @blp.response(202, WalletSchema)
    @jwt_required()
    def delete(self, wallet_id):
        """Delete wallet"""
        wallet = Wallet.query.get_or_404(wallet_id)
        try:
            db.session.delete(wallet)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            abort(500, message=f"{err}")

        return wallet


@blp.route("/<uuid:wallet_id>/transactions")
class CreateTransaction(MethodView):
    """Models CRUD operations on wallets"""

    @blp.arguments(TransactionSchema, location='form')
    @blp.response(202, TransactionSchema)
    @jwt_required()
    def post(self, user_data, wallet_id):
        """Create a transaction"""
        sender_wallet = Wallet.query.get_or_404(wallet_id)
        sender_id = user_data["sender_id"]
        receiver_id = user_data["receiver_id"]
        txn_amount = user_data["amount"]
        narration = user_data["narration"]

        if sender_wallet.user_id != sender_id:
            abort(400, message="wallet is not yours.")

        # Validate sender and receiver existence
        receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()
        if not receiver_wallet:
            abort(404, message="receiver wallet not found")

        # Validate sufficient funds in the sender's wallet
        if sender_wallet.balance < txn_amount:
            abort(400, message="insufficient funds")

        try:
            with db.session.begin_nested():
                # Debit the sender's wallet
                sender_wallet.balance -= txn_amount

                # Credit the receiver's wallet
                receiver_wallet.balance += txn_amount

                # Create sender transaction
                sender_transaction = Transactions(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    wallet_id=wallet_id,
                    amount=txn_amount,
                    narration=narration,
                    transaction_type="DEBIT",
                    status="SUCCESSFUL",
                )
                db.session.add(sender_transaction)

                # Create receiver transaction
                receiver_transaction = Transactions(
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    wallet_id=receiver_wallet.id,
                    amount=txn_amount,
                    narration=narration,
                    transaction_type="CREDIT",
                    status="SUCCESSFUL",
                )
                db.session.add(receiver_transaction)

            # Commit the outermost transaction, which includes both debit and credit operations
            db.session.commit()

        except IntegrityError as err:
            db.session.rollback()
            abort(403, message="transaction exists")

        except OperationalError:
            db.session.rollback()
            abort(403, message="service unavailable")

        except Exception as err:
            db.session.rollback()
            abort(500, message="unknown error occured")

        return sender_transaction


@blp.route("/<uuid:wallet_id>/transactions/<uuid:transaction_id>")
class FetchTransactions(MethodView):
    """Models CRUD operations on wallets"""

    @blp.response(200, TransactionSchema)
    @jwt_required()
    def get(self, wallet_id, transaction_id):
        """Fetch transaction details"""
        wallet = Wallet.query.get_or_404(wallet_id)

        transaction = wallet.transactions.filter_by(id=transaction_id).first()

        if transaction:
            return transaction
        else:
            abort(404, message="Transaction not found")


@blp.route("/<uuid:wallet_id>/fund")
class FundWallet(MethodView):
    """Fund wallet"""

    @blp.arguments(FundTransactionSchema)
    @blp.response(201, FundTransactionSchema)
    def put(self, user_data, wallet_id):
        """Fund wallet"""
        wallet = Wallet.query.get_or_404(wallet_id)
        amount = user_data["amount"]
        wallet.balance += amount
        try:
            db.session.add(wallet)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable.")

        except Exception as err:
            db.session.rollback()
            abort(500, message=f"Internal Server Error: {str(err)}")

        fund_wallet = FundTransaction(amount=amount, wallet_id=wallet_id)
        try:
            db.session.add(fund_wallet)
            db.session.commit()

        except OperationalError:
            db.session.rollback()
            abort(503, message="service unavailable")

        except Exception as err:
            db.session.rollback()
            abort(500, message=f"Internal Server Error: {str(err)}")

        return fund_wallet
