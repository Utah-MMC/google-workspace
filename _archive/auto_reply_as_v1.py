#!/usr/bin/env python3
"""
Create Gmail "Send mail as" aliases for a single user (dcall@utahmmc.com)
using a service account with domain-wide delegation.

Prereqs:
- Gmail API enabled in your Google Cloud project.
- Service account with domain-wide delegation.
- In Admin Console, that service account has the scope:
    https://www.googleapis.com/auth/gmail.settings.sharing
- In Gmail UI for dcall@utahmmc.com you have already set:
    Settings → Accounts → "Reply from the same address the message was sent to"
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

# ------------- CONFIG ------------- #

SERVICE_ACCOUNT_FILE = "service-account-key.json"  # path to your JSON key
USER_EMAIL = "dcall@utahmmc.com"                   # user to impersonate

SCOPES = ["https://www.googleapis.com/auth/gmail.settings.sharing"]

ALIASES = [
    "inbox@tntdump.com",
    "accounts@tntdump.com",
    "ap@tntdump.com",
    "ar@tntdump.com",
    "billing@tntdump.com",
    "contact@tntdump.com",
    "dev@tntdump.com",
    "estimates@tntdump.com",
    "hr@tntdump.com",
    "info@tntdump.com",
    "it@tntdump.com",
    "jobs@tntdump.com",
    "legal@tntdump.com",
    "marketing@tntdump.com",
    "media@tntdump.com",
    "noreply@tntdump.com",
    "payroll@tntdump.com",
    "projects@tntdump.com",
    "security@tntdump.com",
    "service@tntdump.com",
    "support@tntdump.com",
    "vendors@tntdump.com",
]

# Optional: a simple way to choose a display name for all TNT aliases.
# You can also make this a dict if you want different names per address.
DEFAULT_DISPLAY_NAME = "TNT Dumpsters"


# ------------- HELPERS ------------- #

def get_gmail_service_for_user(user_email: str):
    """Build a Gmail API client impersonating the given user."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    delegated = creds.with_subject(user_email)
    return build("gmail", "v1", credentials=delegated)


def list_existing_send_as(gmail):
    """Return a dict of existing send-as aliases keyed by email (lowercased)."""
    resp = gmail.users().settings().sendAs().list(userId="me").execute()
    send_as = resp.get("sendAs", [])
    return {entry["sendAsEmail"].lower(): entry for entry in send_as}


def create_alias_if_missing(gmail, user_email: str, alias_email: str):
    """Create a send-as alias if it does not already exist."""
    existing = list_existing_send_as(gmail)

    if alias_email.lower() in existing:
        print(f"[{user_email}] alias already exists: {alias_email}")
        return

    body = {
        "sendAsEmail": alias_email,
        "displayName": DEFAULT_DISPLAY_NAME,
        # For org-internal addresses, treatAsAlias=True is usually what you want.
        "treatAsAlias": True,
        # Don't set isDefault here; default 'From' is for NEW mail,
        # replies will respect your Gmail 'reply from same address' setting.
    }

    print(f"[{user_email}] creating alias: {alias_email}")
    created = gmail.users().settings().sendAs().create(
        userId="me",
        body=body,
    ).execute()

    # created["verificationStatus"] may be "accepted" or "pending".
    # If it's "pending", Gmail will have sent a verification email to the alias.
    print(
        f"  -> status: {created.get('verificationStatus', 'unknown')} "
        f"(displayName={created.get('displayName')})"
    )


def main():
    gmail = get_gmail_service_for_user(USER_EMAIL)

    print(f"Working on user: {USER_EMAIL}")
    print("Existing send-as addresses before changes:")
    existing = list_existing_send_as(gmail)
    for addr in sorted(existing.keys()):
        print(f"  - {addr}")

    print("\nEnsuring aliases exist:")
    for alias in ALIASES:
        create_alias_if_missing(gmail, USER_EMAIL, alias)

    print("\nDone. Now check Gmail → Settings → Accounts for dcall@utahmmc.com")
    print("If any aliases show verificationStatus = 'pending',")
    print("Gmail will have emailed that address for confirmation.")


if __name__ == "__main__":
    main()
