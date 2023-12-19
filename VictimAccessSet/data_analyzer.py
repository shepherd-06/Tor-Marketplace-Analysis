from sqlmanager import SQLManager
from collections import Counter
from data_viewer import DomainDataProcessor


class DataAnalyzerFinal:

    """
    Question Answered
    1. Find the top N domain (default = 20)
    2. Find out the domain -> which countries they were comrpomised the most, how many times.
    3. Find out the price range for each of the top domains (overall).
    4. Find out the price range between different countries for top domnain.
    5. Find out OS distribution by countries
    """

    def __init__(self):
        self.sqlmanager = SQLManager('data.db')

    def get_top_domains(self, top_n=20):
        """Get the top N most common domains."""
        rows = self.sqlmanager.fetch_domains()
        all_domains = []
        index = 1
        for row in rows:
            try:
                index += 1
                if row is not None:
                    domains = row.split(',')
                    all_domains.extend(domains)
            except IndexError:
                print(index, print(row), type(row))
        domain_count = Counter(all_domains)
        return domain_count.most_common(top_n)

    def get_compromised_countries_counter(self, top_domains: list):
        """
        figure out which countries they were comrpomised the most, how many times.
        """
        data = []
        for domain in top_domains:
            domain_name = domain[0]
            counter = domain[1]
            rows = self.sqlmanager.find_rows_with_specific_domain(domain_name)
            list_of_countries = set()  # unique countries
            list_of_price = []  # inside str

            country_by_price = dict()  # inside dict
            os_counter = dict()  # how many times an OS appeared for a domain
            country_counter = dict()

            for row in rows:
                country = row[3]
                price = row[8]
                os = row[7]

                list_of_price.append(price)
                list_of_countries.add(country)
                if country in country_by_price:
                    country_by_price[country].append(price)
                else:
                    country_by_price[country] = [price,]

                if os in os_counter:
                    os_counter[os] += 1
                else:
                    os_counter[os] = 1

                if country in country_counter:
                    country_counter[country] += 1
                else:
                    country_counter[country] = 1

            data.append({
                "domain": domain_name,
                "counter": counter,
                "list_of_price": list_of_price,
                "list_of_countries": list_of_countries,
                "country_by_price": country_by_price,
                "country_counter": country_counter,
                "os_counter": os_counter,
            })

        return data

    def get_top_20_os(self):
        all_os = self.sqlmanager.fetch_all_os()
        top_20_os = dict()
        for os in all_os:
            if os == "":
                os = "Unknown OS"
            if os in top_20_os:
                top_20_os[os] += 1
            else:
                top_20_os[os] = 1

        top_20_os = dict(
            sorted(top_20_os.items(), key=lambda item: item[1], reverse=True)[:20])
        return top_20_os

    def categorize_os(self):
        all_os = self.sqlmanager.fetch_all_os()
        categorized_os = {'Windows': 0, 'Linux': 0,
                          'MacOS': 0, 'Unrecognized': 0}

        for os_name in all_os:
            if os_name == "":
                categorized_os['Unrecognized'] += 1
            elif 'windows' in os_name.lower():
                categorized_os['Windows'] += 1
            elif 'linux' in os_name.lower() or 'ubuntu' in os_name.lower():
                categorized_os['Linux'] += 1
            elif 'mac' in os_name.lower() or 'os x' in os_name.lower():
                categorized_os['MacOS'] += 1
            else:
                categorized_os['Unrecognized'] += 1

        return categorized_os

    def categorize_windows_versions(self):
        all_os = self.sqlmanager.fetch_all_os()
        windows_versions = {}

        # Filter and categorize Windows versions
        for os_name in all_os:
            if 'windows' in os_name.lower():
                if 'windows 10' in os_name.lower():
                    version = 'Windows 10'
                elif 'windows 11' in os_name.lower():
                    version = 'Windows 11'
                elif 'windows 8' in os_name.lower() or 'windows 8.1' in os_name.lower():
                    version = 'Windows 8/8.1'
                elif 'windows server' in os_name.lower():
                    version = 'Windows Server'
                elif 'windows 7' in os_name.lower():
                    version = 'Windows 7'
                elif 'windows vista' in os_name.lower():
                    version = 'Windows Vista'
                # Add more categorizations as needed
                else:
                    version = 'Other Windows'

                windows_versions[version] = windows_versions.get(
                    version, 0) + 1

        # Calculate the total count of Windows OS entries
        total_windows = sum(windows_versions.values())

        # Exclude versions with less than 5% concentration
        windows_versions = {version: count for version, count in windows_versions.items(
        ) if (count / total_windows) >= 0.05}

        return windows_versions

    def main(self):
        """
        main function
        """
        choice = input("Choices are from 1 to 8. Choose wisely: ")
        dataanalyzer = DataAnalyzerFinal()
        choice = int(choice)

        if 1 <= choice <= 5:
            top_domains = dataanalyzer.get_top_domains()
            print("--------------------------------")
            for item in top_domains:
                print("Domains", item[0])
            print("--------------------------------")
            data = self.get_compromised_countries_counter(top_domains)
            data_processor = DomainDataProcessor(data)

            if choice == 1:
                # 1. Find the top N domain (default = 20)
                data_processor.plot_domain_frequency()  # top N domain
            elif choice == 2:
                # 2. Find out the domain -> which countries they were comrpomised the most, how many times.
                data_processor.plot_domain_compromises_by_country(
                    "epicgames.com")
            elif choice == 3:
                # 3. Find out the price range for each of the top domains (overall). max, min, avg
                data_processor.plot_price_range_all_domains()
            elif choice == 4:
                # 4. Find out the price for a specific domain in top 10 countries
                data_processor.plot_price_range_by_domain(
                    domain_name="paypal.com")  # works perfectly
            else:
                # 5. Compromised domains vs top 10 OS
                data_processor.plot_os_distribution("google.com")
        else:
            data_processor = DomainDataProcessor()
            if choice == 6:
                top_20_os = dataanalyzer.get_top_20_os()
                # 6. Most popular OS irregardless of domains/countries to be compromised
                data_processor.plot_top_20_os(top_20_os)
            elif choice == 7:
                categorized_os = dataanalyzer.categorize_os()
                # 7. Most popular OS systems (Broad spectrum. Windows, Linux, MacOS)
                data_processor.plot_os_pie_chart(categorized_os)
            elif choice == 8:
                windows_versions = dataanalyzer.categorize_windows_versions()
                # 8. Different Windows Systems (Broad Scales 8, 10, Server, 11 etc) and their percentage in the data
                data_processor.plot_windows_distribution(windows_versions)


if __name__ == "__main__":
    DataAnalyzerFinal().main()
