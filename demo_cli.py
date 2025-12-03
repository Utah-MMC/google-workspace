# demo_cli.py
from workspace_actions import (
    list_users,
    create_group,
    add_member_to_group,
    create_label,
    create_filter_from_address,
)

def main():
    print("Listing first 5 users:")
    users = list_users(5)
    for u in users:
        print("-", u["primaryEmail"])

    # Example: create a group (comment out after first run to avoid duplicates)
    # grp = create_group("marketing@utahmmc.com", "Marketing Team", "Marketing team group")
    # print("Created group:", grp["email"])

    # Example: add member to group
    # add_member_to_group("marketing@utahmmc.com", "some.user@utahmmc.com")

    # Example: label + filter
    # user_email = "dcall@utahmmc.com"
    # create_label(user_email, "From-ChatGPT")
    # create_filter_from_address(user_email, "news@example.com", "From-ChatGPT")

if __name__ == "__main__":
    main()
