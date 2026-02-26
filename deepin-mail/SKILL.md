---
name: deepin-mail
description: Interact with deepin-mail via D-Bus to read, send, search, and manage emails. Use this skill whenever the user asks about email operations on Deepin OS, mentions deepin-mail specifically, or wants to read/send/search emails. This covers fetching inbox messages, checking unread counts, composing new emails, searching through emails, and marking emails as read/unread/deleted.
compatibility: Requires gdbus (usually available with glib2-tools) and deepin-mail running on the session D-Bus
---

# Deepin Mail D-Bus Skill

This skill enables interaction with deepin-mail (the email client on Deepin OS) via D-Bus.

## Quick Start

**First step for ANY email operation:**

1. Get accounts and available folders:
   ```bash
   python3 <skill-path>/scripts/dbus_client.py accounts
   ```
   This returns the account ID and a list of available folders with their names.
   **Use the folder names exactly as returned** - they vary by locale (e.g., "收件箱" for Chinese, "INBOX" for English).

2. Then proceed with the user's request using the actual folder names from step 1.

## Important: Always Discover Folder Names First

Folder names depend on the user's locale and email provider. Never assume hardcoded values like "INBOX" or "收件箱".

**Correct workflow:**
```bash
# Step 1: Get accounts to discover available folders
python3 <skill-path>/scripts/dbus_client.py accounts
# Returns: {"id": "user@example.com", "folders": [{"name": "收件箱", "count": 10}, ...]}

# Step 2: Use the actual folder name from the response
python3 <skill-path>/scripts/dbus_client.py mails --folder "收件箱" --limit 10
```

**Wrong approach:**
```bash
# Don't assume English folder names - will fail on non-English systems
python3 <skill-path>/scripts/dbus_client.py mails --folder INBOX --limit 10
# Error: {"error": "Folder not found: INBOX"}
```

## CLI Commands

Use these commands directly via Bash tool:

```bash
# Get accounts and discover available folders
python3 <skill-path>/scripts/dbus_client.py accounts

# Get latest N emails from a folder
python3 <skill-path>/scripts/dbus_client.py mails --folder "<folder_name>" --limit N

# Get unread count
python3 <skill-path>/scripts/dbus_client.py unread

# Get full email detail
python3 <skill-path>/scripts/dbus_client.py detail --folder "<folder_name>" --id <mail_id>

# Search emails
python3 <skill-path>/scripts/dbus_client.py search "<keywords>" --limit N

# Send email
python3 <skill-path>/scripts/dbus_client.py send --to recipient@example.com --subject "Subject" --body "Body"

# Mark emails (does NOT need --folder parameter - mail IDs are unique)
python3 <skill-path>/scripts/dbus_client.py mark --ids "123,456" --action read
```

**Note:** The `mark` command only needs mail IDs, not the folder name.

## Common Workflows

### Reading Emails

1. Run `accounts` to get the folder list
2. Identify the inbox folder (look for highest count or typical inbox-like name)
3. Run `mails --folder "<inbox_folder>" --limit N`
4. Present as numbered list with subject, sender, date, unread status
5. If user wants detail: `detail --folder "<folder>" --id <id>`

### Checking Unread

1. Run: `unread`
2. Report the count

### Sending Email

1. Run: `send --to <email> --subject "<subject>" --body "<body>"`
2. Optional: `--cc <email>` for CC, `--attachments <paths>` for attachments

### Searching

1. Run: `search "<keywords>" --limit N`
2. Present results

### Marking Emails

Actions: `read`, `unread`, `delete`, `star`, `unstar`

```bash
python3 <skill-path>/scripts/dbus_client.py mark --ids "123,456" --action read
```

**Important:** The `mark` command does NOT require `--folder` - mail IDs are globally unique within an account.

## Response Structures

### Accounts Response
```json
[{
  "id": "email@example.com",
  "folders": [
    {"name": "<localized_folder_name>", "count": 1380},
    {"name": "<another_folder>", "count": 92}
  ]
}]
```
Use the account `id` as the account identifier. Use folder `name` values exactly as shown.

### Email List Response
```json
{
  "count": 3,
  "mails": [
    {
      "id": 57601,
      "subject": "Email subject",
      "from": "sender@example.com",
      "date": "2026-02-26 15:32:28",
      "unread": true,
      "flagged": false
    }
  ]
}
```

## Output Format

Present emails clearly:

```
📧 Latest 3 emails

[1] Subject here
    From: sender@example.com
    Date: 2026-02-26 15:32
    Status: 未读

[2] Another subject
    From: other@example.com
    Date: 2026-02-26 14:30
    Status: 已读
```

## Error Handling

| Error | Solution |
|-------|----------|
| `Folder not found: <name>` | Run `accounts` first to get the correct folder name |
| `D-Bus call failed` | deepin-mail is not running - ask user to start it |
| `gdbus not found` | Install `glib2-tools` or `libglib2.0-tools` |
| `No account found` | User needs to configure an account in deepin-mail |

## Notes

- All D-Bus calls return JSON
- Service is on **session bus**
- Mail IDs are integers
- First account is used as default if not specified
- Folder names are locale-dependent - always discover from `accounts` command
