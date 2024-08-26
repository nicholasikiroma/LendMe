"""Base Application for Frontend service"""
import os
from datetime import datetime
from logging.config import dictConfig

from flask import Flask, send_from_directory
from dotenv import load_dotenv

from routes import index_blueprint, dashboard_blueprint, auth_blueprint


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'ERROR',
        'handlers': ['wsgi']
    }
})

def create_app():
    # create instance of flask app
    app = Flask(__name__)
    # access env file
    load_dotenv()

    # base configurations for flask app 
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%B %d, %Y, %H:%M'):
        if isinstance(value, datetime):
            return value.strftime(format)
        return value
    
    app.register_blueprint(index_blueprint)
    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(auth_blueprint)

    @app.route("/preline.js")
    def serve_preline_js():
        return send_from_directory("node_modules/preline/dist", "preline.js")


    return app
