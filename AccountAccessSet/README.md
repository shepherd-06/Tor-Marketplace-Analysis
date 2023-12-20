# Project README: Account Access Data Analysis and Visualization

## Overview
This project encompasses the analysis and visualization of the "AccountAccessSet" dataset, a collection of data obtained from the Database Market within the Tor network. This marketplace is known for trading online accounts (like PayPal, Spotify) and private datasets (driver's license photos, tax forms), primarily using Bitcoin as the currency. Our dataset was built by crawling this marketplace between November 2021 and June 2022, resulting in a substantial collection of 33,896 victim files, totaling approximately 400 MB.

## Dataset Details
- **Source**: Database Market on the Tor network.
- **Content**: Online account credentials, private datasets.
- **Time Frame**: November 2021 - June 2022.
- **Volume**: 33,896 files, approximately 400 MB.

## Modules
The project is divided into four main modules, each handling a specific aspect of the data processing pipeline:

### 1. Parsing Module
- **Purpose**: Extracts and structures raw data from the dataset.
- **Key Classes**:
  - `TestAnalyzer`: Retrieves and parses JSON files, applying regex to extract structured data.

### 2. Cleanup Modules
- **Purpose**: Standardize and clean the extracted data.
- **Key Classes**:
  - `LocationCleanup`: Normalizes and corrects location data using pycountry and OpenAI for complex cases.
  - `PriceCleanup`: Adjusts and standardizes price data, utilizing OpenAI for handling varied formats.

### 3. Analysis and Visualization Module
- **Purpose**: Analyze and visually represent the cleaned data.
- **Key Classes**:
  - `AccountVisualizerManager`: Interfaces with a SQLite database to fetch, filter, and visualize data. It can analyze personal information, financial data, email/digital asset information, and more.
  - `DataVisualizer`: A tool for creating various types of visualizations like histograms, pie charts, and plots specific to the dataset's nature.

## Usage
- Run the respective module as per the need (Parsing, Cleanup, Analyze+Visualize).
- Choose the specific function within the module based on the type of data to be processed or visualized.
- Visualization results provide insights into the distribution, frequency, and trends within the dataset.

## Ethical Consideration
This project processes sensitive data obtained from a dark web marketplace. Ethical considerations and legal compliance are paramount. Data is handled responsibly, with a focus on research and educational purposes only.

## Conclusion
This project provides a comprehensive toolkit for parsing, cleaning, and visualizing complex datasets obtained from unconventional sources. It demonstrates the power of data analysis in understanding trends and patterns in digital marketplaces operating within the Tor network.

---

_**Note**: This project is part of an academic research initiative and is not intended for commercial use. All analysis is carried out within the bounds of ethical research practices._