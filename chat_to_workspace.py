import json
import os
from openai import OpenAI

from workspace_actions import (
    create_group,
    add_member_to_group,
    create_filter_from_address,
)

# Uses the key from your OPENAI_API_KEY environment variable
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
You convert natural-language admin requests into JSON commands
for Google Workspace automation.

You MUST respond with ONLY valid JSON, no extra text.

Supported actions:

1) create_group
   params: {
     "email": string,          // group email, e.g. "marketing@utahmmc.com"
     "name": string,           // display name, e.g. "Marketing Team"
     "description": string     // optional; can be empty ""
   }

2) add_member_to_group
   params: {
     "group_email": string,    // group address
     "member_email": string,   // user address
     "role": "MEMBER" | "MANAGER" | "OWNER"
   }

3) create_filter_from_address
   params: {
     "user_email": string,     // mailbox to modify
     "from_address": string,   // match this From address
     "label_name": string      // label to apply (create if missing)
   }

Return format:
{
  "action": "<one of the above>",
  "params": { ... }
}
"""


def plan_from_text(text: str) -> dict:
    """Ask ChatGPT to turn a command into {action, params} JSON."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},  # force valid JSON
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def dispatch(plan: dict):
    """Call the right Workspace function based on the plan."""
    action = plan["action"]
    params = plan["params"]

    if action == "create_group":
        return create_group(**params)
    elif action == "add_member_to_group":
        return add_member_to_group(**params)
    elif action == "create_filter_from_address":
        return create_filter_from_address(**params)
    else:
        raise ValueError(f"Unknown action: {action}")


def main():
    print("Describe what you want to do in Google Workspace.")
    command_text = input("> ")

    print("\nAsking ChatGPT to plan that action...\n")
    plan = plan_from_text(command_text)
    print("Model plan:", plan, "\n")

    print("Calling Google Workspace APIs...")
    result = dispatch(plan)

    print("\nDone. Raw API response:")
    print(result)


if __name__ == "__main__":
    main()
