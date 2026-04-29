import requests
from typing import List, Dict, Any
from src.config import config
import base64

class MifosClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        auth_string = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode()
        session.headers.update({
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json"
        })
        return session

    def get_clients(self) -> List[Dict[str, Any]]:
        """Fetch all clients from Mifos X"""
        try:
            response = self.session.get(f"{self.base_url}/clients")
            response.raise_for_status()
            return response.json().get("pageItems", [])
        except requests.RequestException as e:
            print(f"Error fetching clients: {e}")
            return []

    def get_client_accounts(self, client_id: int) -> List[Dict[str, Any]]:
        """Fetch loan accounts for a specific client"""
        try:
            response = self.session.get(f"{self.base_url}/clients/{client_id}")
            response.raise_for_status()
            client_data = response.json()
            return client_data.get("loans", [])
        except requests.RequestException as e:
            print(f"Error fetching accounts for client {client_id}: {e}")
            return []

    def get_account_details(self, account_id: int) -> Dict[str, Any]:
        """Fetch detailed account information"""
        try:
            response = self.session.get(f"{self.base_url}/loans/{account_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching account {account_id}: {e}")
            return {}

    def send_reminder(self, client_id: int, message: str) -> bool:
        """Send a reminder to a client"""
        try:
            payload = {
                "clientId": client_id,
                "message": message,
                "type": "reminder"
            }
            response = self.session.post(
                f"{self.base_url}/clients/{client_id}/notes",
                json=payload
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error sending reminder: {e}")
            return False

    def schedule_followup(self, client_id: int, date: str) -> bool:
        """Schedule a follow-up for a client"""
        try:
            payload = {
                "clientId": client_id,
                "followUpDate": date,
                "status": "scheduled"
            }
            response = self.session.post(
                f"{self.base_url}/clients/{client_id}/followups",
                json=payload
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error scheduling followup: {e}")
            return False

    def escalate_case(self, client_id: int, reason: str, loan_officer_id: int) -> bool:
        """Escalate a case to a loan officer"""
        try:
            payload = {
                "clientId": client_id,
                "reason": reason,
                "assignedTo": loan_officer_id
            }
            response = self.session.post(
                f"{self.base_url}/clients/{client_id}/escalations",
                json=payload
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error escalating case: {e}")
            return False
