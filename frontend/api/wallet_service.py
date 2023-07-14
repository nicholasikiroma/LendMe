"""Module handles communication between Frontend interface and wallet service"""
from urllib.parse import urljoin
import httpx
from flask import session
from . import WALLET_API_URL
from .error_handler import handle_response

TIMEOUT = 5


class WalletClient:
    """client for interfacing with Wallet service"""

    @staticmethod
    def create_wallet():
        """Create a wallet"""
        url = urljoin(WALLET_API_URL, "/api/wallets")
        headers = {"Authorization": session["access_token"]}
        payload = {"user_id": session["id"]}

        response = httpx.post(url, headers=headers, json=payload)

        return handle_response(response)

    @staticmethod
    def get_wallet(wallet_id):
        """Fetch a wallet"""
        url = urljoin(WALLET_API_URL, f"/api/wallets/{wallet_id}")
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        try:
            response = httpx.get(url, headers=headers, timeout=TIMEOUT)

        except httpx.ReadTimeout:
            pass
        return handle_response(response)

    @staticmethod
    def delete_wallet(wallet_id):
        """Delete a wallet"""
        url = urljoin(WALLET_API_URL, f"/api/wallets/{wallet_id}")
        headers = {"Authorization": session["access_token"]}

        response = httpx.delete(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def create_transaction(form):
        """Initiate a transaction"""
        wallet_id = session["current_user"]["wallet_id"]
        payload = {
            "sender_id": form.sender_id.data,
            "receiver_id": form.receiver_id.data,
            "amount": form.amount.data,
            "narration": form.narration.data,
        }
        url = urljoin(WALLET_API_URL, f"/api/wallets/{wallet_id}/transactions")

        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.post(url, headers=headers, data=payload)

        return handle_response(response)

    @staticmethod
    def get_transaction(wallet_id, transaction_id):
        """Fetch transaction details"""
        url = urljoin(
            WALLET_API_URL, f"/api/wallets/{wallet_id}/transactions/{transaction_id}"
        )
        access_token = "Bearer " + session["access_token"]
        headers = {"Authorization": access_token}

        response = httpx.get(url, headers=headers)

        return handle_response(response)

    @staticmethod
    def fund_wallet(wallet_id, amount):
        """Fund a wallet"""
        url = urljoin(WALLET_API_URL, f"/api/wallets/{wallet_id}/fund")
        headers = {"Authorization": session["access_token"]}
        payload = {"amount": amount}

        response = httpx.put(url, headers=headers, json=payload)

        return handle_response(response)
