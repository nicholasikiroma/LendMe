"""Base Application for User service"""
import os

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from flask import Flask
from dotenv import load_dotenv

from models import User
from db import db
from routes import blp as user_blueprint


def create_app(db_url=None):
    # create instance of flask app
    app = Flask(__name__)
    # access env file
    load_dotenv()

    # base configurations for flask app
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "USER REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Initialise database
    db.init_app(app)

    # Initialize flask jwt extended
    jwt_manager = JWTManager(app)
    # Initialise SMOREST
    api = Api(app)

    # Initialise flask migrate
    migrate = Migrate(app, db)

    @jwt_manager.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(email=identity).one_or_none()

    with app.app_context():
        db.create_all()

    api.register_blueprint(user_blueprint, url_prefix="/api/users")
    return app
