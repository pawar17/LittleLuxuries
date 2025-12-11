"""
========================================================================================================
MEGA TABLEAU DATASET CREATOR
========================================================================================================
Creates a single, comprehensive Tableau dataset combining ALL data sources
- Time series data (monthly level)
- Search indicators
- Purchase behavior
- Census data
- Economic indicators
All combined on DATE as the common key
========================================================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print(" " * 30 + "MEGA TABLEAU DATASET CREATOR")
print("=" * 100)
print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ========================================================================================================
# LOAD ALL PROCESSED DATA
# ========================================================================================================

print("=" * 100)
print("LOADING ALL PROCESSED DATA FILES")
print("=" * 100)

# 1. Load master dataset (has all time series data)
print("\n[1/5] Loading master dataset...")
master_df = pd.read_csv('Processed_Data/master_dataset_complete.csv')
master_df['date'] = pd.to_datetime(master_df['date'])
print(f"  OK Master dataset: {len(master_df)} rows, {len(master_df.columns)} columns")

# 2. Load search indicator results
print("\n[2/5] Loading search indicator results...")
search_results = pd.read_csv('Processed_Data/search_indicators_results_final.csv')
print(f"  OK Search results: {len(search_results)} indicators")

# 3. Load retail transactions (processed)
print("\n[3/5] Loading retail transactions...")
try:
    retail_df = pd.read_csv('Processed_Data/retail_transactions_processed.csv')
    retail_df['Transaction Date'] = pd.to_datetime(retail_df['Transaction Date'])
    print(f"  OK Retail transactions: {len(retail_df):,} rows")
except:
    print("  X Retail transactions not found (will skip)")
    retail_df = None

# 4. Load census results
print("\n[4/5] Loading census analysis results...")
try:
    census_results = pd.read_csv('Processed_Data/census_retail_results.csv')
    print(f"  OK Census results: {len(census_results)} categories")
except:
    print("  X Census results not found (will skip)")
    census_results = None

# 5. Load census time series data
print("\n[5/5] Loading census time series...")
try:
    census_ts = pd.read_csv('Tableau_Data/tableau_census_timeseries.csv')
    census_ts['observation_date'] = pd.to_datetime(census_ts['observation_date'])
    print(f"  OK Census time series: {len(census_ts)} rows")
except:
    print("  X Census time series not found (will skip)")
    census_ts = None

# ========================================================================================================
# CREATE MEGA DATASET - TIME SERIES LEVEL
# ========================================================================================================

print("\n" + "=" * 100)
print("CREATING MEGA DATASET - TIME SERIES LEVEL")
print("=" * 100)

# Start with master dataset
mega_df = master_df.copy()

# Add census time series data (pivot to wide format)
if census_ts is not None:
    print("\nAdding Census retail sales time series...")

    # Pivot census data to have beauty and fashion as separate columns
    census_beauty = census_ts[census_ts['category'] == 'Beauty & Personal Care'][['observation_date', 'sales']].copy()
    census_beauty.columns = ['date', 'census_beauty_sales']

    census_fashion = census_ts[census_ts['category'] == "Women's Clothing"][['observation_date', 'sales']].copy()
    census_fashion.columns = ['date', 'census_fashion_sales']

    mega_df = mega_df.merge(census_beauty, on='date', how='left')
    mega_df = mega_df.merge(census_fashion, on='date', how='left')
    print(f"  OK Census sales added")

# Add retail transaction monthly aggregates (if not already in master)
if retail_df is not None:
    print("\nAdding retail transaction monthly aggregates...")

    # Check if already in master, if not add it
    if 'retail_total_spending' not in mega_df.columns:
        retail_df['year_month'] = retail_df['Transaction Date'].dt.to_period('M').dt.to_timestamp()

        # Overall aggregates
        retail_monthly = retail_df.groupby('year_month').agg({
            'Total Spent': ['sum', 'mean', 'count'],
            'Customer ID': 'nunique'
        }).reset_index()
        retail_monthly.columns = ['date', 'retail_total_spending', 'retail_avg_transaction',
                                  'retail_transaction_count', 'retail_unique_customers']

        mega_df = mega_df.merge(retail_monthly, on='date', how='left')
        print(f"  OK Retail aggregates added")

    # Add luxury-specific metrics
    print("  Adding luxury purchase metrics...")
    luxury_monthly = retail_df[retail_df['purchase_type'] == 'Little Luxury'].groupby('year_month').agg({
        'Total Spent': ['sum', 'count', 'mean'],
        'Customer ID': 'nunique'
    }).reset_index()
    luxury_monthly.columns = ['date', 'luxury_total_spending', 'luxury_transaction_count',
                              'luxury_avg_transaction', 'luxury_unique_customers']

    mega_df = mega_df.merge(luxury_monthly, on='date', how='left')

    # Add necessity metrics
    necessity_monthly = retail_df[retail_df['purchase_type'] == 'Necessity'].groupby('year_month').agg({
        'Total Spent': ['sum', 'count'],
    }).reset_index()
    necessity_monthly.columns = ['date', 'necessity_total_spending', 'necessity_transaction_count']

    mega_df = mega_df.merge(necessity_monthly, on='date', how='left')

    # Calculate luxury ratio
    mega_df['luxury_ratio_pct'] = (mega_df['luxury_total_spending'] /
                                    mega_df['retail_total_spending'] * 100)

    print(f"  OK Luxury metrics added")

    # Add category breakdown
    print("  Adding category breakdowns...")
    if 'luxury_category' in retail_df.columns:
        for category in retail_df['luxury_category'].unique():
            if category != 'Other':
                cat_data = retail_df[retail_df['luxury_category'] == category].groupby('year_month').agg({
                    'Total Spent': 'sum'
                }).reset_index()
                col_name = f'luxury_{category.lower().replace(" & ", "_").replace(" ", "_")}_spending'
                cat_data.columns = ['date', col_name]
                mega_df = mega_df.merge(cat_data, on='date', how='left')
        print(f"  OK Category breakdowns added")

# Add search indicator rankings as separate columns
print("\nAdding search indicator rankings...")
for idx, row in search_results.iterrows():
    indicator = row['Indicator']
    mega_df[f'{indicator}_R_squared'] = row['R²']
    mega_df[f'{indicator}_p_value'] = row['P-value']
    mega_df[f'{indicator}_coefficient'] = row['Coefficient']
    mega_df[f'{indicator}_significant'] = row['Significant']

print(f"  OK Search rankings added ({len(search_results)} indicators)")

# Add census correlation results
if census_results is not None:
    print("\nAdding census correlation results...")
    for idx, row in census_results.iterrows():
        category = row['Category'].replace(' ', '_').replace('(', '').replace(')', '').replace("'", '')
        mega_df[f'census_{category}_R_squared'] = row['R²']
        mega_df[f'census_{category}_p_value'] = row['P-value']
        mega_df[f'census_{category}_coefficient'] = row['Coefficient']
    print(f"  OK Census results added")

# ========================================================================================================
# ADD ADDITIONAL FEATURES FOR TABLEAU
# ========================================================================================================

print("\n" + "=" * 100)
print("ADDING TABLEAU-FRIENDLY FEATURES")
print("=" * 100)

# Date components (if not already present)
if 'year' not in mega_df.columns:
    mega_df['year'] = mega_df['date'].dt.year
if 'month' not in mega_df.columns:
    mega_df['month'] = mega_df['date'].dt.month
if 'quarter' not in mega_df.columns:
    mega_df['quarter'] = mega_df['date'].dt.quarter

mega_df['month_name'] = mega_df['date'].dt.strftime('%B')
mega_df['year_month'] = mega_df['date'].dt.strftime('%Y-%m')
mega_df['year_quarter'] = mega_df['date'].dt.to_period('Q').astype(str)

print("  OK Date components added")

# Economic period labels (if not already present)
if 'period' not in mega_df.columns:
    mega_df['period'] = 'Normal'
    mega_df.loc[(mega_df['date'] >= '2007-12-01') & (mega_df['date'] <= '2009-06-30'), 'period'] = 'Great Recession'
    mega_df.loc[(mega_df['date'] >= '2020-02-01') & (mega_df['date'] <= '2020-04-30'), 'period'] = 'COVID-19 Crisis'
    mega_df.loc[(mega_df['date'] >= '2022-01-01') & (mega_df['date'] <= '2023-06-30'), 'period'] = 'Inflation Surge'

print("  OK Economic period labels added")

# Recession flags
if 'is_recession' not in mega_df.columns:
    mega_df['is_recession'] = ((mega_df['period'] == 'Great Recession') |
                               (mega_df['period'] == 'COVID-19 Crisis')).astype(int)

print("  OK Recession flags added")

# CCI categories (Low, Medium, High confidence)
if 'cci' in mega_df.columns:
    cci_tertiles = mega_df['cci'].quantile([0.33, 0.67])
    mega_df['cci_category'] = 'Medium'
    mega_df.loc[mega_df['cci'] <= cci_tertiles[0.33], 'cci_category'] = 'Low Confidence'
    mega_df.loc[mega_df['cci'] >= cci_tertiles[0.67], 'cci_category'] = 'High Confidence'
    print("  OK CCI categories added")

# Unemployment categories
if 'unemployment_rate' in mega_df.columns:
    mega_df['unemployment_category'] = 'Normal'
    mega_df.loc[mega_df['unemployment_rate'] < 5, 'unemployment_category'] = 'Low (<5%)'
    mega_df.loc[(mega_df['unemployment_rate'] >= 5) & (mega_df['unemployment_rate'] < 8), 'unemployment_category'] = 'Moderate (5-8%)'
    mega_df.loc[mega_df['unemployment_rate'] >= 8, 'unemployment_category'] = 'High (>=8%)'
    print("  OK Unemployment categories added")

# Search indicator categories (Top performer, Significant, Not significant)
score_cols = [col for col in mega_df.columns if col.endswith('_score')]
for col in score_cols:
    indicator_name = col.replace('_score', '')
    sig_col = f'{indicator_name}_significant'
    r2_col = f'{indicator_name}_R_squared'

    if sig_col in mega_df.columns and r2_col in mega_df.columns:
        mega_df[f'{indicator_name}_performance'] = 'Not Significant'
        mega_df.loc[(mega_df[sig_col] == 'Yes') & (mega_df[r2_col] < 0.10), f'{indicator_name}_performance'] = 'Significant'
        mega_df.loc[(mega_df[sig_col] == 'Yes') & (mega_df[r2_col] >= 0.10), f'{indicator_name}_performance'] = 'Top Performer'

print("  OK Performance categories added")

# ========================================================================================================
# CREATE METADATA TABLE
# ========================================================================================================

print("\n" + "=" * 100)
print("CREATING METADATA TABLE")
print("=" * 100)

metadata = []

# Document all columns
for col in mega_df.columns:
    col_type = str(mega_df[col].dtype)
    non_null = mega_df[col].notna().sum()
    null_count = mega_df[col].isna().sum()

    # Determine category
    if col == 'date':
        category = 'Temporal'
        description = 'Date (monthly frequency)'
    elif col.endswith('_score'):
        category = 'Search Indicator Score'
        description = f'Latent variable score for {col.replace("_score", "")} (SEM)'
    elif col.endswith('_R_squared'):
        category = 'Search Indicator Metric'
        description = f'R-squared value for {col.replace("_R_squared", "")}'
    elif col.endswith('_p_value'):
        category = 'Search Indicator Metric'
        description = f'P-value for {col.replace("_p_value", "")}'
    elif col.endswith('_coefficient'):
        category = 'Search Indicator Metric'
        description = f'Regression coefficient for {col.replace("_coefficient", "")}'
    elif col.endswith('_significant'):
        category = 'Search Indicator Flag'
        description = f'Significance flag for {col.replace("_significant", "")} (Yes/No)'
    elif col.startswith('census_'):
        category = 'Census Data'
        description = f'Census retail sales metric: {col}'
    elif col.startswith('luxury_'):
        category = 'Purchase Behavior - Luxury'
        description = f'Little luxury metric: {col}'
    elif col.startswith('necessity_'):
        category = 'Purchase Behavior - Necessity'
        description = f'Necessity spending metric: {col}'
    elif col.startswith('retail_'):
        category = 'Purchase Behavior - Overall'
        description = f'Retail transaction metric: {col}'
    elif col in ['cci', 'cpi', 'unemployment_rate', 'consumer_sentiment', 'personal_saving_rate', 'retail_sales_clothing']:
        category = 'Economic Indicator'
        description = f'FRED economic indicator: {col}'
    elif col in ['year', 'month', 'quarter', 'month_name', 'year_month', 'year_quarter']:
        category = 'Temporal'
        description = f'Date component: {col}'
    elif col in ['period', 'is_recession', 'cci_category', 'unemployment_category']:
        category = 'Categorical Feature'
        description = f'Derived categorical variable: {col}'
    elif col.startswith('is_'):
        category = 'Binary Flag'
        description = f'Binary indicator: {col}'
    elif col.endswith('_performance'):
        category = 'Performance Category'
        description = f'Performance classification: {col}'
    else:
        category = 'Other'
        description = col

    metadata.append({
        'Column_Name': col,
        'Category': category,
        'Data_Type': col_type,
        'Description': description,
        'Non_Null_Count': non_null,
        'Null_Count': null_count,
        'Null_Percentage': f'{null_count / len(mega_df) * 100:.1f}%'
    })

metadata_df = pd.DataFrame(metadata)
print(f"\nOK Metadata created for {len(metadata_df)} columns")

# ========================================================================================================
# SAVE MEGA DATASET
# ========================================================================================================

print("\n" + "=" * 100)
print("SAVING MEGA TABLEAU DATASET")
print("=" * 100)

import os
os.makedirs('Tableau_Data', exist_ok=True)

# Save mega dataset
output_file = 'Tableau_Data/MEGA_TABLEAU_DATASET.csv'
mega_df.to_csv(output_file, index=False)
print(f"\nOK MEGA Dataset saved: {output_file}")
print(f"  Dimensions: {len(mega_df)} rows x {len(mega_df.columns)} columns")
print(f"  Date range: {mega_df['date'].min().strftime('%Y-%m')} to {mega_df['date'].max().strftime('%Y-%m')}")

# Save metadata
metadata_file = 'Tableau_Data/MEGA_DATASET_METADATA.csv'
metadata_df.to_csv(metadata_file, index=False)
print(f"\nOK Metadata saved: {metadata_file}")

# ========================================================================================================
# CREATE COLUMN GROUPING GUIDE
# ========================================================================================================

print("\n" + "=" * 100)
print("COLUMN GROUPING SUMMARY")
print("=" * 100)

category_summary = metadata_df.groupby('Category').agg({
    'Column_Name': 'count'
}).reset_index()
category_summary.columns = ['Category', 'Column_Count']
category_summary = category_summary.sort_values('Column_Count', ascending=False)

print("\nColumn distribution by category:")
for _, row in category_summary.iterrows():
    print(f"  - {row['Category']}: {row['Column_Count']} columns")

# ========================================================================================================
# FINAL SUMMARY
# ========================================================================================================

print("\n" + "=" * 100)
print(" " * 30 + "MEGA DATASET CREATION COMPLETE")
print("=" * 100)

print(f"\n** MEGA TABLEAU DATASET:")
print(f"  File: {output_file}")
print(f"  Rows: {len(mega_df):,}")
print(f"  Columns: {len(mega_df.columns)}")
print(f"  Date range: {mega_df['date'].min().strftime('%Y-%m')} to {mega_df['date'].max().strftime('%Y-%m')}")
print(f"  Time span: {(mega_df['date'].max() - mega_df['date'].min()).days / 365.25:.1f} years")

print(f"\n** WHAT'S INCLUDED:")
print(f"  - Google Trends search data (40 terms, 8 indicators)")
print(f"  - Economic indicators (CCI, CPI, Unemployment, Sentiment, Saving Rate)")
print(f"  - Retail transaction aggregates (overall + luxury + necessity)")
print(f"  - Census retail sales (beauty + fashion)")
print(f"  - Search indicator metrics (R², p-value, coefficient)")
print(f"  - Temporal features (year, month, quarter, period)")
print(f"  - Categorical features (confidence levels, unemployment categories)")
print(f"  - Recession indicators")

print(f"\n** METADATA:")
print(f"  File: {metadata_file}")
print(f"  Describes all {len(metadata_df)} columns")

print(f"\n** TABLEAU USAGE:")
print(f"  1. Import MEGA_TABLEAU_DATASET.csv into Tableau")
print(f"  2. Use 'date' as your primary dimension")
print(f"  3. All data is pre-joined - no need for multiple data sources!")
print(f"  4. Reference MEGA_DATASET_METADATA.csv to understand each column")

print(f"\n** KEY DIMENSIONS:")
print(f"  - date, year, month, quarter, year_month")
print(f"  - period (Great Recession, COVID-19 Crisis, etc.)")
print(f"  - cci_category (Low/Medium/High Confidence)")
print(f"  - unemployment_category (Low/Moderate/High)")

print(f"\n** KEY MEASURES:")
print(f"  - All search indicator scores (*_score)")
print(f"  - Economic indicators (cci, unemployment_rate, cpi, etc.)")
print(f"  - Retail spending (luxury, necessity, total)")
print(f"  - Census sales (beauty, fashion)")

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)
