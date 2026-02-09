# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
import argparse
import os
import sys
from app import init_db

def main():
    from app import DATABASE_PATH
    parser = argparse.ArgumentParser(description="Initialize or reset the ChatGPT Browser database.")
    parser.add_argument(
        "--force", "--reset",
        dest="force",
        action="store_true",
        help="If the database exists, delete it and create a fresh one (destroys all data).",
    )
    args = parser.parse_args()
    if os.path.exists(DATABASE_PATH) and not args.force:
        print(f"Database already exists: {DATABASE_PATH}", file=sys.stderr)
        print("Use --force to delete it and create a fresh database (all data will be lost).", file=sys.stderr)
        sys.exit(1)
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    from app import app
    with app.app_context():
        init_db()
    print("Database initialized successfully!")

if __name__ == '__main__':
    main() 