# AI Data Cleaning & Quality Audit Assistant

A Streamlit-based data quality audit application that helps users upload CSV files, detect common data issues, generate cleaning recommendations, calculate a data quality score, and download a cleaned dataset with an audit report.

---

## Project Summary

Raw datasets are often incomplete, inconsistent, duplicated, or not ready for analysis. This project solves that problem by providing an automated data quality audit workflow for CSV datasets.

The app helps users quickly identify:

* Missing values
* Duplicate records
* Invalid dates
* Negative numeric values
* Outliers
* Inconsistent category formatting
* Basic business-rule issues
* Overall data quality score

This project demonstrates practical skills in **Python, pandas, Streamlit, data cleaning, data validation, data profiling, and business reporting**.

---

## Business Problem

Data analysts often receive messy raw datasets before creating dashboards, reports, or business insights.

If data quality issues are not detected early, they can lead to:

* Incorrect KPIs
* Wrong dashboard results
* Misleading business decisions
* Poor reporting accuracy
* Extra manual cleaning time

This project provides a simple automated assistant to audit, summarize, and clean datasets before analysis.

---



## Key Features

| Feature                   | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| CSV Upload                | Allows users to upload any CSV file                                       |
| Sample Dataset            | Provides a default messy dataset for testing                              |
| Data Preview              | Displays uploaded dataset structure                                       |
| Data Profiling            | Identifies column names, data types, missing values, and basic statistics |
| Missing Value Detection   | Finds columns and rows with missing values                                |
| Duplicate Detection       | Detects duplicate records                                                 |
| Negative Value Check      | Flags negative values in numeric columns                                  |
| Date Validation           | Identifies invalid or inconsistent date values                            |
| Outlier Detection         | Uses the IQR method to detect possible outliers                           |
| Category Formatting Check | Finds inconsistent text/category formatting                               |
| Data Quality Score        | Calculates an overall quality score                                       |
| Cleaning Recommendations  | Generates rule-based suggestions for improving data quality               |
| Cleaned Dataset Download  | Allows users to download the cleaned CSV file                             |
| Audit Report Download     | Generates a downloadable text report                                      |

---

## Tools and Technologies Used

* Python
* pandas
* Streamlit
* CSV data processing
* Data profiling
* Data validation
* Rule-based recommendation logic
* Business rule checks

---

## Project Workflow

```text
Upload CSV Dataset
        ↓
Preview Dataset
        ↓
Profile Columns and Data Types
        ↓
Run Data Quality Checks
        ↓
Detect Missing Values, Duplicates, Outliers, and Invalid Values
        ↓
Generate Data Quality Score
        ↓
Show Cleaning Recommendations
        ↓
Create Cleaned Dataset
        ↓
Download Cleaned CSV and Audit Report
```

---

## How to Run This Project

### 1. Clone the repository

```bash
git clone https://github.com/Koyyalanaveen/AI-Data-Cleaning-Quality-Audit-Assistant.git
```

### 2. Open the project folder

```bash
cd AI-Data-Cleaning-Quality-Audit-Assistant
```

### 3. Install required libraries

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit app

```bash
streamlit run app.py
```

---

## Folder Structure

```text
AI-Data-Cleaning-Quality-Audit-Assistant/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── raw/
│
├── dashboard/
│   └── screenshots/
│
├── reports/
│
└── testing done/
```

---

## Sample Outputs

The app generates:

* Dataset preview
* Column-level profiling
* Missing value summary
* Duplicate record summary
* Outlier detection summary
* Data quality score
* Cleaning recommendations
* Cleaned CSV file
* Audit report text file

---

## Skills Demonstrated

* Python programming
* pandas data cleaning
* Streamlit app development
* Data profiling
* Data validation
* Data quality auditing
* Rule-based automation
* CSV file handling
* Business reporting
* User-friendly analytics tool development

---

## Recruiter Review Guide

Recruiters or reviewers can check this project in the following order:

1. Open `README.md` to understand the project objective and workflow.
2. Review `app.py` to see the Streamlit application logic.
3. Check `requirements.txt` for required Python libraries.
4. View the screenshots folder to understand the app interface.
5. Run the app using `streamlit run app.py`.
6. Upload a sample CSV file and review the generated audit results.

---

## Future Improvements

* Add Excel file upload support
* Add advanced duplicate detection
* Add downloadable PDF audit report
* Add data visualization charts
* Add automatic column type correction
* Add machine learning-based anomaly detection
* Deploy the app online using Streamlit Cloud

---

## Conclusion

This project shows how Python and Streamlit can be used to automate a common data analyst task: checking and improving raw dataset quality before analysis or dashboard development.

It is useful for data cleaning, reporting preparation, and improving data reliability before business decision-making.
