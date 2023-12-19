import os
import json
import sqlite3
from sqlite3 import Error
import re
import pycountry

# Database setup
def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def get_title_from_text(text_str):
    ''' Get the title text '''
    if not '######' in text_str:
        return ''
    for line in text_str.split('\n'):
        if not '######' in line:
            continue
        title = line.replace('#', '').strip()
        if ' Main ' in title:
            continue
        if title:
            return title
    return ''

def prices_from_text(text_str):
    ''' All USD prices from the text_str to a sorted integer list '''
    number_list = []
    text_str = text_str.replace('Tutorials and Guides', '').replace('Wallets Botnet logs', '')
    text_lower = text_str.lower()
    if 'guide' in text_lower or 'botnet' in text_lower:
        return number_list
    if not '$**' in text_str:
        return number_list
    # Search prices
    regex = r'\s\*\*\d+\$\*\*\s'
    for line in text_str.split('\n'):
        line = line.lower()
        if not '**' in line or not '$' in line:
            continue
        if 'mix' in line: # Skip mixed data packages
            continue
        # Skip 0 pcs or more than 1 pcs
        skip_this = False
        for pcs in ['0', '2', '3', '4', '5', '6', '7', '8', '9']:
            for word in ['pcs', 'piece']:
                if pcs + word in line or pcs + ' ' + word in line:
                    skip_this = True
                    break
        if skip_this:
            continue
        for number in re.findall(regex, line):
            number = float(number.replace('*', '').replace('$', '').strip())
            if 0 < number < 1000000: # More than zero and less than million
                print('Example line %d: %s' % (len(number_list) + 1, line.strip()))
                number_list.append(number)
    number_list.sort()
    return number_list

def location_from_text(text_str):
    # Create a set of all country names for searching
    countries = {country.name for country in pycountry.countries}

    # Prepare the text for searching
    text_str = text_str.lower()

    # Find and return countries mentioned in the text
    found_countries = set()
    for country in countries:
        if country.lower() in text_str:
            found_countries.add(country)

    return list(found_countries)

def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

# Define the database and table creation SQL
database = "compromised_assets.db"
sql_create_data_table = """ CREATE TABLE IF NOT EXISTS data (
                                        id integer PRIMARY KEY,
                                        title text NOT NULL,
                                        location text,
                                        price text,
                                        found_date text,
                                        compromised_domain text,
                                        timestamp text,
                                        file text
                                    ); """

def find_date_in_text(text_str):
    # Search for dates in the specified formats
    regex = r'\b\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?\b'
    match = re.search(regex, text_str)
    return match.group() if match else ''


def find_compromised_domain(text_str):
    # Regular expression to find domain-like patterns
    # Excludes common image extensions, .onion domains, numeric-only domains, and specific patterns
    regex = r'\b([a-zA-Z][\w-]*\.[\w.-]+)\b'
    excluded_extensions = r'\.(jpg|jpeg|png|gif|bmp|svg|onion|oni|All|date|sc)$'
    excluded_pattern = r'database[\w-]*\.(o|onion|o[\w.-]+)$'

    matches = re.finditer(regex, text_str, re.IGNORECASE | re.DOTALL)
    found_domains = set()

    for match in matches:
        domain = match.group(1)
        # Exclude domains that match the excluded patterns
        if not re.search(excluded_extensions, domain, re.IGNORECASE) and \
           not re.search(excluded_pattern, domain, re.IGNORECASE):
            found_domains.add(domain)

    return found_domains


def process_file(file_path, conn):
    with open(file_path, 'r') as file:
        data = json.load(file)

        text = data.get('text', '')
        timestamp = data.get('timestamp', '')

        # Extract information using helper functions
        title = get_title_from_text(text)
        prices = prices_from_text(text)
        locations = location_from_text(text)
        location_str = ', '.join(locations) if locations else ''
        found_date = find_date_in_text(text)
        compromised_domain = find_compromised_domain(text)
        compromised_domain_str = ", ".join(compromised_domain)

        # Aggregate prices if they differ
        unique_prices = sorted(set(prices))
        price_str = ', '.join(map(str, unique_prices)) if unique_prices else ''

        # Create a single entry per file
        data_tuple = (title, price_str, location_str, found_date, compromised_domain_str, timestamp, file.name)
        insert_data(conn, data_tuple)

# Rest of your script...


def insert_data(conn, data):
    sql = ''' INSERT INTO data(title, price, location, found_date, compromised_domain, timestamp, file)
              VALUES(?,?,?,?,?,?, ?) '''  # Update this line to include five placeholders
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()


# Main
def main(start_file=19):
    conn = create_connection(database)
    end_file=5884277
    # end_file = 100

    # Create table
    if conn is not None:
        create_table(conn, sql_create_data_table)
    else:
        print("Error! Cannot create the database connection.")

    for file_number in range(start_file, end_file + 1):
        file_path = f'database/{file_number}.json'
        if os.path.exists(file_path):        
            print("Current file: ", file_path)
            try:
                process_file(file_path, conn)
                if file_number % 1000 == 0:
                    print(f"Processed up to file number: {file_number}")
            except Exception as e:
                print(f"Error occurred at file number: {file_number}")
                print(e)
                break

if __name__ == '__main__':
    main()  # Add start_file argument if resuming from a specific file
