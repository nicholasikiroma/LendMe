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

url = "http://127.0.0.1:5003/api/wallets"


def create_wallet(user_id):
    """Create wallet when user is created"""
    payload = {"user_id": str(user_id)}
    response = requests.post(url, json=payload)

    if response.status_code == 201:
        return response.json().get("id")

    elif response.status_code == 503:
        retry_count = 0
        max_retries = 3
        while retry_count < max_retries:
            sleep(1)  # Wait for 1 second before retrying
            response = requests.post(url, json=payload)
            if response.status_code == 201:
                return response.json().get("id")
            retry_count += 1
            print(f"retry count: {retry_count}")
        return None


@blp.route("/register")
class CreateUser(MethodView):
    @blp.arguments(UserSchema, location="form")
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Create a new user"""
        first_name = user_data["first_name"]
        last_name = user_data["last_name"]
        password = user_data["password"]
        email = user_data["email"]

        hashed_password = pbkdf2_sha256.hash(password)

        try:
            user = User(
                first_name=first_name,
                last_name=last_name,
                password=hashed_password,
                email=email,
            )
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            abort(400, message="User already exists")

        except OperationalError as err:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            abort(500, message=str(err))

        except Exception as err:
            db.session.rollback()
            abort(500, message=str(err))

        wallet_id = create_wallet(user.id)
        user.wallet_id = wallet_id

        try:
            db.session.add(user)
            db.session.commit()

        except OperationalError as err:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError:
            db.session.rollback()
            abort(503, message="Service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Oops...something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Error creating wallet")

        return user


@blp.route("/login")
class LoginUser(MethodView):
    @blp.arguments(LoginSchema, location="form")
    @blp.response(200, LoginSchema)
    def post(self, user_data):
        """Authenticate and generate token for user"""
        email = user_data["email"]
        password = user_data["password"]

        try:
            user = User.query.filter(User.email == email).first()

        except OperationalError:
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError:
            abort(503, message="Service unavailable")

        if not user:
            abort(404, message="User not found.")

        if user and pbkdf2_sha256.verify(password, user.password):
            user.update_access_token()

            try:
                db.session.add(user)
                db.session.commit()

            except OperationalError:
                abort(503, message="Service unavailable")

            except SQLAlchemyOperationalError:
                db.session.rollback()
                abort(503, message="Service unavailable")

            except SQLAlchemyError as err:
                db.session.rollback()
                abort(500, message=str(err))

            except Exception as err:
                db.session.rollback()
                print(str(err))
                abort(500, message="Error signing in")

            return user

        abort(401, message="Invalid email or password")


@blp.route("/<uuid:user_id>/profile")
class GetUser(MethodView):
    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self, user_id):
        """Retrieve user profile"""
        try:
            user = User.query.get_or_404(user_id)

        except NoResultFound:
            abort(404, message="User not found")

        except OperationalError as err:
            abort(503, message="Service unavailable")

        except SQLAlchemyOperationalError as err:
            abort(503, message="Service unavailable")

        except SQLAlchemyError as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        except Exception as err:
            db.session.rollback()
            print(str(err))
            abort(500, message="Something went wrong")

        return user


@blp.route("/current-user")
class GetCurrentUser(MethodView):
    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self):
        """Fetch the current user"""
        current_user = get_current_user()
        if current_user:
            return current_user
        else:
            abort(404, message="user not found")
