"""CLI ingest: load conversations from a JSON file (e.g. from an extracted ChatGPT export zip)."""
import argparse
import json
import os
import sys

# Run from project root so app can find chatgpt.db
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import import_conversations_data, init_db


def main():
    parser = argparse.ArgumentParser(description="Ingest ChatGPT conversations from a JSON file")
    parser.add_argument(
        "path",
        nargs="?",
        default=os.path.join("chatgpt_export", "conversations.json"),
        help="Path to conversations.json (default: chatgpt_export/conversations.json)",
    )
    parser.add_argument("--init-db", action="store_true", help="Initialize database before ingest")
    args = parser.parse_args()

    if not os.path.isfile(args.path):
        print(f"Error: file not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    if args.init_db:
        init_db()
        print("Database initialized.")

    print(f"Loading {args.path}...")
    with open(args.path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        data = [data]
    print(f"Loaded {len(data)} conversations.")
    import_conversations_data(data)
    print("Ingest complete.")


if __name__ == "__main__":
    main()
