from google.oauth2 import service_account
from googleapiclient.discovery import build

# Re-use the same key file path that worked before
SERVICE_ACCOUNT_FILE = r"C:\Users\DCALL\Desktop\utahmmc\google-cloud-console\workspace-automation-sa.json"

# The user whose mailbox you want to inspect
USER_EMAIL = "dcall@utahmmc.com"  # <- change if needed

SCOPES = [
    "https://www.googleapis.com/auth/gmail.labels",
]

def main():
    # Build service account credentials
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )

    # Impersonate the mailbox owner
    delegated_creds = creds.with_subject(USER_EMAIL)

    # Build Gmail API client
    gmail = build("gmail", "v1", credentials=delegated_creds)

    # List labels
    result = gmail.users().labels().list(userId="me").execute()
    labels = result.get("labels", [])

    if not labels:
        print("No labels found.")
    else:
        print(f"Labels for {USER_EMAIL}:")
        for label in labels:
            print(f"- {label['name']} (id: {label['id']})")

if __name__ == "__main__":
    main()
