#!/usr/bin/env python3
"""
Sync Gmail 'Send mail as' aliases for one user (dcall@utahmmc.com),
based on Google Group membership across three brands:

- tntdump.com
- icondumpsters.com
- utahwatergardens.com

For each alias address (e.g. accounts@tntdump.com):

- If user IS a member of the group with that email:
    -> ensure a Gmail "Send mail as" alias exists.
- If user is NOT a member:
    -> delete the Gmail "Send mail as" alias if it exists.
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------- CONFIG ---------- #

SERVICE_ACCOUNT_FILE = r"C:\Users\DCALL\Desktop\utahmmc\google-cloud-console\workspace-automation-sa.json"  # path to your SA JSON key
USER_EMAIL = "jwest@utahmmc.com"                  # user whose aliases we manage
ADMIN_SUBJECT = "dcall@utahmmc.com"               # super admin for Directory API

SCOPES = [
    "https://www.googleapis.com/auth/gmail.settings.sharing",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://www.googleapis.com/auth/admin.directory.group.member.readonly",
]

# All potential aliases for this user across TNT, Icon, and UWG.
ALIASES = [
    # ---------- tntdump.com ----------
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

    # ---------- icondumpsters.com ----------
    "inbox@icondumpsters.com",
    "icon-dev@icondumpsters.com",
    "accounts@icondumpsters.com",
    "ap@icondumpsters.com",
    "ar@icondumpsters.com",
    "billing@icondumpsters.com",
    "contact@icondumpsters.com",
    "dev@icondumpsters.com",
    "estimates@icondumpsters.com",
    "hr@icondumpsters.com",
    "info@icondumpsters.com",
    "it@icondumpsters.com",
    "jobs@icondumpsters.com",
    "legal@icondumpsters.com",
    "marketing@icondumpsters.com",
    "noreply@icondumpsters.com",
    "payroll@icondumpsters.com",
    "projects@icondumpsters.com",
    "sales@icondumpsters.com",
    "security@icondumpsters.com",
    "service@icondumpsters.com",
    "support@icondumpsters.com",
    "vendors@icondumpsters.com",

    # ---------- utahwatergardens.com ----------
    "inbox@utahwatergardens.com",
    "uwg-dev@utahwatergardens.com",
    "accounts@utahwatergardens.com",
    "ap@utahwatergardens.com",
    "ar@utahwatergardens.com",
    "billing@utahwatergardens.com",
    "contact@utahwatergardens.com",
    "dev@utahwatergardens.com",
    "estimates@utahwatergardens.com",
    "hr@utahwatergardens.com",
    "info@utahwatergardens.com",
    "it@utahwatergardens.com",
    "jobs@utahwatergardens.com",
    "legal@utahwatergardens.com",
    "marketing@utahwatergardens.com",
    "noreply@utahwatergardens.com",
    "payroll@utahwatergardens.com",
    "projects@utahwatergardens.com",
    "sales@utahwatergardens.com",
    "security@utahwatergardens.com",
    "service@utahwatergardens.com",
    "support@utahwatergardens.com",
    "vendors@utahwatergardens.com",
]

# Brand display names per domain
DOMAIN_DISPLAY_NAME = {
    "tntdump.com": "TNT Dumpsters",
    "icondumpsters.com": "Icon Dumpsters",
    "utahwatergardens.com": "Utah Water Gardens",
}


# ---------- AUTH HELPERS ---------- #

def get_base_credentials():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    # Debug
    print(f"Using service account: {creds.service_account_email}")
    return creds


def get_directory_service():
    base_creds = get_base_credentials()
    delegated = base_creds.with_subject(ADMIN_SUBJECT)
    print(f"Directory API delegated to: {ADMIN_SUBJECT}")
    return build("admin", "directory_v1", credentials=delegated)


def get_gmail_service_for_user(user_email: str):
    base_creds = get_base_credentials()
    delegated = base_creds.with_subject(user_email)
    print(f"Gmail API delegated to: {user_email}")
    return build("gmail", "v1", credentials=delegated)


# ---------- DIRECTORY HELPERS ---------- #

def is_user_member_of_group(directory, group_email: str, user_email: str) -> bool:
    """
    Uses Admin SDK Directory members.hasMember to check if user is in group.
    If the group doesn't exist or can't be checked, returns False.
    """
    try:
        resp = directory.members().hasMember(
            groupKey=group_email,
            memberKey=user_email,
        ).execute()
        is_member = bool(resp.get("isMember"))
        print(f"[CHECK] {user_email} in {group_email}: {is_member}")
        return is_member
    except HttpError as e:
        status = getattr(e.resp, "status", None)
        print(
            f"[WARN] could not check membership for {user_email} in {group_email}: "
            f"HTTP {status} {e}"
        )
        return False


# ---------- GMAIL HELPERS ---------- #

def list_existing_send_as(gmail):
    resp = gmail.users().settings().sendAs().list(userId="me").execute()
    send_as = resp.get("sendAs", [])
    return {entry["sendAsEmail"].lower(): entry for entry in send_as}


def get_display_name_for_alias(alias_email: str) -> str:
    """
    Choose a reasonable From: display name based on the alias domain.
    E.g., "TNT Dumpsters" for any @tntdump.com alias.
    """
    domain = alias_email.split("@")[-1].lower()
    return DOMAIN_DISPLAY_NAME.get(domain, alias_email)


def create_alias(gmail, user_email: str, alias_email: str):
    display_name = get_display_name_for_alias(alias_email)
    body = {
        "sendAsEmail": alias_email,
        "displayName": display_name,
        "treatAsAlias": True,
    }
    print(f"[ADD]   Creating send-as alias {alias_email} for {user_email} "
          f"(displayName='{display_name}')")
    created = gmail.users().settings().sendAs().create(
        userId="me",
        body=body,
    ).execute()
    print(f"       -> verificationStatus={created.get('verificationStatus')}")


def delete_alias(gmail, user_email: str, alias_email: str):
    print(f"[REMOVE] Deleting send-as alias {alias_email} for {user_email}")
    gmail.users().settings().sendAs().delete(
        userId="me",
        sendAsEmail=alias_email,
    ).execute()


# ---------- MAIN SYNC LOGIC ---------- #

def sync_user_aliases(user_email: str):
    directory = get_directory_service()
    gmail = get_gmail_service_for_user(user_email)

    existing = list_existing_send_as(gmail)
    print("Existing send-as before sync:")
    for addr in sorted(existing.keys()):
        print(f"  - {addr}")

    print("\nSyncing aliases based on group membership...\n")

    for alias in ALIASES:
        alias_lc = alias.lower()
        member = is_user_member_of_group(directory, alias, user_email)
        has_alias = alias_lc in existing

        if member and not has_alias:
            create_alias(gmail, user_email, alias)
        elif member and has_alias:
            print(f"[KEEP]  {user_email} is member of {alias}, alias already exists.")
        elif not member and has_alias:
            delete_alias(gmail, user_email, alias)
        else:
            print(f"[SKIP]  {user_email} is NOT member of {alias}, and alias not configured.")

    print("\nFinal send-as list after sync:")
    updated = list_existing_send_as(gmail)
    for addr in sorted(updated.keys()):
        print(f"  - {addr}")


if __name__ == "__main__":
    print(f"Syncing send-as aliases for {USER_EMAIL}")
    sync_user_aliases(USER_EMAIL)
    print("\nDone. In Gmail UI for this user, make sure:")
    print('  Settings → Accounts → "Reply from the same address the message was sent to" is selected.')
