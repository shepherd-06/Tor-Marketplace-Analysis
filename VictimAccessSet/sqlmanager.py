import sqlite3
import logging


class SQLManager:
    def __init__(self, db_file='data.db'):
        """Initialize the database connection."""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        logging.basicConfig(filename='db_logger.log', level=logging.INFO)

    def create_table(self):
        """Create a table if it doesn't already exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY,
                domains TEXT,
                total_domains INTEGER,
                country TEXT,
                cookies INTEGER,
                installed TEXT,
                updated TEXT,
                os TEXT,
                price REAL,
                filename TEXT
            )
        ''')
        self.conn.commit()

    def insert_data(self, domains, total_domains, country, cookies, installed, updated, os, price, filename):
        """Insert data into the table."""
        self.cursor.execute('''
            INSERT INTO data (domains, total_domains, country, cookies, installed, updated, os, price, filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (domains, total_domains, country, cookies, installed, updated, os, price, filename))
        self.conn.commit()

    def fetch_domains(self):
        """Fetch all domains from the table."""
        self.cursor.execute('SELECT domains FROM data')
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def find_rows_with_specific_domain(self, domain):
        """Find rows where the specified domain appears within the domains text."""
        query = "SELECT * FROM data WHERE domains LIKE ?"
        self.cursor.execute(query, ('%' + domain + '%',))
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def fetch_all_os(self):
        """
        fetch all OS from the database
        """
        self.cursor.execute("SELECT os FROM data")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]


if __name__ == "__main__":
    # Usage example
    db_manager = SQLManager('my_database.db')
    db_manager.create_table()
    # Example data insertion
    db_manager.insert_data('example.com,example2.com', 2, 'IT', 100,
                           '2020-07-06', '2020-07-06', 'Windows 10 Home', 10.00,
                           'file1.json')
    # Remember to close the connection when done
    db_manager.close()
