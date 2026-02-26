---
name: deepin-mail
description: Interact with deepin-mail via D-Bus to read, send, search, and manage emails. Use this skill whenever the user asks about email operations on Deepin OS, mentions deepin-mail specifically, or wants to read/send/search emails. This covers fetching inbox messages, checking unread counts, composing new emails, searching through emails, and marking emails as read/unread/deleted.
compatibility: Requires gdbus (usually available with glib2-tools) and deepin-mail running on the session D-Bus
---

# Deepin Mail D-Bus Skill

This skill enables interaction with deepin-mail (the email client on Deepin OS) via D-Bus. It supports reading, sending, searching, and managing emails.

## Prerequisites

- Deepin OS with deepin-mail installed and running
- `gdbus` command-line tool (typically available via `glib2-tools` or `libglib2.0-tools`)
- The deepin-mail service must be active on the D-Bus session bus

## Available Operations

### 1. Get Accounts
List all configured email accounts.

**Use when:** User asks what accounts are available, or you need to determine the account to use.

### 2. Get Unread Count
Check the number of unread emails for an account.

**Use when:** User asks about unread emails, new messages, or email notifications.

### 3. Get Mails
Retrieve a list of emails from a specific folder (e.g., INBOX, Sent, Drafts).

**Parameters:**
- `account`: Account identifier (use default if not specified)
- `folderName`: Folder name (common: INBOX, Sent, Drafts, Trash, Spam)
- `limit`: Maximum number of emails to retrieve

**Use when:** User wants to read emails, check inbox, see recent messages.

### 4. Get Mail Detail
Get full details of a specific email including body content.

**Parameters:**
- `account`: Account identifier
- `folderName`: Folder containing the email
- `mailId`: The email's ID

**Use when:** User wants to read the full content of a specific email.

### 5. Search Mails
Search emails by keywords across subject, sender, body, etc.

**Parameters:**
- `account`: Account identifier
- `keywords`: Search terms
- `limit`: Maximum results

**Use when:** User wants to find emails containing specific words, from a specific person, or about a particular topic.

### 6. Send Mail
Compose and send a new email.

**Parameters:**
- `account`: Account to send from
- `to`: Recipient email address
- `subject`: Email subject line
- `body`: Email body content
- `cc`: CC recipients (optional, empty string if none)
- `attachments`: File paths as comma-separated string (optional)

**Use when:** User wants to compose, send, or draft an email.

### 7. Mark Mails
Perform actions on emails (mark as read/unread, delete, star/unstar).

**Parameters:**
- `account`: Account identifier
- `mailIds`: Comma-separated email IDs
- `action`: One of: `read`, `unread`, `delete`, `star`, `unstar`

**Use when:** User wants to mark emails as read, archive, delete, or flag important messages.

## Workflow

### Reading Emails

1. If user doesn't specify an account, get the default account
2. Call `GetMails` with the account, folder (default: INBOX), and limit
3. Present the email list to the user (subject, sender, date, snippet)
4. If user wants to read a specific email, call `GetMailDetail` with the mail ID

### Sending Emails

1. Get the default account (or ask user to specify if multiple)
2. Collect email details: recipient, subject, body
3. Optionally collect CC recipients and attachments
4. Call `SendMail` with all parameters
5. Report the result to the user

### Searching Emails

1. Get the default account
2. Extract search keywords from user's request
3. Call `SearchMails` with keywords
4. Present matching results

### Checking Unread

1. Get the default account
2. Call `GetUnread`
3. Report the unread count to the user

## Account Handling

By default, use the **first account** returned by `GetAccounts()` unless the user explicitly specifies a different account. This simplifies the user experience for single-account setups.

## Using the D-Bus Script

The skill includes a Python script at `scripts/dbus_client.py` that wraps all D-Bus operations. Use this script for all interactions:

```python
# Import the client
import sys
sys.path.insert(0, '<skill-path>/scripts')
from dbus_client import DeepinMailDBusClient

client = DeepinMailDBusClient()

# Get accounts
accounts = client.get_accounts()

# Get default account
account = client.get_default_account()

# Get emails from inbox
mails = client.get_mails(account, "INBOX", 20)

# Get unread count
unread = client.get_unread(account)

# Search emails
results = client.search_mails(account, "project update", 20)
```

## Error Handling

- If deepin-mail is not running, inform the user they need to start the application first
- If gdbus is not available, suggest installing `glib2-tools` (or distro equivalent)
- If an account is not found or is invalid, ask the user to verify their account setup
- Parse all JSON responses carefully and report any parsing errors to the user

## Output Format

When presenting emails to users, include:
- **Subject**: Clear and prominent
- **Sender**: From address or name
- **Date**: When the email was received
- **Preview**: Brief snippet of the email body
- **ID**: For reference when requesting full details

Use a clean, readable format. Example:

```
📧 You have 3 unread emails

[1] Project Update - From: john@example.com - Date: 2025-02-26
    Preview: The new design has been approved...

[2] Meeting Reminder - From: sarah@company.com - Date: 2025-02-26
    Preview: Don't forget our sync tomorrow...

[3] Newsletter - From: news@weekly.com - Date: 2025-02-25
    Preview: This week's top stories...
```

## Common User Phrases That Should Trigger This Skill

- "Check my email" / "Read my emails"
- "Send an email to X"
- "Search for emails about Y"
- "How many unread emails?"
- "Show me my inbox"
- "Compose an email"
- "Any new messages?"
- "Find emails from X"
- "Mark as read"
- "Deepin mail operations"

## Notes

- All D-Bus calls return JSON-formatted strings that need to be parsed
- The D-Bus service is on the **session bus**, not system bus
- Mail IDs are integers and uniquely identify emails within a folder
- Folder names are case-sensitive (typically all caps like INBOX, Sent, Drafts)
