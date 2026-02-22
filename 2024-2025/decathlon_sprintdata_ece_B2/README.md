# Decathlon Sprint Data (ECE B2)

Python + SQL workflow to collect Decathlon product pages, clean records, and load data into MySQL.

## What is in this folder

- `data_collect.py` : Selenium scraper for Decathlon listing + product detail pages.
- `decathlon_produits_details.csv` : scraped dataset output.
- `database_init.py` : cleans fields and inserts into MySQL tables.
- `sprintdata_decathlon.sql` : SQL dump/schema.
- `jupyter_database_init.ipynb` : notebook version of processing.

## Requirements

- Python 3.x
- `pandas`
- `mysql-connector-python`
- `selenium`
- Edge WebDriver configured in `data_collect.py`
- Local MySQL/MariaDB server

## Quick Start

1. Update DB credentials in `database_init.py` (`host`, `user`, `password`, `database`).
2. Update Edge driver path in `data_collect.py` (`Service("C:\WebDrivers\msedgedriver.exe")`).
3. Run scraper:
   - `python data_collect.py`
4. Load CSV into DB:
   - `python database_init.py`

## Notes

- Script logic assumes Decathlon page selectors from the time the project was written.
- Website structure changes may break scraping selectors.
