"""Module handles user creation and authentication"""
import functools
from flask import Blueprint, redirect, render_template, flash, request, session, url_for
from api.user_service import UserClient
from forms import LoginForm, SignUpForm


blp = Blueprint(
    "user_auth", __name__, url_prefix="/auth", template_folder="../templates/auth"
)


def login_required(view):
    """Handler for protected routes"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user = session.get("current_user", None)
        if user is None:
            return redirect(url_for("user_auth.login"))

        return view(**kwargs)

    return wrapped_view


@blp.route("/register", methods=["GET", "POST"])
def register():
    """Create new user"""
    form = SignUpForm()
    if request.method == "POST" and form.validate_on_submit():
        response = UserClient.create_user(form)
        user_id = response.get("id", None)
        if user_id:
            flash("Account created!")
            return redirect(url_for("user_auth.login"))
        else:
            flash(response["error"])
    return render_template("signUp.html", form=form)


@blp.route("/login", methods=["GET", "POST"])
def login():
    """Store authenticated user in login session"""
    form = LoginForm()

    if request.method == "POST" and form.validate_on_submit():
        response = UserClient.login_user(form)
        access_token = response.get("access_token", None)
        if access_token:
            session["access_token"] = access_token

            current_user = UserClient.get_current_user()
            user_id = current_user.get("id", None)
            if user_id:
                session["current_user"] = current_user
                return redirect(url_for("dashboard.dashboard"))

            else:
                flash("Could not login. Please try again.")

        else:
            flash(response["error"])

    return render_template("login.html", form=form)


@blp.route("/logout")
def logout():
    """Clear user from session"""
    session.clear()
    return redirect(url_for("index.index"))
