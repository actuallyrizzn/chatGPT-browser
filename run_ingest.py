# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
"""CLI ingest: load conversations from a JSON file (e.g. from an extracted ChatGPT export zip)."""
import argparse
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from app import app
from db import import_conversations_data, init_db


def main():
    # Change to script dir only when invoked as entry point so app can find chatgpt.db
    os.chdir(BASE_DIR)
    parser = argparse.ArgumentParser(description="Ingest ChatGPT conversations from a JSON file")
    parser.add_argument(
        "path",
        nargs="?",
        default=os.path.join(BASE_DIR, "chatgpt_export", "conversations.json"),
        help="Path to conversations.json (default: chatgpt_export/conversations.json)",
    )
    parser.add_argument("--init-db", action="store_true", help="Initialize database before ingest")
    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print(f"Error: file not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    if args.init_db:
        with app.app_context():
            init_db()
        print("Database initialized.")

    print(f"Loading {args.path}...")
    with open(args.path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        data = [data]
    print(f"Loaded {len(data)} conversations.")
    with app.app_context():
        import_conversations_data(data)
    print("Ingest complete.")


if __name__ == "__main__":
    main()
