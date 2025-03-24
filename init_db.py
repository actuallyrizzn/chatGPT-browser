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