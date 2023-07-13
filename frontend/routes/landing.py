from flask import Blueprint, render_template


blp = Blueprint("index", __name__)


@blp.route('/')
def index():
    """Render home page"""
    return render_template('index.html')
