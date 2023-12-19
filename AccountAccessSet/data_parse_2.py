import re
import os
import json
import sqlite3
from time import sleep
from sqlitemanager import SqliteManager


class TestAnalyzer:

    def __init__(self) -> None:
        self.manager = SqliteManager()
        self.conn = self.manager.get_conn()

    def fetch_related_information(self):
        query = """
        SELECT *
        FROM new_data
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        excluded_filenames = [row[5] for row in results]

        placeholders = ', '.join(
            '?' for filename in excluded_filenames)
        query = f"""
        SELECT file
        FROM data
        WHERE (title LIKE '%Product Information%')
           AND file NOT IN ({placeholders})
        """
        cursor = self.conn.cursor()
        cursor.execute(query, excluded_filenames)
        results = cursor.fetchall()
        cursor.close()
        return results

    def parse_json_file(self, file_path):
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return

            # Open and read the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data.get("text", None)
        except Exception as e:
            print("Exception occurred: ", file_path, " ", e)

    def regex(self, text):
        if text is None:
            return None, None, None

        product_info_pattern = r"(?<=###### Product Information\n\n)(.*?)(?=\n\n##### Fields)"
        # Price pattern remains the same
        price_pattern = r"(?<=__ Price: \*\*)(.*?)(?=\*\*)"
        # Location pattern now includes city and state
        location_pattern = r"City : (.+?)\n\nState : (.+?)\n\n"
        # Final Pattern
        specific_pattern = r"!\(.*?\)\n\n"

        # Extracting data using regex
        product_info = re.findall(product_info_pattern, text, re.DOTALL)
        product_info = re.sub(specific_pattern, '',
                              product_info[0], flags=re.DOTALL).strip()

        # Removing URLs from the product information
        price = re.findall(price_pattern, text)
        location = re.findall(location_pattern, text)

        price = price[0] if len(price) > 0 else None
        if not location:
            location = None
        else:
            location = list(
                set([f"{city}, {state}" for city, state in location]))
            location = ', '.join(location)
        return product_info, price, location

    def main(self):
        related_files = self.fetch_related_information()
        print("Total files: ", len(related_files))
        index = 1
        for file in related_files:
            file = file[0]
            filetext = self.parse_json_file(file)
            data = self.regex(filetext)
            print("Index: ", index, data, file)
            self.manager.insert_into_new_data(data[0], data[1], data[2], file)
            index += 1


if __name__ == "__main__":
    TestAnalyzer().main()
