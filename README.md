# Delivery Delay Analytics Dashboard

## Project Overview

Delivery Delay Analytics is a Python-based data analytics project that
explores delivery performance using an interactive Streamlit dashboard.
It helps users review delivery status, compare carriers and warehouses,
examine delivery trends, and export analysis results.

> **Dataset note:** The project uses a synthetic dataset for learning
> and demonstration. Results should not be interpreted as verified
> findings from a real company.

## Features

-   Delivery status overview and key performance indicators (KPIs)
-   Carrier performance comparison
-   Warehouse performance ranking
-   Shipping-mode performance analysis
-   Delivery trend analysis
-   Distance versus delivery-delay visualization
-   Rule-based business recommendations
-   CSV download of the filtered delivery dataset
-   CSV download of business insights

## Technologies Used

-   Python
-   Pandas
-   Streamlit
-   Plotly

## Project Structure

The project currently uses a `Data` folder (capital **D**). Keep the
folder and filename capitalization consistent with the paths used in
`dashboard.py`.

``` text
Delivery_Delay_Analytics/
├── .vscode/
├── Data/
│   ├── cleaned_delivery_dataset.csv
│   └── delivery_delay_dataset.csv
├── 01_introduction.txt
├── 02_main.py
├── 02_understand_command.txt
├── 03_open_command.txt
├── dashboard.py
├── dashboard_backup.py
├── requirements.txt
└── README.md
```

The tree above reflects the files shown in the project screenshot. You
can omit `dashboard_backup.py`, `.vscode/`, or learning notes from a
public repository if they are not needed to run the project.

## Setup and Installation

1.  Install Python.

2.  Open a terminal in the project folder.

3.  Install the required libraries:

    ``` bash
    pip install -r requirements.txt
    ```

4.  Start the dashboard:

    ``` bash
    python -m streamlit run dashboard.py
    ```

5.  Open the local URL shown in the terminal.

## Requirements

The dashboard uses Streamlit, Pandas, and Plotly. The `requirements.txt`
file should list the packages imported by the project. Add any
additional third-party packages that your code requires.

## Dataset

The `Data` folder contains the CSV files used for the project. Confirm
that `dashboard.py` reads the intended file, for example:

``` python
pd.read_csv("Data/cleaned_delivery_dataset.csv")
```

Use the exact path that appears in your own code. File and folder
capitalization can matter on hosting platforms.

## How the Analysis Works

The dashboard calculates delivery delay by comparing the actual delivery
date with the promised delivery date. Delivery status is classified as:

-   **Late:** Actual delivery date is after the promised date.
-   **On Time:** Actual delivery date matches the promised date.
-   **Early:** Actual delivery date is before the promised date.

The dashboard's business recommendations are rule-based suggestions to
help identify areas for investigation; they do not establish the cause
of a delay.

## Learning Outcomes

-   Data analysis with Pandas
-   KPI calculation and aggregation
-   Interactive dashboards with Streamlit
-   Data visualization with Plotly
-   Filtered analysis and CSV export
-   Communicating findings as business insights

## Future Improvements

-   Add automated tests for data processing and filtering
-   Improve error handling for missing or invalid data
-   Add more detailed route-level analysis
-   Deploy the dashboard online
-   Add screenshots of the dashboard to this README

## Author

Name = Kishan lal Kumawat 
Email I'd = wwwkishu112@gmail.com
Mobile Number = 7073919377

