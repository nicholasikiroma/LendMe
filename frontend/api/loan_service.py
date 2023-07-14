"""Module handles communication between Frontend interface and Loan service"""
from . import LOAN_API_URL
from flask import session
import httpx
from urllib.parse import urljoin
from .error_handler import handle_response


class LoanClient:
    """defines methods for fetching loan service"""

    @staticmethod
    def get_all_loans():
        """Fetch all loans"""
        url = urljoin(LOAN_API_URL, "/api/loans/")

        response = httpx.get(url)

        return handle_response(response)

    @staticmethod
    def get_user_loans(user_id):
        """Fetch all loans associated with user"""
        url = urljoin(LOAN_API_URL, f"/api/loans/user/{user_id}/loans")

        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.get(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def get_user_applications(user_id):
        """Fetch all loans associated with user"""
        url = urljoin(LOAN_API_URL, f"/api/loans/user/{user_id}/applications")

        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.get(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def create_loan(form):
        """Create a loan"""
        payload = {
            "lender_id": form.lender_id.data,
            "interest": form.interest.data,
            "duration": form.duration.data,
            "amount": form.amount.data,
        }
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        url = urljoin(LOAN_API_URL, "/api/loans/")

        response = httpx.post(url, headers=headers, data=payload)

        return handle_response(response)

    @staticmethod
    def fetch_loan(loan_id):
        """Fetch details of a loan"""
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        url = urljoin(LOAN_API_URL, f"/api/loans/{loan_id}")

        response = httpx.get(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def delete_loan(loan_id):
        """Delete loan"""
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        url = urljoin(LOAN_API_URL, f"/api/loans/{loan_id}")

        response = httpx.delete(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def get_repayment_details(loan_id):
        """Fetch repayment details for loan"""
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        url = urljoin(LOAN_API_URL, f"/api/loans/{loan_id}/repayments")

        response = httpx.get(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def accept_application(application_id):
        """Accept loan application"""
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        url = urljoin(LOAN_API_URL, f"/api/loans/{application_id}/applications")

        response = httpx.get(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def apply_to_loan(loan_id=None, lender_id=None, borrower_id=None):
        """Apply to loan"""
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        url = urljoin(LOAN_API_URL, f"/api/loans/{loan_id}/applications")

        payload = {"borrower_id": borrower_id, "lender_id": lender_id}
        response = httpx.post(url, headers=headers, json=payload)

        return handle_response(response)

    @staticmethod
    def update_start_date(start_date, loan_id):
        """Start loan"""
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        url = urljoin(LOAN_API_URL, f"/api/loans/{loan_id}/start-date")

        payload = {"start_date": str(start_date)}
        response = httpx.put(url, headers=headers, json=payload)

        return handle_response(response)

    @staticmethod
    def update_end_date(end_date, loan_id):
        """end loan"""
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        url = urljoin(LOAN_API_URL, f"/api/loans/{loan_id}/end-date")

        payload = {"end_date": str(end_date)}
        response = httpx.put(url, headers=headers, json=payload)

        return handle_response(response)
