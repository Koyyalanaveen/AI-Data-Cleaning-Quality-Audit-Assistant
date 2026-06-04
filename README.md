# AI Data Cleaning & Quality Audit Assistant

## Project Overview

The **AI Data Cleaning & Quality Audit Assistant** is a Streamlit-based data analytics application that helps users upload CSV datasets, audit data quality, detect common data issues, generate cleaning recommendations, and download a cleaned dataset.

This project solves a common real-world data analyst problem: raw datasets are often messy, incomplete, inconsistent, and not ready for analysis, reporting, or dashboard creation.

The app performs dynamic column profiling, detects business meaning from column headers, validates business rules, identifies data quality issues, generates a data quality score, and provides an executive summary for reporting.

---

## Business Problem

Data analysts often receive raw CSV or Excel files with issues such as:

- Missing values
- Duplicate records
- Invalid dates
- Negative numeric values
- Outliers
- Inconsistent category names
- Invalid ratings or scores
- Incorrect business-rule values

If these problems are not detected early, they can lead to inaccurate dashboards, wrong KPIs, poor reporting decisions, and misleading business insights.

This project helps solve that problem by providing an automated data quality audit workflow.

---

## Key Features

- Upload any CSV file
- Use a default sample messy dataset
- Preview dataset structure
- Detect column data types
- Perform dynamic column profiling
- Identify business meaning of columns
- Detect missing values
- Detect duplicate rows
- Detect negative numeric values
- Detect invalid date values
- Validate business rules dynamically
- Detect outliers using the IQR method
- Detect inconsistent category formatting
- Generate an overall data quality score
- Generate rule-based cleaning recommendations
- Provide an executive data quality summary
- Create a safely cleaned dataset
- Download cleaned CSV output
- Download audit report as a text file

---

## Tools and Technologies Used

- Python
- pandas
- Streamlit
- CSV data processing
- Data profiling
- Data quality validation
- Rule-based recommendation logic
- Business rule validation
- Dynamic schema detection

---

## Project Workflow

```text
Upload CSV Dataset
        ↓
Preview Dataset
        ↓
Dynamic Column Profiling
        ↓
Detect Business Meaning
        ↓
Run Data Quality Checks
        ↓
Validate Business Rules
        ↓
Calculate Data Quality Score
        ↓
Generate Cleaning Recommendations
        ↓
Create Cleaned Dataset
        ↓
Download Cleaned CSV and Audit Report