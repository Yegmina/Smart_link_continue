import sqlite3
import os

def initialize_db(db_path):
    """Creates the SQLite database and the necessary tables if they don't exist."""
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scraped_companies_PRH (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                domain TEXT UNIQUE,
                url TEXT,
                main_business_line TEXT
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scraped_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT,
            page_url TEXT,
            content TEXT
            -- No direct foreign key here; we rely on domain for linking
            );
        ''')
    conn.close()

if __name__ == '__main__':
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Create database path relative to script location
    db_path = os.path.join(script_dir, 'scraped_data.db')
    
    initialize_db(db_path)
    print(f"Database initialized at {db_path}")
