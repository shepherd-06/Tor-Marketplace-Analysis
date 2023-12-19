import os
import json


def get_parent_domain(domain):
    """Extract the parent domain from a given domain."""
    parts = domain.split('.')
    # If the domain is a subdomain, we return only the domain and TLD
    if len(parts) > 2:
        return '.'.join(parts[-2:])
    else:
        return domain


def get_unique_parent_domains(domains):
    """Get a set of unique parent domains."""
    parent_domains = set()
    for domain in domains:
        parent_domain = get_parent_domain(domain)
        parent_domains.add(parent_domain)

    parent_domains = list(parent_domains)
    total = len(parent_domains)
    parent_domains = ",".join(domain for domain in parent_domains)
    return parent_domains, total


def print_contents_of_first_n_files(directory, num_files=1):
    """Prints the contents of the first 'num_files' files in the specified directory using a generator."""
    files_printed = 0

    with os.scandir(directory) as it:
        for entry in it:
            if entry.is_file():
                file_path = entry.path
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    for item in data:
                        print(item, data[item] if item != "text" else None)
                    unique_parent_domains, total = get_unique_parent_domains(
                        data["domain_names"])
                    print(unique_parent_domains, total)
                    # print(f"Filename: {entry.name}\nContent:\n{
                    #       content}\n\n{'-'*40}\n")
                    files_printed += 1
                    if files_printed >= num_files:
                        break


# Replace the directory path with the actual path
# Replace with your actual directory path
directory_path = 'genesisvictims/genesisvictims'
print_contents_of_first_n_files(directory_path)
