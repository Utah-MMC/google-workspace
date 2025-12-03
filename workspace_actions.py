# workspace_actions.py
from typing import List
from googleapiclient.errors import HttpError

from google_clients import get_directory_service, get_gmail_service, ADMIN_EMAIL

# ---------- USER & GROUP MANAGEMENT ----------

def list_users(max_results: int = 20):
    service = get_directory_service()
    result = service.users().list(
        customer="my_customer",
        maxResults=max_results,
        orderBy="email"
    ).execute()
    return result.get("users", [])


def create_user(primary_email: str, given_name: str, family_name: str, password: str):
    service = get_directory_service()
    body = {
        "primaryEmail": primary_email,
        "name": {
            "givenName": given_name,
            "familyName": family_name,
        },
        "password": password,
    }

    user = service.users().insert(body=body).execute()
    return user


def create_group(email: str, name: str, description: str = ""):
    service = get_directory_service()
    body = {
        "email": email,
        "name": name,
        "description": description,
    }
    group = service.groups().insert(body=body).execute()
    return group


def add_member_to_group(group_email: str, member_email: str, role: str = "MEMBER"):
    service = get_directory_service()
    body = {
        "email": member_email,
        "role": role,  # MEMBER, MANAGER, OWNER
    }
    member = service.members().insert(groupKey=group_email, body=body).execute()
    return member


# ---------- GMAIL: LABELS & FILTERS ----------

def create_label(user_email: str, label_name: str):
    gmail = get_gmail_service(user_email)
    label_body = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    }
    label = gmail.users().labels().create(userId="me", body=label_body).execute()
    return label


def list_labels(user_email: str):
    gmail = get_gmail_service(user_email)
    result = gmail.users().labels().list(userId="me").execute()
    return result.get("labels", [])


def create_filter_from_address(user_email: str, from_address: str, label_name: str):
    """
    If label doesn't exist, creates it.
    Then creates a filter: if From == from_address, apply label.
    """
    gmail = get_gmail_service(user_email)

    # 1) Ensure label exists
    labels = list_labels(user_email)
    label_id = None
    for l in labels:
        if l["name"].lower() == label_name.lower():
            label_id = l["id"]
            break

    if not label_id:
        label = create_label(user_email, label_name)
        label_id = label["id"]

    # 2) Create filter
    filter_body = {
        "criteria": {
            "from": from_address,
        },
        "action": {
            "addLabelIds": [label_id],
            # you could also mark as read, archive etc
            # "removeLabelIds": ["INBOX"]
        }
    }

    gmail_filter = gmail.users().settings().filters().create(
        userId="me",
        body=filter_body
    ).execute()

    return gmail_filter
