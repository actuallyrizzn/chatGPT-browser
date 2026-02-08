# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
from app import init_db
import os

def main():
    # Remove existing database if it exists
    if os.path.exists('chatgpt.db'):
        os.remove('chatgpt.db')
    
    # Initialize fresh database
    init_db()
    print("Database initialized successfully!")

if __name__ == '__main__':
    main() 