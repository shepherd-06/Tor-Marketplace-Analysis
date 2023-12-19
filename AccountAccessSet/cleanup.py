import sqlite3
import json
import os
from gpt_cleaner import analyze_text_with_openai
import logging
import re
from time import sleep
import traceback

logging.basicConfig(filename='datacleanup.log', level=logging.INFO)


class DataCleaup:

    def __init__(self) -> None:
        database_path = 'compromised_assets.db'
        self.conn = sqlite3.connect(database_path)

    def update_row(self, title, location, price, domain, file):
        # Connect to SQLite database
        cursor = self.conn.cursor()

        try:
            # SQL query to create the table if it does not exist
            sql_create_data_table = """ 
                CREATE TABLE IF NOT EXISTS new_data (
                    id integer PRIMARY KEY,
                    title text NOT NULL,
                    location text,
                    price text,
                    compromised_domain text,
                    file text
                ); """
            cursor.execute(sql_create_data_table)

            # SQL query to insert or update the row
            # Assuming 'file' is a unique identifier for each row
            sql = '''INSERT INTO new_data(title, price, location, compromised_domain, file)
                VALUES(?,?,?,?,?) '''
            cursor.execute(sql, (title, price, location, domain, file))
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error updating database: {e}: file {file}")
            print(f"Error updating database: {e}: file {file}")

    def parse_json_file(self, file_path):
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return

            # Open and read the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)
                # Print the text field from the JSON data
                # remove all URls
                url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                result = re.sub(url_pattern, '', data.get("text", ""))

                pattern = r'[^a-zA-Z0-9]'  # remove all special characters
                result = re.sub(pattern, '', data.get("text"))

                # remove all dates
                date_patterns = [
                    # Matches dd/mm/yyyy, mm/dd/yyyy, dd-mm-yyyy, etc.
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                    # Matches yyyy-mm-dd, yyyy/mm/dd, etc.
                    r'\b\d{2,4}[/-]\d{1,2}[/-]\d{1,2}\b',
                ]
                for pattern in date_patterns:
                    result = re.sub(pattern, '', result)

                return result

        except Exception as e:
            print(f"Error parsing JSON file {file_path}: {e}")
            logging.error(f"Error parsing JSON file {file_path}: {e}")

    def fetch_files_with_multiple_locations(self, conn):
        cursor = self.conn.cursor()
        try:
            # Query to select records with more than one location
            query = "SELECT id, file FROM data WHERE location LIKE '%,%'"

            # Executing the query
            cursor.execute(query)
            rows = cursor.fetchall()
            print("total rows: {}".format(len(rows)))
            # Print the file field for each row
            for row in rows:
                row_id, file_path = row
                print("current row: ", row_id, file_path)
                file_text = self.parse_json_file(file_path)
                analyzed_json = analyze_text_with_openai(file_text, file_path)
                # analyzed_json = None
                print(analyzed_json)
                # Check for null values and update the database or log
                if analyzed_json is not None:
                    title = analyzed_json.get('product')
                    if title is None:
                        title = analyzed_json.get('product_name')
                    location = analyzed_json.get('location')
                    price = analyzed_json.get('price')
                    domain = analyzed_json.get('domain')

                    if isinstance(location, list):
                        new_location = ""
                        for item in location:
                            new_location += "-" + item
                        location = new_location

                    print(
                        "update: {} - [{}: {}: {}]".format(file_path, title, location, price))
                    logging.info(
                        "update: {} - [{}: {}: {}]".format(file_path, title, location, price))
                    if title is not None and location is not None:
                        self.update_row(conn, title,
                                        location, price, domain, file_path)
                else:
                    logging.info(f"Null value found for row {
                        row_id}: {file_path}: {analyzed_json}")
                sleep(3)

        except Exception as e:
            print(f"An error occurred: {e}")

    def fix_product_description(self):
        cursor = self.conn.cursor()
        query = """
        SELECT *
        FROM data
        WHERE title = 'Product Information'
        """

        cursor.execute(query)
        results = cursor.fetchall()
        print("total: ", len(results))
        index = 1
        for row in results:
            row_id, file_path = row[0], row[7]
            print("current index: ", index, file_path)
            file_text = self.parse_json_file(file_path)
            analyzed_json = analyze_text_with_openai(file_text, file_path)
            # Check for null values and update the database or log
            if analyzed_json is not None:
                title = analyzed_json.get('product')
                if title is None:
                    title = analyzed_json.get('product_name')
                location = analyzed_json.get('location')
                price = analyzed_json.get('price')
                domain = analyzed_json.get('domain')

                if isinstance(location, list):
                    new_location = ""
                    for item in location:
                        new_location += "-" + item
                    location = new_location

                if title is not None and location is not None:
                    print(
                    "update: {} - [{}: {}: {}]".format(file_path, title, location, price))
                    self.update_row(title,
                                    location, price, domain, file_path)
            else:
                logging.error(f"Null value found for row {
                    row_id}: {file_path}: {analyzed_json}")
            sleep(3)
            index += 1
        cursor.close()


if __name__ == "__main__":
    try:
        cleanup = DataCleaup()
        cleanup.fix_product_description()
    except Exception as e:
        print(e)
        traceback.print_exc()
