# google_clients.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# ---- CONFIG ----
SERVICE_ACCOUNT_FILE = r"C:\Users\DCALL\Desktop\utahmmc\google-cloud-console\workspace-automation-sa.json"
ADMIN_EMAIL = "dcall@utahmmc.com"  # super admin or admin user in your domain

# Common scopes you'll use
DIRECTORY_SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.group",
]

# For Gmail “settings” stuff (labels, filters, send-as)
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://www.googleapis.com/auth/gmail.settings.sharing",
    "https://www.googleapis.com/auth/gmail.labels",
]


def _base_creds(scopes):
    """Create base service-account creds (no user impersonation yet)."""
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scopes,
    )


def get_directory_service(impersonate_email: str = ADMIN_EMAIL):
    """Admin SDK Directory API client (for users + groups)."""
    creds = _base_creds(DIRECTORY_SCOPES).with_subject(impersonate_email)
    return build("admin", "directory_v1", credentials=creds)


def get_gmail_service(user_email: str):
    """Gmail API client, impersonating the given user."""
    creds = _base_creds(GMAIL_SCOPES).with_subject(user_email)
    return build("gmail", "v1", credentials=creds)
