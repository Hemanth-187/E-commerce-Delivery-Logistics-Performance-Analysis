# E-commerce Delivery & Logistics Performance Analysis

## Overview
Analyze e-commerce order and logistics data to understand order trends, shipping performance, delivery delays, and differences across shipping modes, markets, and regions.

## Objectives
- Profile the source data and document its fields.
- Audit missing values, exact duplicates, data types, and inconsistent categories.
- Build a reproducible cleaning workflow without modifying raw source files.
- Explore order volume and shipping/delivery performance.
- Produce documented charts and summary tables.

## Tools
Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter, SQL, Excel, Git, and GitHub.

## Structure
- `data/raw/`: original source data (ignored by Git)
- `data/interim/`: intermediate outputs (ignored by Git)
- `data/processed/`: analysis-ready outputs (ignored by Git)
- `notebooks/`: exploratory notebooks
- `src/`: reusable Python modules
- `sql/`: SQL scripts
- `docs/`: data dictionary and quality notes
- `reports/figures/`: exported charts

## Setup
1. Create and activate a virtual environment.
2. Run `pip install -r requirements.txt`.
3. Place approved source data in `data/raw/` locally.
4. Start Jupyter and open `notebooks/01_data_understanding.ipynb`.

## Data safety
Do not commit raw data or customer-identifiable information to a public repository. Verify licensing and sharing permissions before redistributing data. Keep original source files unchanged.
