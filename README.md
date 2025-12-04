# Google Workspace SDK Automation Toolkit

This repo contains a minimal set of Google Admin SDK and Gmail API helpers plus an OpenAI powered dispatcher that can translate natural language into concrete Workspace automation calls. It is designed to be a starting point for building internal admin tools that can create users, groups, and Gmail automations on demand.

## What You Can Do
- **User and group management** (`workspace_actions.py`): list existing users, create new accounts, create groups, and add members through the Admin SDK Directory API.
- **Gmail configuration** (`workspace_actions.py`): create labels and filters that auto-apply labels based on sender, impersonating any mailbox in the domain.
- **Natural-language control** (`chat_to_workspace.py`): describe a task (e.g., "add alex@company.com to marketing@company.com") and let GPT plan and execute the correct Workspace action.
- **Demo & diagnostics** (`demo_cli.py`, `test_*.py`): quick scripts to confirm Directory, Gmail, and OpenAI connectivity before wiring everything together.

## Requirements
1. **Python** 3.10+.
2. **Google Cloud service account** with Workspace Domain-Wide Delegation enabled and the Admin scopes granted through the Admin Console security page.
3. **Service account key file path** configured inside `google_clients.py` (`SERVICE_ACCOUNT_FILE`) plus a super admin email (`ADMIN_EMAIL`). You can replace the hardcoded path with `os.environ.get(...)` if you prefer.
4. **OPENAI_API_KEY** environment variable for `chat_to_workspace.py` and `test_openai.py`.

Install the Python dependencies inside a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install google-auth google-auth-httplib2 google-api-python-client openai
```

## Usage

### 1. Verify connectivity
- `python test_list_users.py` – Lists up to 10 users to confirm Admin SDK access.
- `python test_gmail_labels.py` – Lists the labels of an impersonated mailbox to confirm Gmail scopes.
- `python test_openai.py` – Ensures the OpenAI key is visible and working.

### 2. Run the demo CLI
`python demo_cli.py` lists the first five users and includes commented examples showing how to create groups, add members, or create Gmail labels/filters. Uncomment the blocks you need, run once, and revert to avoid duplicates.

### 3. Natural-language dispatcher
`python chat_to_workspace.py` will prompt, e.g.:

```
> create a group called marketing@utahmmc.com and add dave
```

The script asks GPT-4o-mini to emit a JSON plan containing one of the supported actions (`create_group`, `add_member_to_group`, `create_filter_from_address`) and then executes it against Workspace.

### 4. Building your own tools
Import the functions in `workspace_actions.py` wherever you need automation. Every helper impersonates either the admin (`get_directory_service`) or the target user (`get_gmail_service`), so you can safely call them from bots, scheduled tasks, or webhooks. Wrap calls in additional logging/exception handling as you productionize.

## Extending The Toolkit
- Add more Admin SDK scopes to `DIRECTORY_SCOPES` or Gmail scopes to `GMAIL_SCOPES` as you enable new workflows.
- Implement additional helper functions inside `workspace_actions.py` (e.g., suspend users, reset passwords, manage aliases).
- Teach `chat_to_workspace.py` about new actions by updating the `SYSTEM_PROMPT`, importing your helper, and extending `dispatch`.

With the service account authenticated and these scripts in place, you can automate virtually any Google Workspace admin task from Python or plain English instructions.
