from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1) Path to your downloaded service account JSON key
SERVICE_ACCOUNT_FILE = r"C:\Users\DCALL\Desktop\utahmmc\google-cloud-console\workspace-automation-sa.json"  # <- change this

# 2) An admin user in your Workspace domain
DELEGATED_ADMIN = "dcall@utahmmc.com"  # <- change this

# 3) Scopes you allowed in the Admin Console (read-only for now)
SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly"
]

def main():
    # Build credentials from the service account file
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )

    # Impersonate the admin user
    delegated_creds = creds.with_subject(DELEGATED_ADMIN)

    # Build the Admin SDK Directory API client
    service = build("admin", "directory_v1", credentials=delegated_creds)

    # Call the API: list first 10 users
    results = service.users().list(
        customer="my_customer",
        maxResults=10,
        orderBy="email"
    ).execute()

    users = results.get("users", [])

    if not users:
        print("No users found.")
    else:
        print("Users:")
        for user in users:
            email = user.get("primaryEmail")
            name = user.get("name", {}).get("fullName")
            print(f"- {email} ({name})")

if __name__ == "__main__":
    main()
