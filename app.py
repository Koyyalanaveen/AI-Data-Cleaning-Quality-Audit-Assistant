import streamlit as st
import pandas as pd
import warnings

st.set_page_config(
    page_title="AI Data Cleaning & Quality Audit Assistant",
    layout="wide"
)

st.title("AI Data Cleaning & Quality Audit Assistant")

st.write(
    "Upload a CSV file or use the default sample dataset to audit data quality, "
    "detect common issues, generate cleaning recommendations, and download cleaned data."
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_to_datetime(series):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pd.to_datetime(series, errors="coerce")


def detect_column_type(df, column):
    unique_values = df[column].nunique(dropna=True)
    total_rows = len(df)

    date_keywords = [
        "date", "time", "created", "updated", "purchase",
        "transaction", "invoice", "ordered", "timestamp"
    ]

    column_name_lower = column.lower()

    if pd.api.types.is_numeric_dtype(df[column]):
        return "Numeric"

    converted_dates = safe_to_datetime(df[column])
    date_success_rate = converted_dates.notnull().mean()

    if any(keyword in column_name_lower for keyword in date_keywords) and date_success_rate >= 0.50:
        return "Date-like"

    if date_success_rate >= 0.80 and unique_values > 20:
        return "Date-like"

    if unique_values <= 20:
        return "Categorical"

    if unique_values >= total_rows * 0.80:
        return "Identifier / High Unique"

    return "Text / Object"


def detect_business_meaning(column_name, detected_type):
    col = column_name.lower().replace(" ", "_")

    if "id" in col or "code" in col or "number" in col:
        return "Identifier"

    if detected_type == "Date-like":
        return "Date / Time"

    if any(word in col for word in ["price", "amount", "revenue", "sales", "cost", "value"]):
        return "Price / Amount"

    if any(word in col for word in ["quantity", "qty", "units", "volume"]):
        return "Quantity"

    if any(word in col for word in ["discount", "offer", "rebate"]):
        return "Discount"

    if any(word in col for word in ["rating", "score", "review", "satisfaction", "feedback"]):
        return "Rating / Score"

    if any(word in col for word in ["status", "payment", "txn_status", "transaction_status"]):
        return "Status"

    if any(word in col for word in ["region", "zone", "location", "city", "state", "country"]):
        return "Location / Region"

    if any(word in col for word in ["category", "product", "type", "department", "segment"]):
        return "Category / Product"

    if any(word in col for word in ["channel", "source", "platform"]):
        return "Channel / Source"

    if detected_type == "Numeric":
        return "General Numeric"

    if detected_type == "Categorical":
        return "General Category"

    return "Unknown / Text"


def get_columns_by_meaning(profile_df, meaning):
    return profile_df[
        profile_df["Business Meaning"] == meaning
    ]["Column Name"].tolist()


def create_column_profile(df):
    column_profiles = []

    for column in df.columns:
        missing_values = df[column].isnull().sum()
        missing_percentage = (missing_values / len(df)) * 100
        unique_values = df[column].nunique(dropna=True)
        sample_values = df[column].dropna().astype(str).head(3).tolist()

        detected_type = detect_column_type(df, column)
        business_meaning = detect_business_meaning(column, detected_type)

        column_profiles.append({
            "Column Name": column,
            "Data Type": str(df[column].dtype),
            "Detected Type": detected_type,
            "Business Meaning": business_meaning,
            "Missing Values": missing_values,
            "Missing Percentage": round(missing_percentage, 2),
            "Unique Values": unique_values,
            "Sample Values": ", ".join(sample_values)
        })

    return pd.DataFrame(column_profiles)


def detect_outliers_iqr(df, numeric_columns):
    outlier_summary = []

    for column in numeric_columns:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        outlier_rows = df[
            (df[column] < lower_limit) | (df[column] > upper_limit)
        ]

        outlier_count = outlier_rows.shape[0]

        if outlier_count > 0:
            outlier_summary.append({
                "Column Name": column,
                "Outlier Count": outlier_count,
                "Lower Limit": round(lower_limit, 2),
                "Upper Limit": round(upper_limit, 2)
            })

    return pd.DataFrame(outlier_summary)


# ============================================================
# DATASET UPLOAD
# ============================================================

st.sidebar.header("Dataset Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Uploaded dataset loaded successfully.")
    dataset_source = "Uploaded CSV file"
else:
    df = pd.read_csv("data/raw/messy_business_data.csv")
    st.sidebar.info("Using default sample dataset.")
    dataset_source = "Default sample dataset"

st.caption(f"Current Dataset Source: {dataset_source}")


# ============================================================
# COLUMN PROFILING AND DETECTION
# ============================================================

column_profile_df = create_column_profile(df)

numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

detected_date_columns = column_profile_df[
    column_profile_df["Detected Type"] == "Date-like"
]["Column Name"].tolist()

detected_category_columns = column_profile_df[
    column_profile_df["Detected Type"] == "Categorical"
]["Column Name"].tolist()

quantity_columns = get_columns_by_meaning(column_profile_df, "Quantity")
amount_columns = get_columns_by_meaning(column_profile_df, "Price / Amount")
discount_columns = get_columns_by_meaning(column_profile_df, "Discount")
rating_columns = get_columns_by_meaning(column_profile_df, "Rating / Score")


# ============================================================
# BASIC AUDIT CALCULATIONS
# ============================================================

total_rows = df.shape[0]
total_columns = df.shape[1]
total_cells = total_rows * total_columns

missing_count = df.isnull().sum()
missing_percentage = (df.isnull().sum() / len(df)) * 100

missing_summary = pd.DataFrame({
    "Column Name": df.columns,
    "Missing Values": missing_count.values,
    "Missing Percentage": missing_percentage.round(2).values
})

total_missing_values = int(df.isnull().sum().sum())
total_duplicate_rows = int(df.duplicated().sum())

duplicate_rows = df[df.duplicated()]

if len(numeric_columns) > 0:
    total_negative_values = int((df[numeric_columns] < 0).sum().sum())
else:
    total_negative_values = 0


# ============================================================
# NEGATIVE VALUES
# ============================================================

negative_summary = []

for column in numeric_columns:
    negative_count = int((df[column] < 0).sum())

    if negative_count > 0:
        negative_summary.append({
            "Column Name": column,
            "Negative Values Count": negative_count
        })

negative_summary_df = pd.DataFrame(negative_summary)

if len(numeric_columns) > 0:
    negative_rows = df[
        (df[numeric_columns] < 0).any(axis=1)
    ]
else:
    negative_rows = pd.DataFrame()


# ============================================================
# DATE VALIDATION
# ============================================================

date_issue_summary = []
total_invalid_dates = 0

for date_column in detected_date_columns:
    converted_dates = safe_to_datetime(df[date_column])

    invalid_date_count = int(converted_dates.isnull().sum())
    valid_date_count = int(converted_dates.notnull().sum())

    total_invalid_dates += invalid_date_count

    date_issue_summary.append({
        "Date Column": date_column,
        "Invalid Date Count": invalid_date_count,
        "Valid Date Count": valid_date_count
    })

date_issue_summary_df = pd.DataFrame(date_issue_summary)


# ============================================================
# BUSINESS RULE VALIDATION
# ============================================================

business_rule_summary = []

for column in quantity_columns:
    if column in numeric_columns:
        invalid_count = int((df[column] <= 0).sum())
        business_rule_summary.append({
            "Business Rule": "Quantity should be greater than 0",
            "Column Name": column,
            "Invalid Count": invalid_count
        })

for column in amount_columns:
    if column in numeric_columns:
        invalid_count = int((df[column] < 0).sum())
        business_rule_summary.append({
            "Business Rule": "Price / Amount should not be negative",
            "Column Name": column,
            "Invalid Count": invalid_count
        })

for column in discount_columns:
    if column in numeric_columns:
        invalid_count = int(((df[column] < 0) | (df[column] > 100)).sum())
        business_rule_summary.append({
            "Business Rule": "Discount should be between 0 and 100",
            "Column Name": column,
            "Invalid Count": invalid_count
        })

for column in rating_columns:
    if column in numeric_columns:
        invalid_count = int(((df[column] < 1) | (df[column] > 5)).sum())
        business_rule_summary.append({
            "Business Rule": "Rating / Score should be between 1 and 5",
            "Column Name": column,
            "Invalid Count": invalid_count
        })

business_rule_summary_df = pd.DataFrame(business_rule_summary)

if not business_rule_summary_df.empty:
    total_business_rule_violations = int(business_rule_summary_df["Invalid Count"].sum())
else:
    total_business_rule_violations = 0


# ============================================================
# OUTLIERS
# ============================================================

outlier_summary_df = detect_outliers_iqr(df, numeric_columns)

if not outlier_summary_df.empty:
    total_outliers = int(outlier_summary_df["Outlier Count"].sum())
else:
    total_outliers = 0


# ============================================================
# CATEGORY INCONSISTENCIES
# ============================================================

category_summary = []
total_category_inconsistencies = 0

for column in detected_category_columns:
    unique_count_before = df[column].nunique(dropna=True)

    cleaned_temp = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .str.title()
    )

    unique_count_after_standardization = cleaned_temp.nunique(dropna=True)
    inconsistency_count = unique_count_before - unique_count_after_standardization

    total_category_inconsistencies += inconsistency_count

    category_summary.append({
        "Column Name": column,
        "Unique Values Before Cleaning": unique_count_before,
        "Unique Values After Basic Standardization": unique_count_after_standardization,
        "Possible Inconsistency Count": inconsistency_count
    })

category_summary_df = pd.DataFrame(category_summary)


# ============================================================
# AUDIT SUMMARY AND QUALITY SCORE
# ============================================================

audit_summary = pd.DataFrame({
    "Audit Check": [
        "Total Rows",
        "Total Columns",
        "Total Data Cells",
        "Missing Values",
        "Duplicate Rows",
        "Negative Values",
        "Invalid Dates",
        "Business Rule Violations",
        "Outliers",
        "Possible Category Inconsistencies"
    ],
    "Count": [
        total_rows,
        total_columns,
        total_cells,
        total_missing_values,
        total_duplicate_rows,
        total_negative_values,
        total_invalid_dates,
        total_business_rule_violations,
        total_outliers,
        total_category_inconsistencies
    ]
})

missing_penalty = (total_missing_values / total_cells) * 25 if total_cells > 0 else 0
duplicate_penalty = (total_duplicate_rows / total_rows) * 20 if total_rows > 0 else 0
negative_penalty = (total_negative_values / total_cells) * 10 if total_cells > 0 else 0
invalid_date_penalty = (total_invalid_dates / total_rows) * 15 if total_rows > 0 else 0
business_rule_penalty = (total_business_rule_violations / total_rows) * 15 if total_rows > 0 else 0
outlier_penalty = (total_outliers / total_cells) * 10 if total_cells > 0 else 0
category_penalty = (
    total_category_inconsistencies / max(len(detected_category_columns), 1)
) * 5

total_penalty = (
    missing_penalty
    + duplicate_penalty
    + negative_penalty
    + invalid_date_penalty
    + business_rule_penalty
    + outlier_penalty
    + category_penalty
)

quality_score = 100 - total_penalty
quality_score = max(0, min(100, round(quality_score, 2)))


# ============================================================
# SAFE CLEANING
# ============================================================

cleaned_df = df.copy()

original_row_count = cleaned_df.shape[0]
cleaned_df = cleaned_df.drop_duplicates()
duplicates_removed = original_row_count - cleaned_df.shape[0]

for column in detected_category_columns:
    cleaned_df[column] = cleaned_df[column].fillna("Unknown")
    cleaned_df[column] = cleaned_df[column].astype(str).str.strip().str.title()

for date_column in detected_date_columns:
    cleaned_df[date_column] = safe_to_datetime(cleaned_df[date_column])
    cleaned_df[f"{date_column}_Invalid_Flag"] = cleaned_df[date_column].isnull()

for column in quantity_columns:
    if column in numeric_columns:
        cleaned_df[f"{column}_Invalid_Quantity_Flag"] = cleaned_df[column] <= 0

for column in amount_columns:
    if column in numeric_columns:
        cleaned_df[f"{column}_Negative_Amount_Flag"] = cleaned_df[column] < 0

for column in discount_columns:
    if column in numeric_columns:
        invalid_discount_mask = (cleaned_df[column] < 0) | (cleaned_df[column] > 100)
        cleaned_df[f"{column}_Invalid_Discount_Flag"] = invalid_discount_mask
        cleaned_df.loc[invalid_discount_mask, column] = float("nan")

for column in rating_columns:
    if column in numeric_columns:
        invalid_rating_mask = (
            (cleaned_df[column] < 1) |
            (cleaned_df[column] > 5)
        )
        cleaned_df[f"{column}_Invalid_Rating_Flag"] = invalid_rating_mask
        cleaned_df.loc[invalid_rating_mask, column] = float("nan")

for column in numeric_columns:
    median_value = cleaned_df[column].median()

    if pd.notna(median_value):
        cleaned_df[column] = cleaned_df[column].fillna(median_value)

for column in numeric_columns:
    q1 = cleaned_df[column].quantile(0.25)
    q3 = cleaned_df[column].quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        cleaned_df[f"{column}_Outlier_Flag"] = False
        continue

    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    cleaned_df[f"{column}_Outlier_Flag"] = (
        (cleaned_df[column] < lower_limit) |
        (cleaned_df[column] > upper_limit)
    )

cleaning_summary = pd.DataFrame({
    "Cleaning Step": [
        "Original Rows",
        "Rows After Removing Duplicates",
        "Duplicate Rows Removed",
        "Missing Values After Cleaning",
        "Columns After Adding Flags"
    ],
    "Result": [
        original_row_count,
        cleaned_df.shape[0],
        duplicates_removed,
        int(cleaned_df.isnull().sum().sum()),
        cleaned_df.shape[1]
    ]
})


# ============================================================
# RECOMMENDATIONS
# ============================================================

recommendations = []

if total_missing_values > 0:
    recommendations.append({
        "Issue Detected": "Missing Values",
        "Recommendation": "Review missing values. Fill numeric columns with median and categorical columns with 'Unknown' when business logic allows.",
        "Why It Matters": "Missing values can affect KPIs, averages, totals, and dashboard accuracy."
    })

if total_duplicate_rows > 0:
    recommendations.append({
        "Issue Detected": "Duplicate Rows",
        "Recommendation": "Remove exact duplicate rows before reporting.",
        "Why It Matters": "Duplicate records can inflate sales, quantity, revenue, and customer counts."
    })

if total_negative_values > 0:
    recommendations.append({
        "Issue Detected": "Negative Numeric Values",
        "Recommendation": "Review negative values before deletion because they may represent returns, refunds, or corrections.",
        "Why It Matters": "Negative values can reduce totals and create misleading business metrics."
    })

if total_invalid_dates > 0:
    recommendations.append({
        "Issue Detected": "Invalid Dates",
        "Recommendation": "Convert invalid dates to missing date values and flag them for source correction.",
        "Why It Matters": "Invalid dates affect monthly trends, time-series analysis, and dashboard filters."
    })

if total_business_rule_violations > 0:
    recommendations.append({
        "Issue Detected": "Business Rule Violations",
        "Recommendation": "Review quantity, amount, discount, and rating columns based on expected business rules.",
        "Why It Matters": "Business rule violations can create incorrect KPIs and misleading analysis."
    })

if total_outliers > 0:
    recommendations.append({
        "Issue Detected": "Outliers",
        "Recommendation": "Flag outliers for review instead of automatically removing them.",
        "Why It Matters": "Some outliers may be valid high-value transactions."
    })

if total_category_inconsistencies > 0:
    recommendations.append({
        "Issue Detected": "Inconsistent Categories",
        "Recommendation": "Standardize category values by trimming spaces and using consistent case.",
        "Why It Matters": "Inconsistent categories can split the same value into multiple groups in BI reports."
    })

recommendation_df = pd.DataFrame(recommendations)


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

summary_points = []

summary_points.append(
    f"The dataset contains {total_rows} rows, {total_columns} columns, and {total_cells} total data cells."
)

summary_points.append(
    f"The overall data quality score is {quality_score}/100."
)

if total_missing_values > 0:
    summary_points.append(
        f"There are {total_missing_values} missing values that may affect reporting accuracy."
    )

if total_duplicate_rows > 0:
    summary_points.append(
        f"There are {total_duplicate_rows} duplicate rows that should be removed to avoid inflated reports."
    )

if total_negative_values > 0:
    summary_points.append(
        f"There are {total_negative_values} negative numeric values that should be reviewed before analysis."
    )

if total_invalid_dates > 0:
    summary_points.append(
        f"There are {total_invalid_dates} invalid date values that may impact time-based analysis."
    )

if total_business_rule_violations > 0:
    summary_points.append(
        f"There are {total_business_rule_violations} business rule violations across quantity, amount, discount, or rating columns."
    )

if total_outliers > 0:
    summary_points.append(
        f"There are {total_outliers} detected outliers. These should be reviewed instead of removed automatically."
    )

if total_category_inconsistencies > 0:
    summary_points.append(
        f"There are {total_category_inconsistencies} possible category inconsistencies caused by spacing or capitalization issues."
    )

if quality_score >= 85:
    final_summary = "Overall, the dataset has good quality and may only require minor cleaning."
elif quality_score >= 70:
    final_summary = "Overall, the dataset has moderate data quality issues. Cleaning is recommended before dashboard creation."
else:
    final_summary = "Overall, the dataset has poor data quality and requires strong cleaning before reporting."

summary_points.append(final_summary)


# ============================================================
# DOWNLOADABLE AUDIT REPORT
# ============================================================

report_text = "AI Data Cleaning & Quality Audit Report\n"
report_text += "=" * 45 + "\n\n"

report_text += f"Dataset Source: {dataset_source}\n"
report_text += f"Rows: {total_rows}\n"
report_text += f"Columns: {total_columns}\n"
report_text += f"Total Cells: {total_cells}\n"
report_text += f"Data Quality Score: {quality_score}/100\n\n"

report_text += "Executive Summary:\n"
for point in summary_points:
    report_text += f"- {point}\n"

report_text += "\nAudit Summary:\n"
report_text += audit_summary.to_string(index=False)

if not recommendation_df.empty:
    report_text += "\n\nRecommendations:\n"
    for _, row in recommendation_df.iterrows():
        report_text += f"\nIssue: {row['Issue Detected']}\n"
        report_text += f"Recommendation: {row['Recommendation']}\n"
        report_text += f"Why It Matters: {row['Why It Matters']}\n"


# ============================================================
# STREAMLIT TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dataset Overview",
    "Column Profiling",
    "Quality Audit",
    "Cleaning Output",
    "Recommendations",
    "Executive Summary"
])


with tab1:
    st.subheader("Dataset Preview")
    st.dataframe(df.head(20), width="stretch")

    st.subheader("Dataset Shape")
    st.write("Rows and Columns:", df.shape)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", total_rows)
    col2.metric("Total Columns", total_columns)
    col3.metric("Total Data Cells", total_cells)

    st.subheader("Column Names")
    st.write(df.columns.tolist())

    st.subheader("Data Types")
    data_types = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.astype(str).values
    })
    st.dataframe(data_types, width="stretch")


with tab2:
    st.subheader("Dynamic Column Profiling")
    st.dataframe(column_profile_df, width="stretch")

    st.subheader("Detected Column Groups")

    detected_groups = pd.DataFrame({
        "Group": [
            "Numeric Columns",
            "Date-like Columns",
            "Categorical Columns",
            "Quantity Columns",
            "Price / Amount Columns",
            "Discount Columns",
            "Rating / Score Columns"
        ],
        "Detected Columns": [
            ", ".join(numeric_columns) if numeric_columns else "None",
            ", ".join(detected_date_columns) if detected_date_columns else "None",
            ", ".join(detected_category_columns) if detected_category_columns else "None",
            ", ".join(quantity_columns) if quantity_columns else "None",
            ", ".join(amount_columns) if amount_columns else "None",
            ", ".join(discount_columns) if discount_columns else "None",
            ", ".join(rating_columns) if rating_columns else "None"
        ],
        "Count": [
            len(numeric_columns),
            len(detected_date_columns),
            len(detected_category_columns),
            len(quantity_columns),
            len(amount_columns),
            len(discount_columns),
            len(rating_columns)
        ]
    })

    st.dataframe(detected_groups, width="stretch")

    st.subheader("Business Meaning Mapping")
    st.dataframe(
        column_profile_df[["Column Name", "Detected Type", "Business Meaning"]],
        width="stretch"
    )


with tab3:
    st.subheader("Missing Values Summary")
    st.dataframe(missing_summary, width="stretch")

    st.subheader("Duplicate Rows Check")
    st.write("Total Duplicate Rows:", total_duplicate_rows)

    if total_duplicate_rows > 0:
        st.warning(f"Found {total_duplicate_rows} duplicate rows.")
        st.dataframe(duplicate_rows.head(10), width="stretch")
    else:
        st.success("No duplicate rows found.")

    st.subheader("Negative Values Check")

    if negative_summary_df.empty:
        st.success("No negative values found in numeric columns.")
    else:
        st.warning("Negative values found.")
        st.dataframe(negative_summary_df, width="stretch")
        st.dataframe(negative_rows.head(10), width="stretch")

    st.subheader("Dynamic Invalid Date Check")

    if date_issue_summary_df.empty:
        st.info("No date-like columns detected.")
    else:
        st.dataframe(date_issue_summary_df, width="stretch")

        selected_date_column = st.selectbox(
            "Select a date column to view invalid rows",
            detected_date_columns
        )

        selected_converted_dates = safe_to_datetime(df[selected_date_column])
        invalid_date_rows = df[selected_converted_dates.isnull()]

        if invalid_date_rows.empty:
            st.success(f"No invalid dates found in {selected_date_column}.")
        else:
            st.warning(f"Invalid dates found in {selected_date_column}.")
            st.dataframe(invalid_date_rows.head(10), width="stretch")

    st.subheader("Dynamic Business Rule Validation")

    if business_rule_summary_df.empty:
        st.info("No business-rule columns detected.")
    else:
        st.dataframe(business_rule_summary_df, width="stretch")

        issue_columns = business_rule_summary_df[
            business_rule_summary_df["Invalid Count"] > 0
        ]["Column Name"].tolist()

        if issue_columns:
            selected_business_column = st.selectbox(
                "Select a business-rule column to view invalid rows",
                issue_columns
            )

            if selected_business_column in quantity_columns:
                invalid_business_rows = df[df[selected_business_column] <= 0]
            elif selected_business_column in amount_columns:
                invalid_business_rows = df[df[selected_business_column] < 0]
            elif selected_business_column in discount_columns:
                invalid_business_rows = df[
                    (df[selected_business_column] < 0) |
                    (df[selected_business_column] > 100)
                ]
            elif selected_business_column in rating_columns:
                invalid_business_rows = df[
                    (df[selected_business_column] < 1) |
                    (df[selected_business_column] > 5)
                ]
            else:
                invalid_business_rows = pd.DataFrame()

            st.dataframe(invalid_business_rows.head(10), width="stretch")
        else:
            st.success("No business rule violations found.")

    st.subheader("Outlier Detection using IQR Method")

    if outlier_summary_df.empty:
        st.success("No major outliers detected.")
    else:
        st.warning("Outliers detected.")
        st.dataframe(outlier_summary_df, width="stretch")

        selected_outlier_column = st.selectbox(
            "Select a column to view outlier rows",
            outlier_summary_df["Column Name"].tolist()
        )

        q1 = df[selected_outlier_column].quantile(0.25)
        q3 = df[selected_outlier_column].quantile(0.75)
        iqr = q3 - q1
        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        selected_outlier_rows = df[
            (df[selected_outlier_column] < lower_limit) |
            (df[selected_outlier_column] > upper_limit)
        ]

        st.dataframe(selected_outlier_rows.head(20), width="stretch")

    st.subheader("Dynamic Inconsistent Category Check")

    if category_summary_df.empty:
        st.info("No categorical columns detected.")
    else:
        st.dataframe(category_summary_df, width="stretch")

        selected_category_column = st.selectbox(
            "Select a category column to view unique values",
            detected_category_columns
        )

        unique_values = pd.DataFrame({
            "Unique Values": df[selected_category_column].dropna().unique()
        })

        st.dataframe(unique_values, width="stretch")

    st.subheader("Overall Data Quality Audit Summary")
    st.dataframe(audit_summary, width="stretch")

    st.subheader("Data Quality Score")
    st.metric("Overall Data Quality Score", f"{quality_score}/100")

    if quality_score >= 85:
        st.success("Good data quality. Minor cleaning may be required.")
    elif quality_score >= 70:
        st.warning("Moderate data quality. Cleaning is recommended before analysis.")
    else:
        st.error("Poor data quality. Strong cleaning is required before reporting.")


with tab4:
    st.subheader("Safe Data Cleaning Summary")
    st.dataframe(cleaning_summary, width="stretch")

    st.subheader("Cleaned Dataset Preview")
    st.dataframe(cleaned_df.head(20), width="stretch")

    cleaned_csv = cleaned_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Cleaned CSV",
        data=cleaned_csv,
        file_name="cleaned_business_data.csv",
        mime="text/csv"
    )


with tab5:
    st.subheader("Cleaning Recommendations")

    if recommendation_df.empty:
        st.success("No major data quality issues found. Dataset looks ready for analysis.")
    else:
        st.dataframe(recommendation_df, width="stretch")

    st.subheader("Download Audit Report")

    st.download_button(
        label="Download Audit Report TXT",
        data=report_text.encode("utf-8"),
        file_name="data_quality_audit_report.txt",
        mime="text/plain"
    )


with tab6:
    st.subheader("Executive Data Quality Summary")

    for point in summary_points:
        st.write("- " + point)