---
name: tencent-exmail
description: Interact with Tencent Enterprise Email (腾讯企业邮箱) via qqmail-cli to read, search, and manage emails. Use this skill whenever the user asks about Tencent Exmail, mentions 腾讯企业邮箱, wants to read/search emails from their Tencent enterprise mailbox, check inbox, download attachments, or browse mail folders. This also covers any email operation that involves exmail.qq.com or imap.exmail.qq.com.
compatibility: Requires qqmail-cli installed (via `uv tool install qqmail-cli` or `pip install qqmail-cli`)
---

# Tencent Enterprise Email Skill

This skill wraps [qqmail-cli](https://pypi.org/project/qqmail-cli/) to interact with Tencent Enterprise Email via IMAP.

All qqmail commands read credentials from a `.env` file in the **current working directory**. The skill stores credentials at `~/.config/qqmail-cli/.env` and runs commands from that directory to ensure they are found.

## Pre-flight: Authentication

Before ANY email operation, verify the user is authenticated:

1. Check if the credential file exists:
   ```bash
   python3 <skill-path>/scripts/setup_auth.py check
   ```

2. If **not configured** (`"configured": false`), guide the user through setup:
   - Ask the user for their enterprise email address (e.g. `user@company.com`)
   - Ask the user for their password or app-specific token
   - Write the credential file:
     ```bash
     python3 <skill-path>/scripts/setup_auth.py write "user@company.com" "the_password"
     ```
   - Verify by running: `cd ~/.config/qqmail-cli && qqmail login`

3. If **configured**, verify the credentials are still valid:
   ```bash
   cd ~/.config/qqmail-cli && qqmail login
   ```
   If login fails, inform the user and ask if they want to reconfigure.

## CLI Commands

All commands output JSON. Add `--compact` for single-line JSON.
**Important:** Always prefix commands with `cd ~/.config/qqmail-cli &&` so the `.env` file is found.

```bash
# Verify login
cd ~/.config/qqmail-cli && qqmail login

# List all folders
cd ~/.config/qqmail-cli && qqmail folders

# Browse emails in a folder (paginated)
cd ~/.config/qqmail-cli && qqmail mails                                    # INBOX, page 1, 20 per page
cd ~/.config/qqmail-cli && qqmail mails --folder "Sent Messages" --page 2  # specific folder & page
cd ~/.config/qqmail-cli && qqmail mails --size 50                          # custom page size

# View email detail
cd ~/.config/qqmail-cli && qqmail mail 1555
cd ~/.config/qqmail-cli && qqmail mail 1555 --raw              # include forwarded history
cd ~/.config/qqmail-cli && qqmail mail 1555 --folder "Sent Messages"

# Manage attachments
cd ~/.config/qqmail-cli && qqmail attachments list 1555
cd ~/.config/qqmail-cli && qqmail attachments download 1555 -o /tmp/attachments
cd ~/.config/qqmail-cli && qqmail attachments download 1555 -f "周报.xlsx" -o /tmp/attachments
```

**Note:** If the user has upgraded to qqmail-cli 0.3.0+, the `mails search` subcommand is also available:
```bash
cd ~/.config/qqmail-cli && qqmail mails search --since 2026-04-13
cd ~/.config/qqmail-cli && qqmail mails search --since 2026-04-13 --from sender@example.com --subject 周报 --limit 5
```

## Common Workflows

### Reading Inbox

1. Run `cd ~/.config/qqmail-cli && qqmail login` to verify auth
2. Run `cd ~/.config/qqmail-cli && qqmail folders` to discover available folders
3. Run `cd ~/.config/qqmail-cli && qqmail mails` to list recent inbox emails
4. Present as a clean summary with subject, sender, date
5. For detail: `cd ~/.config/qqmail-cli && qqmail mail <id>`

### Downloading Attachments

1. Find the email via browse or search
2. List attachments: `cd ~/.config/qqmail-cli && qqmail attachments list <id>`
3. Download: `cd ~/.config/qqmail-cli && qqmail attachments download <id> -o <directory>`

## Output Format

Present emails in a clear, scannable format:

```
Latest 3 emails in INBOX

[1] Email subject here
    From: sender@example.com
    Date: 2026-04-19 16:30
    Attachments: 周报.xlsx

[2] Another subject
    From: other@example.com
    Date: 2026-04-19 14:30
```

## Error Handling

| Error | Solution |
|-------|----------|
| `Authentication failed` | Reconfigure credentials via the pre-flight flow |
| `qqmail: command not found` | Install: `uv tool install qqmail-cli` |
| `Folder not found` | Run `qqmail folders` to get correct folder names |
| Connection timeout | Check network; IMAP requires port 993 |
