"""Module handles communication between Frontend interface and User service"""
from urllib.parse import urljoin
from . import USER_API_URL
from flask import session
import httpx
from .error_handler import handle_response


class UserClient:
    @staticmethod
    def create_user(form):
        """Make API call to create a new user"""
        payload = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "password": form.password.data,
        }
        url = urljoin(USER_API_URL, "/api/users/register")

        response = httpx.post(url, data=payload)

        return handle_response(response)

    @staticmethod
    def login_user(form):
        """Add user to session"""
        payload = {"email": form.email.data, "password": form.password.data}
        url = urljoin(USER_API_URL, "/api/users/login")

        response = httpx.post(url, data=payload)

        return handle_response(response)

    @staticmethod
    def get_current_user():
        """Fetch current user from the user service"""
        url = urljoin(USER_API_URL, "/api/users/current-user")
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.get(url, headers=headers)

        return handle_response(response)
