import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pycountry


class DataVisualizer:
    def __init__(self, data):
        self.data = data

    def _average_price(self, price):
        if isinstance(price, list):
            prices = [float(p) for p in price]
            return sum(prices) / len(prices)
        return float(price)

    def _country_full_name(self, code):
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else code

    def process_data_to_get_top(self, info_list):
        country_counts = {}
        for info in info_list:
            countries = info['location'] if isinstance(
                info['location'], list) else [info['location']]
            for country in countries:
                if country != 'Unknown':
                    country_counts[country] = country_counts.get(
                        country, 0) + 1
        top_countries = sorted(country_counts.items(),
                               key=lambda item: item[1], reverse=True)[:10]
        return pd.DataFrame(top_countries, columns=['Country', 'Count'])

    def histogram_price_by_location(self, currency=None,
                                    is_unknown_location_allowed=False,
                                    additional_title=None):
        # Filter data based on currency and non-Unknown values
        df = pd.DataFrame(self.data)
        original_data_count = len(df)

        if currency is not None:
            filtered_data = df[df['currency'] == currency]
        else:
            filtered_data = df

        if is_unknown_location_allowed:
            filtered_data = filtered_data[(
                filtered_data['price'] != 'Unknown')]
        else:
            filtered_data = filtered_data[(filtered_data['price'] != 'Unknown') & (
                filtered_data['location'] != 'Unknown')]
        filtered_data_count = len(filtered_data)

        expanded_data = filtered_data.explode('location')
        expanded_data['price'] = expanded_data['price'].apply(
            self._average_price)

        grouped_data = expanded_data.groupby(
            'location')['price'].mean().reset_index()
        grouped_data = grouped_data.sort_values(
            by='price', ascending=False).head(20)
        grouped_data['full_name'] = grouped_data['location'].apply(
            self._country_full_name)

        # Plotting
        plt.figure(figsize=(12, 8))
        palette = sns.color_palette("pastel", len(grouped_data))
        barplot = sns.barplot(x='location', y='price',
                              data=grouped_data, palette=palette)

        # Set the titles for the graph
        if currency is not None:
            title = f'Average Price by Location in {currency} (Data Points: {
                original_data_count}, Filtered: {filtered_data_count})'
        else:
            title = f'Average Price by Location (Data Points: {
                original_data_count}, Filtered: {filtered_data_count})'

        if additional_title is not None:
            plt.suptitle(additional_title, fontsize=14, fontweight='bold')
            plt.title(title, fontsize=10)
        else:
            plt.title(title, fontsize=12)

        # Creating custom legend
        handles = [plt.Rectangle((0, 0), 1, 1, color=palette[i])
                   for i in range(len(grouped_data))]
        legend_labels = [f"{code} - {name}" for code,
                         name in zip(grouped_data['location'], grouped_data['full_name'])]
        plt.legend(handles, legend_labels, title="Country Codes",
                   loc='center left', bbox_to_anchor=(1, 0.5))

        plt.xlabel('Location')
        if currency is not None:
            plt.ylabel(f'Average Price ({currency})')
        else:
            plt.ylabel('Average Price')
        plt.xticks(rotation=90)
        # Adjust the right space to prevent overlap with the legend
        plt.subplots_adjust(right=0.8)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def price_variation_by_location(self, currency,
                                    country,
                                    additional_title=None):
        df = pd.DataFrame(self.data)

        # Filter out entries without the specified currency or with 'Unknown' values
        df = df[(df['currency'] == currency) & (df['price'] != 'Unknown')]

        original_data_count = len(df)

        df['price'] = df['price'].apply(self._average_price)

        df = df.explode('location')

        country_data = df[df['location'] == country]

        filtered_data_count = len(country_data)

        palette = sns.color_palette("Spectral", filtered_data_count)

        plt.figure(figsize=(14, 8))
        sns.lineplot(data=country_data, x=country_data.index,
                     y='price', palette=palette)

        if additional_title:
            plt.suptitle(additional_title, fontsize=16, fontweight='bold')

        title = f'Price Points by Location in {
            currency} - {self._country_full_name(country)}'
        subtitle = f'(Data Points: {original_data_count}, Used: {
            filtered_data_count})'
        plt.title(f'{title}\n{subtitle}', fontsize=14)

        plt.xlabel('Data Point')
        plt.ylabel(f'Price ({currency})')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def pie_stat(self, data_dict: dict):
        total_data_points = 33896

        unparsed_data_points = total_data_points - data_dict['Total']

        if unparsed_data_points > 0:
            data_dict['Unparsed'] = unparsed_data_points

        del data_dict['Total']

        labels = data_dict.keys()
        sizes = data_dict.values()

        colors = sns.color_palette('YlOrBr', len(labels))

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors,
                autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title('Distribution of Categories', pad=20, fontsize=16)
        plt.show()

    def plot_top_10_in_categories(self, personal_info: list, bank_info: list, email_info: list):
        top_personal = self.process_data_to_get_top(personal_info)
        top_bank = self.process_data_to_get_top(bank_info)
        top_email = self.process_data_to_get_top(email_info)

        unique_countries = set(top_personal.head(10)['Country']) | set(
            top_bank.head(10)['Country']) | set(top_email.head(10)['Country'])

        palette = sns.color_palette("bright", len(unique_countries))
        country_color_map = {country: palette[i]
                             for i, country in enumerate(unique_countries)}

        def assign_colors(df):
            return [country_color_map[country] for country in df['Country']]

        fig, axes = plt.subplots(1, 3, figsize=(21, 7), sharey=True)

        sns.barplot(ax=axes[0], x='Count', y='Country',
                    data=top_personal, palette=assign_colors(top_personal))
        sns.barplot(ax=axes[1], x='Count', y='Country',
                    data=top_bank, palette=assign_colors(top_bank))
        sns.barplot(ax=axes[2], x='Count', y='Country',
                    data=top_email, palette=assign_colors(top_email))

        axes[0].set_title('Top 10 Personal Information')
        axes[1].set_title('Top 10 Financial Information')
        axes[2].set_title('Top 10 Online Account Information')

        plt.suptitle('Top 10 Popular Countries in Each Category',
                     fontsize=16, fontweight='bold')

        legend_handles = [plt.Rectangle(
            (0, 0), 1, 1, color=country_color_map[country]) for country in unique_countries]
        legend_labels = [f"{country}, {self._country_full_name(
            country)}" for country in unique_countries]

        plt.legend(legend_handles, legend_labels, title="Countries",
                   loc='center left', bbox_to_anchor=(1, 0.5))

        plt.tight_layout(rect=[0, 0.03, 0.9, 0.95])
        plt.show()
