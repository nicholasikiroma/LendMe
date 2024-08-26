"""Module handles communication between Frontend interface and Risk service"""

from urllib.parse import urljoin
import httpx
from flask import session
from . import RISK_API_URL
from .error_handler import handle_response


class RiskClient:
    """Defines methods for interacting with risk assessment service"""

    @staticmethod
    def get_finance_profile(borrower_id):
        """Fetch financial profile for borrower"""
        url = urljoin(RISK_API_URL, f"/api/risk/{borrower_id}/profile")
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.get(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def create_finance_profile(form):
        """Create financial profile for borrower"""
        borrower_id = session["id"]
        payload = {
            "credit_score": form.credit_score.data,
            "monthly_income": form.monthly_income.data,
            "debt_payments": form.debt_payments.data,
            "employment_status": form.employment_status.data,
        }
        url = urljoin(RISK_API_URL, f"/api/risk/{borrower_id}/profile")
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.post(url, headers=headers, data=payload)

        return handle_response(response)

    @staticmethod
    def delete_finance_profile(borrower_id):
        """Delete financial profile for borrower"""
        url = urljoin(RISK_API_URL, f"/api/risk/{borrower_id}/profile")
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.delete(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def create_finance_report(borrower_id, loan_amount, loan_id):
        """Create financial assessment report for borrower"""
        url = urljoin(RISK_API_URL, f"/api/risk/{borrower_id}/report")
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}
        payload = {"loan_amount": loan_amount, "loan_id": loan_id}

        response = httpx.post(url, headers=headers, data=payload)

        return handle_response(response)

    @staticmethod
    def fetch_finance_report(borrower_id):
        """Fetch financial assessment report for borrower"""
        url = urljoin(RISK_API_URL, f"/api/risk/{borrower_id}/report")
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.get(url, headers=headers)

        return handle_response(response)
