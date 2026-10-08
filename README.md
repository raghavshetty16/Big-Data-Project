# Big-Data-Project — Suzlon Modern Data Engineering Pipeline

PROJECT OVERVIEW
This project implements an end-to-end modern data engineering pipeline using synthetic Suzlon Energy operational data. The workflow covers synthetic data generation, data validation, Bronze/Silver/Gold processing in Databricks, Spark SQL analytics, KPI creation, and machine-learning-ready feature engineering.

IMPORTANT NOTE
All datasets used in this repository are synthetic and are created for academic/project purposes. They do not represent actual confidential Suzlon Energy operational, customer, financial, or asset data.

ARCHITECTURE
Synthetic Data Generation
        |
        v
Raw CSV Dataset
        |
        v
Bronze Layer
        |
        v
Silver Layer
        |
        v
Gold Layer
        |
        +------> Business Analytics
        |
        +------> Feature Engineering

DATA GENERATION
Python, NumPy, and Pandas are used to generate reproducible synthetic datasets representing a wind-energy business.

MAIN DIMENSION TABLES
- dim_customer
- dim_date
- dim_model
- dim_site
- dim_technician
- dim_turbine

MAIN FACT TABLES
- fact_order
- fact_contract
- fact_generation
- fact_service

DATA ENGINEERING PIPELINE
1. Bronze Layer
   - Raw data ingestion
   - Initial table creation
   - Data preservation
   - Delta-based storage

2. Silver Layer
   - Schema enforcement
   - Data-type conversion
   - Data cleaning
   - Data-quality validation
   - Business-rule validation

3. Gold Layer
   - Business-oriented analytical tables
   - Monthly generation analysis
   - Site-level KPIs
   - Customer and commercial analytics
   - Operational performance metrics

ANALYTICS
The project demonstrates:
- GROUP BY aggregations
- ROLLUP
- GROUPING SETS
- RANK()
- LAG()
- Moving averages
- Month-over-month analysis
- Monthly KPI aggregation
- Site and turbine performance analysis

FEATURE ENGINEERING
A turbine-level feature table is created for a potential predictive-maintenance use case.

Example features include:
- Average availability percentage
- Total downtime over the previous 90 days
- Service ticket count over the previous 90 days
- Average energy generation over the previous 90 days

No predictive model is trained as part of the current implementation.

TECHNOLOGY STACK
- Python
- NumPy
- Pandas
- Apache Spark
- PySpark
- Spark SQL
- Databricks
- Delta Lake
- Databricks Feature Store
- Jupyter Notebooks

REPOSITORY STRUCTURE
Big-Data-Project/
|
+-- Data-generation_Python_scripts/
|   +-- config.py
|   +-- generate_dataset.py
|   +-- validate_dataset.py
|   +-- requirements.txt
|
+-- DATABRICS_NOTEBOOK/
|   +-- 01_Bronze_to_Silver.ipynb
|   +-- 02_Silver_to_Gold.ipynb
|   +-- 03_Feature_Store.ipynb
|
+-- RAW_DATASET/
|   +-- Dimension and fact CSV datasets
|
+-- docs/
|   +-- Data-generation strategy
|   +-- Project report
|   +-- Project documentation
|
+-- README.md

EXECUTION
1. Navigate to the data-generation directory.
2. Install the required Python packages.
3. Run generate_dataset.py.
4. Run validate_dataset.py.
5. Upload the generated datasets to a Databricks-accessible location.
6. Execute the Databricks notebooks in the following order:

   01_Bronze_to_Silver.ipynb
   02_Silver_to_Gold.ipynb
   03_Feature_Store.ipynb

DATA QUALITY
The project includes checks for:
- Empty datasets
- Primary-key validity
- Foreign-key relationships
- Valid availability ranges
- Non-negative energy generation
- Non-negative downtime
- Valid renewal indicators
- Expected data grain

PROJECT OUTCOMES
The project demonstrates an end-to-end data engineering workflow involving:
- Synthetic data generation
- Dimensional data modelling
- Data ingestion
- Lakehouse architecture
- Data cleaning
- Data validation
- Spark transformations
- Advanced SQL aggregations
- Window analytics
- KPI generation
- Feature engineering

AUTHOR
Raghav Shetty
GitHub: https://github.com/raghavshetty16
Repository: https://github.com/raghavshetty16/Big-Data-Project
