import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import numpy as np


class DomainDataProcessor:
    def __init__(self, data: List[Dict] = None):
        """
        Initialize the processor with a list of domain data.
        """
        self.data = data

    def _convert_price_str_to_float(self, price_list: List[str]) -> List[float]:
        """
        Convert price list from string to float. Handles empty strings and non-numeric values.
        """
        return [float(price) for price in price_list if self._is_float(price)]

    def _is_float(self, value: str) -> bool:
        """
        Check if a string can be converted to float.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def domain_frequency(self) -> pd.DataFrame:
        """
        Calculate the frequency of each domain.
        """
        domain_counts = [item['counter'] for item in self.data]
        domain_names = [item['domain'] for item in self.data]
        return pd.DataFrame({'Domain': domain_names, 'Frequency': domain_counts})

    def aggregate_prices(self, split: int = 0) -> pd.DataFrame:
        """
        Aggregate price information by domain and country, calculating the median price.
        """
        rows = []
        if split == 0:
            splitted_data = self.data
        else:
            splitted_data = self.data[0:split]

        for item in splitted_data:
            domain = item['domain']
            for country, prices in item['country_by_price'].items():
                prices = self._convert_price_str_to_float(prices)
                if prices:  # Only include if there are valid prices
                    median_price = np.median(prices)  # Calculate median price
                    rows.append(
                        {'Domain': domain, 'Country': country, 'MedianPrice': median_price})

        return pd.DataFrame(rows)

    def os_distribution(self) -> pd.DataFrame:
        """
        Analyze the distribution of operating systems by country for each domain.
        """
        rows = []
        for item in self.data:
            domain = item['domain']
            for country, os_list in item['country_by_os'].items():
                for os_name in os_list:
                    rows.append(
                        {'Domain': domain, 'Country': country, 'OS': os_name})
        return pd.DataFrame(rows)

    def compromised_countries_counter(self) -> pd.DataFrame:
        """
        Determine which countries have the domains compromised the most and how many times.
        """
        country_compromises = {}
        for item in self.data:
            for country in item['list_of_countries']:
                if country:  # Ensure country is not an empty string
                    country_compromises[country] = country_compromises.get(
                        country, 0) + 1

        # Convert the dictionary to a list of tuples and sort by the number of compromises
        sorted_compromises = sorted(
            country_compromises.items(), key=lambda x: x[1], reverse=True)

        # Taking the top 10 countries with the most compromises
        top_countries_compromises = sorted_compromises[:20]

        # Convert to DataFrame
        df_top_countries = pd.DataFrame(top_countries_compromises, columns=[
                                        'Country', 'Compromises'])

        return df_top_countries

    def plot_domain_frequency(self):
        """
        Plot the frequency of each domain as a bar chart with different colors for each bar.
        """
        df = self.domain_frequency()
        plt.figure(figsize=(12, 6))
        # Generate a color palette with a distinct color for each bar
        palette = sns.color_palette("hsv", len(df))
        sns.barplot(x='Domain', y='Frequency', data=df, palette=palette)
        plt.title('Frequency of Domains')
        plt.xlabel('Domain')
        plt.ylabel('Frequency')
        plt.xticks(rotation=90, ha='center')
        plt.subplots_adjust(bottom=0.3)
        plt.tight_layout()
        plt.show()

    def plot_os_distribution(self, domain_name: str):
        """
        Plot the distribution of operating systems for a specific domain as a bar graph,
        limited to the top 10 operating systems.
        """
        # Filter data for the specific domain
        domain_data = next(
            (item for item in self.data if item['domain'] == domain_name), None)

        # Prepare the data for the bar graph
        if domain_data and 'os_counter' in domain_data:
            os_counter = domain_data['os_counter']

            # Convert the dictionary to a DataFrame and get the top 10 OS
            df_os = pd.DataFrame(list(os_counter.items()),
                                 columns=['OS', 'Count'])
            df_top_os = df_os.sort_values(by='Count', ascending=False).head(10)

            plt.figure(figsize=(12, 6))
            palette = sns.color_palette("hsv", len(df_top_os))
            sns.barplot(x='OS', y='Count', data=df_top_os, palette=palette)
            plt.title(f'OS Distribution for {domain_name} (Top 10 OS)')
            plt.xlabel('Operating System')
            plt.ylabel('Frequency')
            plt.xticks(rotation=45, ha='center')
            plt.subplots_adjust(bottom=0.2)
            plt.tight_layout()
            plt.show()
        else:
            print(f"No data found for domain {domain_name}")

    def plot_price_range_all_domains(self):
        """
        Plot a graph showing the max, min, and median prices for each domain.
        """
        # Convert 'list_of_price' to floats for all items
        for item in self.data:
            item['list_of_price'] = self._convert_price_str_to_float(
                item['list_of_price'])

        # Prepare a DataFrame with min, max, and median prices for each domain
        price_stats = []
        for item in self.data:
            prices = item['list_of_price']
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                median_price = np.median(prices)  # Calculate median
                price_stats.append(
                    {
                        'Domain': item['domain'],
                        'MinPrice': min_price,
                        'MaxPrice': max_price,
                        'MedianPrice': median_price
                    })

        df_stats = pd.DataFrame(price_stats)

        # Plotting
        plt.figure(figsize=(12, 8))
        for _, row in df_stats.iterrows():
            plt.errorbar(x=row['Domain'], y=row['MedianPrice'],
                         yerr=[[row['MedianPrice'] - row['MinPrice']],
                               [row['MaxPrice'] - row['MedianPrice']]],
                         fmt='o', capsize=5)
            plt.text(row['Domain'], row['MedianPrice'], f"{row['MedianPrice']:.2f}",
                     ha='center', va='bottom')

        plt.title('Price Range for Each Domain')
        plt.xlabel('Domain')
        plt.ylabel('Price')
        plt.xticks(rotation=30, ha='center')
        plt.subplots_adjust(bottom=0.5)
        plt.tight_layout()
        plt.legend()
        plt.show()

    def plot_price_range_by_domain(self, domain_name: str):
        """
        Plot the median price as a line curve for a specific domain across the top countries.
        """
        df = self.aggregate_prices()
        # Filter the dataframe for the specified domain
        df = df[df['Domain'] == domain_name]

        # Get the median price for each country and reset index for easier iteration
        country_prices = df.groupby(
            'Country')['MedianPrice'].median().reset_index()

        # Sort and select the top countries based on the median price
        top_countries = country_prices.sort_values(
            by='MedianPrice', ascending=False).head(10)

        # Adjust the size of our plot to be better suited for the number of countries
        plt.figure(figsize=(len(top_countries) * 1.5, 6))

        # Generate a color palette with a distinct color for each country
        num_countries = len(top_countries)
        palette = sns.color_palette("hsv", num_countries)

        # Plotting the line curve
        sns.lineplot(x='Country', y='MedianPrice', data=top_countries,
                     sort=False, marker='o', linewidth=2.5, color='skyblue')

        # Scatter plot for each point with a different color
        for i, (index, row) in enumerate(top_countries.iterrows()):
            plt.scatter(row['Country'], row['MedianPrice'],
                        color=palette[i % num_countries], s=100, zorder=3)
            plt.text(row['Country'], row['MedianPrice'] + (row['MedianPrice'] * 0.02), f"{row['MedianPrice']:.2f}",
                     horizontalalignment='center', size='medium', color='black', weight='semibold', zorder=4)

        plt.title(f'Median Price in Top Countries for {domain_name}')
        plt.xlabel('Country')
        plt.ylabel('Median Price')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_compromised_countries_counter(self):
        """
        Plot a colorful bar chart showing the top 10 countries where domains were compromised the most.
        """
        df_top_countries = self.compromised_countries_counter()
        plt.figure(figsize=(12, 6))
        palette = sns.color_palette("Spectral", len(df_top_countries))
        sns.barplot(x='Country', y='Compromises',
                    data=df_top_countries, palette=palette)
        plt.title('Top 10 Countries by Domain Compromises')
        plt.xlabel('Country')
        plt.ylabel('Number of Compromises')
        plt.xticks(rotation=45)
        plt.show()

    def plot_domain_compromises_by_country(self, domain_name: str):
        """
        Plot a colorful bar graph showing the number of times a specific domain was compromised in each country,
        limited to the top 10 countries with the most compromises.
        """
        # Filter data for the specific domain
        domain_data = next(
            (item for item in self.data if item['domain'] == domain_name), None)

        # Prepare the data for the bar graph
        if domain_data and 'country_counter' in domain_data:
            country_compromises = domain_data['country_counter']

            # Convert the dictionary to a DataFrame
            df_compromises = pd.DataFrame(list(country_compromises.items()), columns=[
                                          'Country', 'Compromises'])

            # Sort the DataFrame by 'Compromises' and select the top 10 countries
            df_top_countries = df_compromises.sort_values(
                by='Compromises', ascending=False).head(10)

            plt.figure(figsize=(10, 6))
            palette = sns.color_palette("hsv", len(df_top_countries))
            sns.barplot(x='Country', y='Compromises',
                        data=df_top_countries, palette=palette)
            plt.title(f'Compromises in Top 10 Countries for {domain_name}')
            plt.xlabel('Country')
            plt.ylabel('Number of Compromises')
            plt.xticks(rotation=45)
            plt.show()
        else:
            print(f"No data found for domain {domain_name}")

    def plot_top_20_os(self, top_20_os):
        # Convert the dictionary to a DataFrame for easier plotting
        df_top_20_os = pd.DataFrame(
            list(top_20_os.items()), columns=['OS', 'Count'])

        plt.figure(figsize=(14, 8))
        sns.barplot(x='Count', y='OS', data=df_top_20_os, palette='viridis')
        plt.title('Top 20 Most Popular Operating Systems')
        plt.xlabel('Frequency')
        plt.ylabel('Operating System')
        plt.subplots_adjust(bottom=0.2)
        plt.tight_layout()
        plt.show()

    def plot_os_pie_chart(self, categorized_os):
        # Create a pie chart
        # Create a pie chart
        labels = categorized_os.keys()
        sizes = categorized_os.values()
        # Use bright and vibrant colors
        # colors = ['#BF0603', '#DAF0EE', '#456990', '#2b59c3']
        colors = sns.color_palette("bright", len(categorized_os))

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=None, colors=colors, autopct='', startangle=140)

        # Adding a legend and placing it to the right of the pie chart
        plt.legend(labels=[f'{label} - {s/sum(sizes)*100:.2f}%' for label, s in zip(labels, sizes)],
                   title="Operating Systems",
                   loc="center left",
                   bbox_to_anchor=(1, 0, 0.5, 1))

        # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.axis('equal')
        plt.title('OS Distribution')
        # Adjust the right margin to make space for the legend
        plt.subplots_adjust(left=0.1, right=0.7)
        plt.show()

    def plot_windows_distribution(self, windows_versions):
        # Create a pie chart
        labels = windows_versions.keys()
        sizes = windows_versions.values()
        # Use bright and vibrant colors
        colors = sns.color_palette("bright", len(windows_versions))

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, colors=colors,
                autopct='%1.1f%%', startangle=140)

        # Adding a legend and placing it to the right of the pie chart
        plt.legend(title="Windows Versions",
                   loc="center left",
                   bbox_to_anchor=(1, 0, 0.5, 1))

        plt.axis('equal')
        plt.title('Windows OS Distribution', loc='center', y=1.08)
        # Adjust the right margin to make space for the legend
        plt.subplots_adjust(left=0.1, right=0.7)
        plt.show()
