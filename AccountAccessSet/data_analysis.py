import re
from sqlitemanager import SqliteManager
from visualizer import DataVisualizer
import sys
import traceback


class AccountVisualizerManager:
    """
    A class dedicated to managing and visualizing various aspects of account-related data. 

    The class interfaces with a SQLite database to fetch data and then applies data filtering \
        and visualization techniques. \
    It deals with different types of data including personal information, financial data,\
        and email/digital asset information. The class offers functionalities like filtering \
            based on price and currency, location, and generating various types of analysis \
                and visualizations such as statistical data, top categories analysis, \
                    and price variation visualizations.

    Methods:
        analysis_sob: Fetches and processes personal information data.
        analysis_finance: Fetches and processes financial data.
        analysis_access_cred: Fetches and processes email/digital asset data.
        analysis_stat: Generates statistical analysis of the data.
        analysis_top_cate: Provides analysis on top categories based on different data sets.
        filtering_price_and_currency: Filters and cleans price and currency data.
        filtering_locations: Filters and normalizes location data.
    """

    def __init__(self) -> None:
        self.manager = SqliteManager()
        self.batch_1 = []

    def filtering_price_and_currency(self, other_data: list = None):
        """
        filtering price and currency.

        """
        skip = 0
        data = list()
        if other_data is None:
            other_data = self.batch_1

        for row in other_data:
            try:
                price = row[3]
                # filtering all the special character from price except , and .
                cleaned_price = re.sub(r'[^a-zA-Z0-9,\.]', '', price)
                pattern = r'(\d+(?:\.\d+)?)\s*([A-Za-z]+)'

                if "," in price:
                    # multiple price
                    price = cleaned_price.split(",")  # now price is a list

                if isinstance(price, str):
                    if price == "Unknown":
                        data.append({
                            "title": row[1],
                            "location": row[2],
                            "price": "Unknown",
                            "currency": None,
                        })
                    else:
                        try:
                            price, currency = re.search(
                                pattern, price).groups()
                        except Exception:
                            print(price, " Exception occurred")
                            break
                        if price is None:
                            price = "Unknown"
                        data.append({
                            "title": row[1],
                            "location": row[2],
                            "price": price,
                            "currency": currency,
                        })
                elif isinstance(price, list):
                    multiple_price = []
                    currency = None
                    for data_inside_price_list in price:
                        price_item, currency = re.search(
                            pattern, data_inside_price_list).groups()
                        if price_item is None:
                            price_item = "Unknown"
                        multiple_price.append(price_item)

                    data.append({
                        "title": row[1],
                        "location": row[2],
                        "price": multiple_price,
                        "currency": currency,
                    })
            except Exception:
                print(row)
                print("Exception Occurred")
                return []

        print("Skipped : ", skip, " Total : ", len(
            self.batch_1), " Final: ", len(data))
        return data

    def filtering_locations(self, data: list):
        """
        filtering out location that are not either in alpha_2 or Unknown. 
        """
        for index in range(0, len(data)):
            try:
                row = data[index]
            except Exception:
                print(index, len(data))
                return
            location = row["location"]

            if "," in location:
                location = location.split(",")

            if isinstance(location, str):
                if location != "Unknown" and len(location) > 2:
                    location = "Unknown"
                data[index]["location"] = location

            if isinstance(location, list):
                new_location_list = set()
                for item in location:
                    if item != "Unknown" and len(item) > 2:
                        item = "Unknown"
                    new_location_list.add(item)
                data[index]["location"] = list(new_location_list)
        return data

    def analysis_sob(self):
        # this data are correctly filtered
        # remaining info.
        self.batch_1 = self.manager.fetch_gpt_info_personal()

    def analysis_finance(self):
        self.batch_1 = self.manager.fetch_bank_info_gpt()

    def analysis_access_cred(self):
        self.batch_1 = self.manager.fetch_emails_gpt()

    def analysis_stat(self):
        return self.manager.stats()

    def analysis_top_cate(self):
        # Fetch the data
        personal_info = self.manager.fetch_gpt_info_personal()
        bank_info = self.manager.fetch_bank_info_gpt()
        email_info = self.manager.fetch_emails_gpt()

        return personal_info, bank_info, email_info


if __name__ == "__main__":
    try:
        info = AccountVisualizerManager()
        title_text = ""
        print("-*&" * 15)
        choice = input(
            " * Select 1 to view data set where Personal Identitification Information (SSN, Drivers License, Passport) is sold,\
            \n * Select 2 for Financial Information (Bank Account, Credit/Debit Card, Cheque etc) are sold, \
            \n * Select 3 for Email/Digital Assets like Email Address, Account for a specific website is Sold\
            \n * Select 4 to view Top 10 countries from each categories above\
            \n * Select 5 to view overall statistics>> ")
        print("-*&" * 15)
        if choice == "1":
            title_text = "Distribution of PII-related Entries by Location"
            info.analysis_sob()
        elif choice == "2":
            title_text = "Financial Term Frequency"
            info.analysis_finance()
        elif choice == "3":
            title_text = "Credential and Email Identifier Occurrences"
            info.analysis_access_cred()
        elif choice == "4":
            personal_info, bank_info, email_info = info.analysis_top_cate()

            personal_info = info.filtering_price_and_currency(personal_info)
            personal_info = info.filtering_locations(personal_info)

            bank_info = info.filtering_price_and_currency(bank_info)
            bank_info = info.filtering_locations(bank_info)

            email_info = info.filtering_price_and_currency(email_info)
            email_info = info.filtering_locations(email_info)

            data_analysis = DataVisualizer([])
            data_analysis.plot_top_10_in_categories(
                personal_info, bank_info, email_info)
        elif choice == "5":
            data_analysis = DataVisualizer([])
            data_analysis.pie_stat(info.analysis_stat())
        else:
            print("Wrong choice!")
            sys.exit(-1)

        if choice in ["1", "2", "3"]:
            print("-*&" * 15)
            currency_choice = input(
                "To view data in USD type 1,\
                \nTo view data sold in BTC select 2 >> ")
            print("-*&" * 15)
            if currency_choice == "1":
                currency = "USD"
            elif currency_choice == "2":
                currency = "BTC"
            else:
                print("Wrong choice!")
                sys.exit(-1)

            data = info.filtering_price_and_currency()
            data = info.filtering_locations(data)
            data_analysis = DataVisualizer(data)

            print("-*&" * 15)
            graph_choice = input(
                "Graph Choice: To view Price by location and Currency type 1,\
                \nGraph Choice: To view price by location, Currency and Country Type 2 >> ")
            print("-*&" * 15)
            if graph_choice == "1":
                unknown_choice = input(
                    "To add Unknown Location in the data point, Type 1,\
                    \nTo remove unknown from data point, Type anything else >> ")
                print("-*&" * 15)
                is_unknown_location_allowed = True if unknown_choice == "1" else False
                data_analysis.histogram_price_by_location(
                    currency=currency,
                    is_unknown_location_allowed=is_unknown_location_allowed,
                    additional_title=title_text)
            elif graph_choice == "2":
                country_choice = input(
                    "To view for a specific country, type the alpha-2 country name >> ")
                print("-*&" * 15)
                if country_choice is None or len(country_choice) == 0:
                    country_choice = "US"
                data_analysis.price_variation_by_location(
                    currency=currency,
                    country=country_choice,
                    additional_title=title_text)
            else:
                print("Wrong choice!")
                sys.exit(-1)
    except Exception as e:
        print(e)
        traceback.print_exc()
