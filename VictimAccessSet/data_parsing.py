import os
import json
from sqlmanager import SQLManager
import logging


class DataParser:

    def __init__(self) -> None:
        self.db_manager = SQLManager()
        self.db_manager.create_table()
        logging.basicConfig(filename='basic.log', level=logging.INFO)

    def get_parent_domain(self, domain):
        """Extract the parent domain from a given domain."""
        parts = domain.split('.')
        # If the domain is a subdomain, we return only the domain and TLD
        if len(parts) > 2:
            return '.'.join(parts[-2:])
        else:
            return domain

    def get_unique_parent_domains(self, domains):
        """Get a set of unique parent domains."""
        parent_domains = set()
        for domain in domains:
            parent_domain = self.get_parent_domain(domain)
            parent_domains.add(parent_domain)

        parent_domains = list(parent_domains)
        total = len(parent_domains)
        parent_domains = ",".join(domain for domain in parent_domains)
        return parent_domains, total

    def parse_file_data(self, data, file):
        domain_names = data["domain_names"]
        country = data["country"]
        installed = data["installed"]
        updated = data["updated"]
        os = data["os"]
        price = data["price"]
        domain_names, total_domains = self.get_unique_parent_domains(
            domain_names)

        self.db_manager.insert_data(
            domain_names, total_domains, country, 0, installed, updated, os, price, file)
        print("file: {} inserted".format(file))

    def main(self):
        directory_path = 'genesisvictims/genesisvictims'
        files_printed = 0

        with os.scandir(directory_path) as it:
            for entry in it:
                if entry.is_file():
                    file_path = entry.path
                    with open(file_path, 'r') as file:
                        files_printed += 1
                        print("File: ", files_printed)
                        try:
                            self.parse_file_data(json.load(file), file_path)
                        except json.JSONDecodeError:
                            print(
                                f"Error: {file_path} is not a valid JSON file.")
                            logging.error(
                                f"Error: {file_path} is not a valid JSON file.")
                        except FileNotFoundError:
                            print(f"Error: File {file_path} not found.")
                            logging.error(
                                f"Error: File {file_path} not found.")
                        except PermissionError:
                            print(f"Error: Permission denied to read file {
                                  file_path}.")
                            logging.error(f"Error: Permission denied to read file {
                                file_path}.")
                        except Exception as e:
                            print(f"Error: An unexpected error occurred while processing {
                                  file_path}: {e}")
                            logging.error(f"Error: An unexpected error occurred while processing {
                                file_path}: {e}")


if __name__ == "__main__":
    DataParser().main()
