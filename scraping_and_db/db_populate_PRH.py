import sqlite3
import csv
import os

def populate_db_from_csv(db_path, csv_path):
    """Reads CSV rows and inserts them into scraped_companies if not present."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    conn = sqlite3.connect(db_path)
    with conn:
        cursor = conn.cursor()
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['website.url'].strip()
                if not url.startswith('http'):
                    url = 'http://' + url

                domain = url.split("//")[-1].split("/")[0].replace('www.', '')

                # Insert ignoring duplicates (domain is UNIQUE in the table)
                cursor.execute('''
                    INSERT OR IGNORE INTO scraped_companies_PRH 
                    (company_name, domain, url, main_business_line)
                    VALUES (?, ?, ?, ?)
                ''', (
                    row['name'],
                    domain,
                    url,
                    row['mainBusinessLine.descriptions']
                ))
    conn.close()

if __name__ == '__main__':
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create absolute paths relative to script location
    db_path = os.path.join(script_dir, 'scraped_data.db')
    csv_path = os.path.join(script_dir, 'processed_data_from_prh.fi', 'relevant_companies_broadly.csv')
    
    populate_db_from_csv(db_path, csv_path)
    print(f"Database populated from {csv_path}")
