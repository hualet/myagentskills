#!/usr/bin/env python3
"""
D-Bus client for deepin-mail operations.
Communicates with org.deepin.mail via session bus.
"""

import json
import subprocess
from typing import Optional, Dict, Any, List


class DeepinMailDBusClient:
    """Client for interacting with deepin-mail via D-Bus."""

    BUS_NAME = "org.deepin.mail"
    OBJECT_PATH = "/org/deepin/mail"
    INTERFACE = "org.deepin.mail"

    @staticmethod
    def _call_dbus_method(method: str, *args) -> str:
        """
        Call a D-Bus method and return the result.

        Args:
            method: Method name to call
            *args: Method arguments (will be converted to D-Bus types)

        Returns:
            Raw string result from D-Bus call
        """
        cmd = ["gdbus", "call", "--session",
               "--dest", DeepinMailDBusClient.BUS_NAME,
               "--object-path", DeepinMailDBusClient.OBJECT_PATH,
               "--method", f"{DeepinMailDBusClient.INTERFACE}.{method}"]

        # Add arguments to command
        for arg in args:
            if isinstance(arg, str):
                cmd.append(arg)
            elif isinstance(arg, int):
                cmd.append(str(arg))
            elif isinstance(arg, bool):
                cmd.append("true" if arg else "false")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout.strip()

            # gdbus returns result in format: ('<result>',)
            # e.g.: ('{"accounts":[...]}',)

            # Remove outer parentheses
            if output.startswith("(") and output.endswith(")") or output.endswith(","):
                output = output[1:-1].strip()
                # Remove trailing comma if present
                if output.endswith(","):
                    output = output[:-1].strip()

            # Remove quotes - handle both single and double quotes
            if (output.startswith("'") and output.endswith("'")) or \
               (output.startswith('"') and output.endswith('"')):
                output = output[1:-1]

            # Handle escaped quotes in the content (gdbus escapes double quotes)
            output = output.replace('\\"', '"')

            return output
        except subprocess.CalledProcessError as e:
            raise Exception(f"D-Bus call failed: {e.stderr}") from e
        except FileNotFoundError:
            raise Exception("gdbus not found. Please install glib2-tools or libglib2.0-tools") from None

    @staticmethod
    def _parse_json_response(response: str) -> Any:
        """Parse JSON response from D-Bus method."""
        if not response:
            return None
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}") from e

    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Get all email accounts.

        Returns:
            List of account dictionaries
        """
        result = self._call_dbus_method("GetAccounts")
        data = self._parse_json_response(result)
        # GetAccounts returns {"accounts": [...]}
        if isinstance(data, dict) and "accounts" in data:
            return data["accounts"]
        return data if isinstance(data, list) else []

    def get_unread(self, account: str) -> Dict[str, Any]:
        """
        Get unread count for an account.

        Args:
            account: Account identifier

        Returns:
            Dictionary with unread information
        """
        result = self._call_dbus_method("GetUnread", account)
        return self._parse_json_response(result)

    def get_mails(self, account: str, folder_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get list of emails from a folder.

        Args:
            account: Account identifier
            folder_name: Folder name (e.g., 'INBOX', 'Sent', 'Drafts')
            limit: Maximum number of emails to retrieve

        Returns:
            List of email dictionaries
        """
        result = self._call_dbus_method("GetMails", account, folder_name, limit)
        return self._parse_json_response(result)

    def get_mail_detail(self, account: str, folder_name: str, mail_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific email.

        Args:
            account: Account identifier
            folder_name: Folder name
            mail_id: Email ID

        Returns:
            Dictionary with email details
        """
        result = self._call_dbus_method("GetMailDetail", account, folder_name, mail_id)
        return self._parse_json_response(result)

    def search_mails(self, account: str, keywords: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search emails by keywords.

        Args:
            account: Account identifier
            keywords: Search keywords
            limit: Maximum number of results

        Returns:
            List of matching email dictionaries
        """
        result = self._call_dbus_method("SearchMails", account, keywords, limit)
        return self._parse_json_response(result)

    def send_mail(self, account: str, to: str, subject: str, body: str,
                  cc: str = "", attachments: str = "") -> Dict[str, Any]:
        """
        Send an email.

        Args:
            account: Account identifier to send from
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: CC recipients (optional)
            attachments: File paths as comma-separated string (optional)

        Returns:
            Dictionary with send result
        """
        result = self._call_dbus_method("SendMail", account, to, subject, body, cc, attachments)
        return self._parse_json_response(result)

    def mark_mails(self, account: str, mail_ids: str, action: str) -> Dict[str, Any]:
        """
        Mark emails with an action.

        Args:
            account: Account identifier
            mail_ids: Comma-separated mail IDs
            action: Action to perform (e.g., 'read', 'unread', 'delete', 'star', 'unstar')

        Returns:
            Dictionary with operation result
        """
        result = self._call_dbus_method("MarkMails", account, mail_ids, action)
        return self._parse_json_response(result)

    def get_default_account(self) -> Optional[str]:
        """
        Get the first/default account.

        Returns:
            Account identifier or None if no accounts exist
        """
        accounts = self.get_accounts()
        if accounts and len(accounts) > 0:
            return accounts[0].get("account") or accounts[0].get("id") or accounts[0].get("name")
        return None


def main():
    """CLI for testing D-Bus operations."""
    import argparse

    parser = argparse.ArgumentParser(description="deepin-mail D-Bus client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Accounts
    subparsers.add_parser("accounts", help="List all accounts")

    # Unread
    unread_parser = subparsers.add_parser("unread", help="Get unread count")
    unread_parser.add_argument("--account", "-a", help="Account (uses default if not specified)")

    # Get mails
    mails_parser = subparsers.add_parser("mails", help="Get emails from folder")
    mails_parser.add_argument("--account", "-a", help="Account (uses default if not specified)")
    mails_parser.add_argument("--folder", "-f", default="INBOX", help="Folder name (default: INBOX)")
    mails_parser.add_argument("--limit", "-l", type=int, default=20, help="Max emails (default: 20)")

    # Mail detail
    detail_parser = subparsers.add_parser("detail", help="Get email details")
    detail_parser.add_argument("--account", "-a", help="Account (uses default if not specified)")
    detail_parser.add_argument("--folder", "-f", default="INBOX", help="Folder name")
    detail_parser.add_argument("--id", "-i", type=int, required=True, help="Mail ID")

    # Search
    search_parser = subparsers.add_parser("search", help="Search emails")
    search_parser.add_argument("--account", "-a", help="Account (uses default if not specified)")
    search_parser.add_argument("keywords", help="Search keywords")
    search_parser.add_argument("--limit", "-l", type=int, default=20, help="Max results")

    # Send
    send_parser = subparsers.add_parser("send", help="Send email")
    send_parser.add_argument("--account", "-a", help="Account (uses default if not specified)")
    send_parser.add_argument("--to", "-t", required=True, help="Recipient")
    send_parser.add_argument("--subject", "-s", required=True, help="Subject")
    send_parser.add_argument("--body", "-b", required=True, help="Email body")
    send_parser.add_argument("--cc", "-c", default="", help="CC recipients")
    send_parser.add_argument("--attachments", default="", help="Attachments (comma-separated paths)")

    # Mark
    mark_parser = subparsers.add_parser("mark", help="Mark emails (read/unread/delete/star/unstar)",
                                        epilog="Note: --folder parameter is not needed for mark command - mail IDs are unique.",
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    mark_parser.add_argument("--account", "-a", help="Account (uses default if not specified)")
    mark_parser.add_argument("--ids", "-i", required=True, help="Mail IDs (comma-separated, e.g., 123,456)")
    mark_parser.add_argument("--action", required=True,
                            choices=["read", "unread", "delete", "star", "unstar"],
                            help="Action to perform on the emails")

    args = parser.parse_args()
    client = DeepinMailDBusClient()

    try:
        if args.command == "accounts":
            accounts = client.get_accounts()
            print(json.dumps(accounts, indent=2, ensure_ascii=False))

        elif args.command == "unread":
            account = args.account or client.get_default_account()
            if not account:
                print("No account found")
                return
            result = client.get_unread(account)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "mails":
            account = args.account or client.get_default_account()
            if not account:
                print("No account found")
                return
            mails = client.get_mails(account, args.folder, args.limit)
            print(json.dumps(mails, indent=2, ensure_ascii=False))

        elif args.command == "detail":
            account = args.account or client.get_default_account()
            if not account:
                print("No account found")
                return
            detail = client.get_mail_detail(account, args.folder, args.id)
            print(json.dumps(detail, indent=2, ensure_ascii=False))

        elif args.command == "search":
            account = args.account or client.get_default_account()
            if not account:
                print("No account found")
                return
            results = client.search_mails(account, args.keywords, args.limit)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "send":
            account = args.account or client.get_default_account()
            if not account:
                print("No account found")
                return
            result = client.send_mail(account, args.to, args.subject, args.body, args.cc, args.attachments)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "mark":
            account = args.account or client.get_default_account()
            if not account:
                print("No account found")
                return
            result = client.mark_mails(account, args.ids, args.action)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
