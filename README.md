!\[Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)



\# Sickle Cell Public Health Data Tool



A Python application for the analysis of public health data related to

\*\*sickle cell disease\*\*, that utilises estimates from the \*\*Global Burden of Disease (GBD)\*\*

study published by the Institute for Health Metrics and Evaluation (IHME).



This was developed for an academic programming assignment and

demonstrates data loading, persistence, analysis, visualisation, and testing.



---



\## Dataset



The project uses the \*\*IHME Global Burden of Disease – Sickle Cell Disorders Estimates\*\*

dataset.



\- Source: IHME / GBD data portal  

\- Format: CSV  

\- Content includes:

&nbsp; - Incidence, prevalence, and mortality estimates

&nbsp; - Multiple years (e.g. 2000–2021)

&nbsp; - Locations (countries/regions)

&nbsp; - Sex and age group breakdowns



\*\*The dataset is not included in this repository\*\* due to size constraints.



\### How to access the dataset

1\. Download \*\*“ Sickle cell disorders estimates (CSV)”\*\* from the IHME GHDx portal.

2\. Place the file at:data/raw/





---



\## Features



\- Streaming CSV loader (handles large files efficiently)

\- SQLite database for persistent storage

\- Query and filter by:

\- Location

\- Year

\- Measure (e.g. prevalence, mortality)

\- Metric (rate / number)

\- Sex and age group

\- Summary statistics (min, mean, max)

\- Time-series trend analysis

\- Location comparison for a given year

\- Matplotlib visualisations (line charts and bar charts)

\- Text-based interactive CLI

\- Unit tests with measured code coverage



---



\## Project Structure



sickle-cell-public-health-tool/

│

├── data/

│ ├── raw/ # Dataset location (CSV not committed)

│ └── README.md # Dataset instructions

│

├── database/ # SQLite database (generated at runtime)

│

├── src/

│ ├── loader.py # CSV loading and validation

│ ├── db.py # SQLite database layer

│ ├── analysis.py # Data analysis and queries

│ ├── visualise.py # Matplotlib visualisations

│ └── cli.py # Command-line interface

│

├── tests/ # Unit tests

├── main.py # Application entry point

├── requirements.txt

└── README.md





---



\## Installation



Ensure Python 3.10+ is installed.



Install dependencies:



```bash

pip install -r requirements.txt



Running the Application



From the project root:



python main.py



First-time setup



Choose Option 1 to load the dataset into the SQLite database.



Subsequent runs can skip loading unless the database is deleted.



Running Tests



Unit tests are implemented using Python’s built-in unittest framework.



Current overall test coverage: 97%

