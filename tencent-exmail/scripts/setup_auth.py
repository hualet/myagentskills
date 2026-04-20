#!/usr/bin/env python3
"""Check and manage qqmail-cli authentication configuration."""

import os
import sys

CONFIG_DIR = os.path.expanduser("~/.config/qqmail-cli")
ENV_FILE = os.path.join(CONFIG_DIR, ".env")


def check_auth():
    """Check if authentication is configured. Returns dict with status."""
    if not os.path.isfile(ENV_FILE):
        return {"configured": False, "path": ENV_FILE}

    config = {}
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()

    required = {"IMAP_HOST", "IMAP_PORT", "IMAP_USER", "IMAP_PASSWORD"}
    missing = required - set(config.keys())
    if missing:
        return {"configured": False, "path": ENV_FILE, "missing": sorted(missing)}

    return {
        "configured": True,
        "path": ENV_FILE,
        "user": config.get("IMAP_USER", ""),
        "host": config.get("IMAP_HOST", ""),
    }


def write_config(email: str, password: str):
    """Write the .env configuration file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(ENV_FILE, "w") as f:
        f.write(f"IMAP_HOST=imap.exmail.qq.com\n")
        f.write(f"IMAP_PORT=993\n")
        f.write(f"IMAP_USER={email}\n")
        f.write(f"IMAP_PASSWORD={password}\n")
    os.chmod(ENV_FILE, 0o600)
    return {"configured": True, "path": ENV_FILE, "user": email}


if __name__ == "__main__":
    import json

    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "check":
            print(json.dumps(check_auth(), indent=2))
        elif action == "write" and len(sys.argv) == 4:
            print(json.dumps(write_config(sys.argv[2], sys.argv[3]), indent=2))
        else:
            print(f"Usage: {sys.argv[0]} check | write <email> <password>", file=sys.stderr)
            sys.exit(1)
    else:
        print(json.dumps(check_auth(), indent=2))
