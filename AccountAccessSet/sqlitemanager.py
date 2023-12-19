import sqlite3
import logging


class SqliteManager:

    def __init__(self) -> None:
        database_path = 'compromised_assets.db'
        self.conn = sqlite3.connect(database_path)
        logging.basicConfig(filename='db_logger.log', level=logging.INFO)

    def get_conn(self):
        return self.conn

    def fetch_gpt_info_personal(self):
        """
        This query returns information that has been filtered by GPT.
        """
        query = """
        SELECT *
        FROM new_data
        WHERE title LIKE '%SSN%'
           OR title LIKE '%DL%'
           OR title LIKE '%drivers%'
           OR title LIKE '%DOB%'
           OR title LIKE '%Full Info%'
           OR title LIKE '%passport%'
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def fetch_bank_info_gpt(self):
        """
        This query returns information for titles containing banking-related terms.
        """
        query = """
        SELECT *
        FROM new_data
        WHERE title LIKE '%bank%'
           OR title LIKE '%cheque%'
           OR title LIKE '%credit%'
           OR title LIKE '%debit%'
           OR title LIKE '%card%'
           OR title LIKE '%cash%'
           OR title LIKE '%tax%'
           OR title LIKE '%payment%'
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def fetch_emails_gpt(self):
        """
        This query returns information for titles containing banking-related terms.
        """
        query = """
        SELECT *
        FROM new_data
        WHERE (title LIKE '%email%'
            OR title LIKE '%password%'
            OR title LIKE '%username%'
            OR title LIKE '%@%'
            OR title LIKE '%.com%'
            OR title LIKE '%phone%'
            OR title LIKE '%online%'
            OR title LIKE '%social%')
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def insert_into_new_data(self, title, price, location, file):
        # Connect to SQLite database
        cursor = self.conn.cursor()

        if title is None and price is None and location is None:
            logging.warn(
                f"Error Inserting database: No available data: file {file}")
            return

        try:
            sql = '''INSERT INTO new_data(title, price, location, compromised_domain, file)
                VALUES(?,?,?,?,?) '''
            cursor.execute(sql, (title, price, location, None, file))
            self.conn.commit()
        except Exception as e:
            print(f"Error Inserting database: {e}: file {file}")
            logging.error(f"Error Inserting database: {e}: file {file}")

    def stats(self):
        personal = self.fetch_gpt_info_personal()
        money = self.fetch_bank_info_gpt()
        online_acc = self.fetch_emails_gpt()

        query = """
        SELECT *
        FROM new_data
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        return {
            "Personal": len(personal),
            "Financial": len(money),
            "OnlineAcc": len(online_acc),
            "Total": len(results),
        }


if __name__ == "__main__":
    manager = SqliteManager()
    print(manager.stats())
