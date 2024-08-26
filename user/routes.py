from passlib.hash import pbkdf2_sha256
from time import sleep
from flask_jwt_extended import jwt_required, get_current_user
import requests
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from psycopg2 import OperationalError

from schema import LoginSchema, UserSchema
from models import User, db

blp = Blueprint(
    "Users",
    "users",
    description="\
               Operations on users",
)

wallet_service_url = "http://wallet-service:5003/api/wallets"


# Helper function for wallet creation
def create_wallet(user_id, retries=3, delay=1):
    """Create wallet for a user with retry logic."""
    payload = {"user_id": str(user_id)}
    for attempt in range(retries):
        response = requests.post(wallet_service_url, json=payload)
        if response.status_code == 201:
            return response.json().get("id")
        if response.status_code == 503:
            sleep(delay)
        else:
            break
    return None


@blp.route("/register")
class CreateUser(MethodView):
    @blp.arguments(UserSchema, location="form")
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Create a new user and a wallet for the user."""
        user = User(
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            email=user_data["email"],
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="User already exists.")
        except (SQLAlchemyError, OperationalError) as err:
            db.session.rollback()
            abort(
                503 if isinstance(err, OperationalError) else 500,
                message="Service unavailable.",
            )

        # Create wallet after user is created
        user.wallet_id = create_wallet(user.id)
        try:
            db.session.add(user)
            db.session.commit()
        except (SQLAlchemyError, OperationalError) as err:
            db.session.rollback()
            abort(
                503 if isinstance(err, OperationalError) else 500,
                message="Error creating wallet.",
            )

        return user


@blp.route("/login")
class LoginUser(MethodView):
    @blp.arguments(LoginSchema, location="form")
    @blp.response(200, LoginSchema)
    def post(self, user_data):
        """Authenticate a user and return a token."""
        try:
            user = User.query.filter_by(email=user_data["email"]).first()
            if not user or not pbkdf2_sha256.verify(
                user_data["password"], user.password
            ):
                abort(401, message="Invalid email or password.")

            user.update_access_token()
            db.session.commit()
            return user
        except (SQLAlchemyError, OperationalError) as err:
            db.session.rollback()
            abort(
                503 if isinstance(err, OperationalError) else 500,
                message="Service unavailable.",
            )


@blp.route("/<uuid:user_id>/profile")
class GetUser(MethodView):
    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self, user_id):
        """Retrieve user profile."""
        try:
            user = User.query.get_or_404(user_id)
            return user
        except (SQLAlchemyError, OperationalError) as err:
            abort(
                503 if isinstance(err, OperationalError) else 500,
                message="Something went wrong.",
            )


@blp.route("/current-user")
class GetCurrentUser(MethodView):
    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self):
        """Fetch the current authenticated user."""
        current_user = get_current_user()
        if not current_user:
            abort(404, message="User not found.")
        return current_user
