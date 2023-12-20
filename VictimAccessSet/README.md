# Project README: Victim Access Data Analysis and Visualization

## Overview
This project focuses on analyzing and visualizing the "VictimAccessSet" dataset, a comprehensive collection of data derived from the Genesis Market within the realm of Infostealer malware networks. The Genesis Market is renowned for its user-friendly platform and a steady supply of compromised data, facilitating unauthorized access to victims' online accounts. This project aims to dissect the intricacies of this marketplace, focusing on the dynamics of compromised device pricing and the method of access to victims' browser sessions.

## Dataset Details
- **Source**: Genesis Market, a platform in the domain of Infostealer malware.
- **Content**: Compromised data including passwords, usernames, and browser session details.
- **Time Frame**: April 2019 - May 2022.
- **Volume**: 0.5 million victim files, totaling approximately 3.5 GB.

## Modules and Their Functionalities
The project is structured into distinct modules, each catering to a specific aspect of data handling and analysis:

### 1. Data Parsing Module
- **Purpose**: Extracts and organizes raw data from the dataset.
- **Key Class**: `DataParser` - Manages file parsing, extracts parent domains, and handles database interactions.

### 2. Data Analysis Module
- **Purpose**: Performs in-depth analysis of the structured data.
- **Key Class**: `DataAnalyzerFinal` - Analyzes domain frequency, compromised countries, price ranges, and operating system distributions.

### 3. Data Visualization Module
- **Purpose**: Visualizes the analyzed data in an easily interpretable format.
- **Key Class**: `DomainDataProcessor` - Generates various plots and charts to represent data insights, like domain frequencies, price distributions, OS distributions, and more.

## Key Features
- **Domain Analysis**: Identifies and ranks the most commonly compromised domains.
- **Geographical Insights**: Determines the countries most affected by compromises for each domain.
- **Price Analysis**: Evaluates the pricing structure of compromised accounts, both overall and within specific countries.
- **Operating System Distribution**: Explores the distribution of compromised systems across different operating systems and versions.
- **Visualization**: Provides graphical representations of data for intuitive understanding and easy communication of findings.

## Ethical Consideration
This project involves sensitive data related to compromised online accounts. The handling of such data is governed by strict ethical guidelines, ensuring that the project's scope is confined to research and educational purposes only. No personal data is used beyond the realm of analysis, and all findings are presented in an anonymized format.

## Usage Guidelines
- Choose the appropriate module based on the specific analysis or visualization need.
- Run the main function of the chosen module and follow the prompts to navigate through the various functionalities.
- For visualization, ensure the necessary libraries (like matplotlib, seaborn) are installed.

## Conclusion
Through meticulous data parsing, in-depth analysis, and comprehensive visualization, this project sheds light on the operations of malware networks like Genesis Market. It offers valuable insights into how compromised data is traded, priced, and utilized, enhancing our understanding of modern cyber threats.

---

_**Note**: This project is part of an academic research initiative and is not intended for commercial use. All analysis is carried out within the bounds of ethical research practices._