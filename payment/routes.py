from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import (
    SQLAlchemyError,
    OperationalError as SQLAlchemyOperationalError,
)
from psycopg2 import OperationalError
from functools import wraps

from schema import WalletSchema, TransactionSchema, FundTransactionSchema
from models import Transactions, Wallet, FundTransaction
from db import db

blp = Blueprint(
    "Payments",
    "payments",
    description="Operations on Payment Management Service",
)


def handle_exceptions(func):
    """Decorator to handle exceptions for database operations."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyOperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable.")
        except SQLAlchemyError as err:
            db.session.rollback()
            print(f"Error: {str(err)}")
            abort(500, message="Database error occurred.")
        except Exception as err:
            db.session.rollback()
            print(f"Error: {str(err)}")
            abort(500, message="An unknown error occurred.")

    return wrapper


@blp.route("/")
class CreateWallet(MethodView):
    """Models CRUD operations on wallets"""

    @blp.arguments(WalletSchema)
    @blp.response(201, WalletSchema)
    @handle_exceptions
    def post(self, user_data):
        """Create wallet"""
        wallet = Wallet(user_id=user_data["user_id"])
        db.session.add(wallet)
        db.session.commit()
        return wallet


@blp.route("/<uuid:wallet_id>")
class FetchWallet(MethodView):
    """Models CRUD operations on wallets"""

    @blp.response(200, WalletSchema)
    @jwt_required()
    @handle_exceptions
    def get(self, wallet_id):
        """Fetch wallet"""
        wallet = Wallet.query.get_or_404(wallet_id)
        return wallet

    @blp.response(202, WalletSchema)
    @jwt_required()
    @handle_exceptions
    def delete(self, wallet_id):
        """Delete wallet"""
        wallet = Wallet.query.get_or_404(wallet_id)
        db.session.delete(wallet)
        db.session.commit()
        return wallet


@blp.route("/<uuid:wallet_id>/transactions")
class CreateTransaction(MethodView):
    """Models CRUD operations on wallets"""

    @blp.arguments(TransactionSchema, location="form")
    @blp.response(202, TransactionSchema)
    @jwt_required()
    @handle_exceptions
    def post(self, user_data, wallet_id):
        """Create a transaction"""
        sender_wallet = Wallet.query.get_or_404(wallet_id)
        sender_id = user_data["sender_id"]
        receiver_id = user_data["receiver_id"]
        txn_amount = user_data["amount"]
        narration = user_data["narration"]

        if sender_wallet.user_id != sender_id:
            abort(400, message="This wallet is not yours.")

        receiver_wallet = Wallet.query.filter_by(user_id=receiver_id).first()
        if not receiver_wallet:
            abort(404, message="Receiver wallet not found.")

        if sender_wallet.balance < txn_amount:
            abort(400, message="Insufficient funds.")

        with db.session.begin_nested():
            sender_wallet.balance -= txn_amount
            receiver_wallet.balance += txn_amount

            sender_transaction = Transactions(
                sender_id=sender_id,
                receiver_id=receiver_id,
                wallet_id=wallet_id,
                amount=txn_amount,
                narration=narration,
                transaction_type="DEBIT",
                status="SUCCESSFUL",
            )
            receiver_transaction = Transactions(
                sender_id=sender_id,
                receiver_id=receiver_id,
                wallet_id=receiver_wallet.id,
                amount=txn_amount,
                narration=narration,
                transaction_type="CREDIT",
                status="SUCCESSFUL",
            )

            db.session.add(sender_transaction)
            db.session.add(receiver_transaction)

        db.session.commit()
        return sender_transaction


@blp.route("/<uuid:wallet_id>/transactions/<uuid:transaction_id>")
class FetchTransactions(MethodView):
    """Models CRUD operations on wallets"""

    @blp.response(200, TransactionSchema)
    @jwt_required()
    @handle_exceptions
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
    @handle_exceptions
    def put(self, user_data, wallet_id):
        """Fund wallet"""
        wallet = Wallet.query.get_or_404(wallet_id)
        amount = user_data["amount"]
        wallet.balance += amount

        db.session.add(wallet)
        db.session.commit()

        fund_wallet = FundTransaction(amount=amount, wallet_id=wallet_id)

        db.session.add(fund_wallet)
        db.session.commit()

        return fund_wallet
