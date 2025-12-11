"""
========================================================================================================
PRESENTATION DATA COMPILATION SCRIPT
========================================================================================================
Creates a comprehensive dataframe containing ALL data sources used in the analysis
and generates visualizations showing data distribution and processing flow.

This script:
1. Loads all raw data sources
2. Combines them into a single comprehensive presentation dataframe
3. Creates data distribution visualizations
4. Documents the data processing pipeline
========================================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print(" " * 25 + "COMPREHENSIVE DATA COMPILATION FOR PRESENTATION")
print("=" * 100)
print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ========================================================================================================
# PART 1: LOAD ALL RAW DATA SOURCES
# ========================================================================================================

print("=" * 100)
print("PART 1: LOADING ALL RAW DATA SOURCES")
print("=" * 100)

# 1. Google Trends Data
print("\n[1/9] Loading Google Trends data...")
google_trends = pd.read_excel('Data_Sources/All_Variables_Us_Data_Sheet1.xlsx', header=1)
# Clean numeric columns
for col in google_trends.columns:
    if google_trends[col].dtype == 'object':
        google_trends[col] = google_trends[col].astype(str).str.replace(',', '')
        google_trends[col] = pd.to_numeric(google_trends[col], errors='coerce')

if 'date' in google_trends.columns:
    google_trends['date'] = pd.to_datetime(google_trends['date'], errors='coerce')
    if google_trends['date'].isna().all():
        google_trends['date'] = pd.date_range(start='2004-01-01', periods=len(google_trends), freq='MS')

print(f"  OK Google Trends: {len(google_trends)} rows, {len(google_trends.columns)} columns")
print(f"    Period: {google_trends['date'].min().strftime('%Y-%m')} to {google_trends['date'].max().strftime('%Y-%m')}")

# 2. CPI (Consumer Price Index)
print("\n[2/9] Loading CPI data...")
cpi_data = pd.read_csv('Data_Sources/CPILFESL.csv')
cpi_data['observation_date'] = pd.to_datetime(cpi_data['observation_date'])
print(f"  OK CPI: {len(cpi_data)} rows")
print(f"    Period: {cpi_data['observation_date'].min().strftime('%Y-%m')} to {cpi_data['observation_date'].max().strftime('%Y-%m')}")

# 3. Consumer Confidence Index
print("\n[3/9] Loading Consumer Confidence Index...")
cci_data = pd.read_csv('Data_Sources/USACSCICP02STSAM.csv')
cci_data['observation_date'] = pd.to_datetime(cci_data['observation_date'])
print(f"  OK CCI: {len(cci_data)} rows")
print(f"    Period: {cci_data['observation_date'].min().strftime('%Y-%m')} to {cci_data['observation_date'].max().strftime('%Y-%m')}")

# 4. Consumer Sentiment
print("\n[4/9] Loading Consumer Sentiment...")
consumer_sentiment = pd.read_csv('Data_Sources/UMCSENT.csv')
consumer_sentiment['observation_date'] = pd.to_datetime(consumer_sentiment['observation_date'])
print(f"  OK Consumer Sentiment: {len(consumer_sentiment)} rows")

# 5. Unemployment Rate
print("\n[5/9] Loading Unemployment Rate...")
unemployment = pd.read_csv('Data_Sources/UNRATE.csv')
unemployment['observation_date'] = pd.to_datetime(unemployment['observation_date'])
print(f"  OK Unemployment: {len(unemployment)} rows")

# 6. Retail Sales (Clothing)
print("\n[6/9] Loading Retail Sales...")
retail_sales = pd.read_csv('Data_Sources/MRTSSM448USN.csv')
retail_sales['observation_date'] = pd.to_datetime(retail_sales['observation_date'])
print(f"  OK Retail Sales: {len(retail_sales)} rows")

# 7. Personal Saving Rate
print("\n[7/9] Loading Personal Saving Rate...")
saving_rate = pd.read_csv('Data_Sources/PSAVERT.csv')
saving_rate['observation_date'] = pd.to_datetime(saving_rate['observation_date'])
print(f"  OK Saving Rate: {len(saving_rate)} rows")

# 8. Retail Transactions
print("\n[8/9] Loading Retail Transaction data...")
retail_transactions = pd.read_csv('Data_Sources/spending_patterns_detailed.csv')
retail_transactions['Transaction Date'] = pd.to_datetime(retail_transactions['Transaction Date'])
print(f"  OK Retail Transactions: {len(retail_transactions):,} rows")
print(f"    Period: {retail_transactions['Transaction Date'].min().strftime('%Y-%m-%d')} to {retail_transactions['Transaction Date'].max().strftime('%Y-%m-%d')}")
print(f"    Total spending: ${retail_transactions['Total Spent'].sum():,.2f}")

# 9. Census Retail Sales
print("\n[9/9] Loading Census Retail Sales data...")
census_data = pd.read_csv('Data_Sources/census_retail_sales_1992_2025.csv')
census_data['observation_date'] = pd.to_datetime(census_data['observation_date'])
print(f"  OK Census Data: {len(census_data)} rows")
print(f"    Period: {census_data['observation_date'].min().strftime('%Y-%m')} to {census_data['observation_date'].max().strftime('%Y-%m')}")
print(f"    NAICS codes: {census_data['NAICS  Code'].unique()}")

# ========================================================================================================
# PART 2: CREATE COMPREHENSIVE PRESENTATION DATAFRAME
# ========================================================================================================

print("\n" + "=" * 100)
print("PART 2: CREATING COMPREHENSIVE PRESENTATION DATAFRAME")
print("=" * 100)

# Start with Google Trends as base (2004-2024)
presentation_df = google_trends.copy()

# Merge all FRED economic indicators
print("\nMerging economic indicators...")

# CPI
presentation_df = presentation_df.merge(
    cpi_data.rename(columns={'observation_date': 'date', 'CPILFESL': 'cpi'}),
    on='date', how='left'
)

# CCI (if not already in Google Trends data)
if 'USACSCICP02STSAM' in cci_data.columns:
    presentation_df = presentation_df.merge(
        cci_data.rename(columns={'observation_date': 'date', 'USACSCICP02STSAM': 'cci_fred'}),
        on='date', how='left'
    )

# Consumer Sentiment
presentation_df = presentation_df.merge(
    consumer_sentiment.rename(columns={'observation_date': 'date', 'UMCSENT': 'consumer_sentiment'}),
    on='date', how='left'
)

# Unemployment
presentation_df = presentation_df.merge(
    unemployment.rename(columns={'observation_date': 'date', 'UNRATE': 'unemployment_rate'}),
    on='date', how='left'
)

# Retail Sales
presentation_df = presentation_df.merge(
    retail_sales.rename(columns={'observation_date': 'date', 'MRTSSM448USN': 'retail_sales_clothing'}),
    on='date', how='left'
)

# Saving Rate
presentation_df = presentation_df.merge(
    saving_rate.rename(columns={'observation_date': 'date', 'PSAVERT': 'personal_saving_rate'}),
    on='date', how='left'
)

print(f"OK Economic indicators merged: {len(presentation_df)} rows x {len(presentation_df.columns)} columns")

# Add monthly retail transaction aggregates (for overlapping period)
print("\nAggregating retail transactions by month...")
retail_monthly = retail_transactions.copy()
retail_monthly['year_month'] = retail_monthly['Transaction Date'].dt.to_period('M').dt.to_timestamp()

retail_agg = retail_monthly.groupby('year_month').agg({
    'Total Spent': ['sum', 'mean', 'count'],
    'Customer ID': 'nunique'
}).reset_index()
retail_agg.columns = ['date', 'retail_total_spending', 'retail_avg_transaction',
                      'retail_transaction_count', 'retail_unique_customers']

presentation_df = presentation_df.merge(retail_agg, on='date', how='left')
print(f"OK Retail transactions aggregated and merged")

# Add Census data for overlapping period
print("\nMerging Census retail sales data...")

# Pivot Census data to have beauty and fashion as separate columns
census_pivot = census_data.pivot_table(
    index='observation_date',
    columns='NAICS  Code',
    values='sales',
    aggfunc='first'
).reset_index()
census_pivot.columns = ['date'] + [f'census_sales_naics_{int(col)}' for col in census_pivot.columns[1:]]

# Also get the CCI from census data
census_cci = census_data.groupby('observation_date')['USACSCICP02STSAM'].first().reset_index()
census_cci.columns = ['date', 'census_cci']

presentation_df = presentation_df.merge(census_pivot, on='date', how='left')
presentation_df = presentation_df.merge(census_cci, on='date', how='left')

print(f"OK Census data merged")

# Add derived metrics
print("\nCalculating derived metrics...")

# Inflation metrics
if 'cpi' in presentation_df.columns:
    base_cpi = presentation_df['cpi'].dropna().iloc[0]
    presentation_df['cpi_index'] = presentation_df['cpi'] / base_cpi
    presentation_df['inflation_rate_yoy'] = presentation_df['cpi'].pct_change(12) * 100

# Economic periods
presentation_df['year'] = presentation_df['date'].dt.year
presentation_df['month'] = presentation_df['date'].dt.month
presentation_df['quarter'] = presentation_df['date'].dt.quarter

# Recession indicators
presentation_df['is_great_recession'] = ((presentation_df['date'] >= '2007-12-01') &
                                          (presentation_df['date'] <= '2009-06-30')).astype(int)
presentation_df['is_covid_crisis'] = ((presentation_df['date'] >= '2020-02-01') &
                                       (presentation_df['date'] <= '2020-04-30')).astype(int)
presentation_df['is_inflation_surge'] = ((presentation_df['date'] >= '2022-01-01') &
                                          (presentation_df['date'] <= '2023-06-30')).astype(int)

print(f"OK Derived metrics calculated")

# ========================================================================================================
# PART 3: CREATE DATA SOURCE SUMMARY TABLE
# ========================================================================================================

print("\n" + "=" * 100)
print("PART 3: CREATING DATA SOURCE SUMMARY TABLE")
print("=" * 100)

data_sources_summary = []

# Google Trends
data_sources_summary.append({
    'Data Source': 'Google Trends',
    'Description': 'Fashion/Beauty search volumes (40 terms across 8 indicators)',
    'Time Period': f"{google_trends['date'].min().strftime('%Y-%m')} to {google_trends['date'].max().strftime('%Y-%m')}",
    'Observations': len(google_trends),
    'Variables': len([c for c in google_trends.columns if c not in ['date', 'cci']]),
    'Frequency': 'Monthly',
    'Source': 'Google Trends API',
    'Used For': 'Search behavior analysis, consumer interest patterns'
})

# CPI
data_sources_summary.append({
    'Data Source': 'Consumer Price Index (CPI)',
    'Description': 'Inflation measure (CPILFESL)',
    'Time Period': f"{cpi_data['observation_date'].min().strftime('%Y-%m')} to {cpi_data['observation_date'].max().strftime('%Y-%m')}",
    'Observations': len(cpi_data),
    'Variables': 1,
    'Frequency': 'Monthly',
    'Source': 'FRED (Federal Reserve Economic Data)',
    'Used For': 'Inflation adjustment, real value calculations'
})

# CCI
data_sources_summary.append({
    'Data Source': 'Consumer Confidence Index (CCI)',
    'Description': 'Consumer confidence measure (USACSCICP02STSAM)',
    'Time Period': f"{cci_data['observation_date'].min().strftime('%Y-%m')} to {cci_data['observation_date'].max().strftime('%Y-%m')}",
    'Observations': len(cci_data),
    'Variables': 1,
    'Frequency': 'Monthly',
    'Source': 'FRED',
    'Used For': 'Primary economic sentiment indicator, regression dependent variable'
})

# Consumer Sentiment
data_sources_summary.append({
    'Data Source': 'Consumer Sentiment Index',
    'Description': 'University of Michigan sentiment measure (UMCSENT)',
    'Time Period': f"{consumer_sentiment['observation_date'].min().strftime('%Y-%m')} to {consumer_sentiment['observation_date'].max().strftime('%Y-%m')}",
    'Observations': len(consumer_sentiment),
    'Variables': 1,
    'Frequency': 'Monthly',
    'Source': 'FRED',
    'Used For': 'Secondary validation of consumer confidence'
})

# Unemployment
data_sources_summary.append({
    'Data Source': 'Unemployment Rate',
    'Description': 'National unemployment rate (UNRATE)',
    'Time Period': f"{unemployment['observation_date'].min().strftime('%Y-%m')} to {unemployment['observation_date'].max().strftime('%Y-%m')}",
    'Observations': len(unemployment),
    'Variables': 1,
    'Frequency': 'Monthly',
    'Source': 'FRED',
    'Used For': 'Economic context, recession identification'
})

# Retail Sales
data_sources_summary.append({
    'Data Source': 'Retail Sales - Clothing',
    'Description': 'Monthly retail sales in clothing sector (MRTSSM448USN)',
    'Time Period': f"{retail_sales['observation_date'].min().strftime('%Y-%m')} to {retail_sales['observation_date'].max().strftime('%Y-%m')}",
    'Observations': len(retail_sales),
    'Variables': 1,
    'Frequency': 'Monthly',
    'Source': 'FRED',
    'Used For': 'Validation of fashion spending patterns'
})

# Saving Rate
data_sources_summary.append({
    'Data Source': 'Personal Saving Rate',
    'Description': 'Percentage of disposable income saved (PSAVERT)',
    'Time Period': f"{saving_rate['observation_date'].min().strftime('%Y-%m')} to {saving_rate['observation_date'].max().strftime('%Y-%m')}",
    'Observations': len(saving_rate),
    'Variables': 1,
    'Frequency': 'Monthly',
    'Source': 'FRED',
    'Used For': 'Economic behavior context'
})

# Retail Transactions
data_sources_summary.append({
    'Data Source': 'Retail Transactions',
    'Description': f"Individual purchase transactions ({retail_transactions['Customer ID'].nunique()} customers)",
    'Time Period': f"{retail_transactions['Transaction Date'].min().strftime('%Y-%m-%d')} to {retail_transactions['Transaction Date'].max().strftime('%Y-%m-%d')}",
    'Observations': len(retail_transactions),
    'Variables': len(retail_transactions.columns),
    'Frequency': 'Daily (transaction-level)',
    'Source': 'Retail transaction database',
    'Used For': 'Purchase behavior, price point analysis, category spending'
})

# Census Data
data_sources_summary.append({
    'Data Source': 'U.S. Census Retail Sales',
    'Description': 'Official retail sales (NAICS 446: Beauty, NAICS 44812: Women\'s Clothing)',
    'Time Period': f"{census_data['observation_date'].min().strftime('%Y-%m')} to {census_data['observation_date'].max().strftime('%Y-%m')}",
    'Observations': len(census_data),
    'Variables': len(census_data.columns),
    'Frequency': 'Monthly',
    'Source': 'U.S. Census Bureau',
    'Used For': 'Hill et al. (2012) replication, long-term purchase patterns (33 years)'
})

data_sources_df = pd.DataFrame(data_sources_summary)

print(f"\nOK Data source summary created: {len(data_sources_df)} data sources documented")

# ========================================================================================================
# PART 4: SAVE OUTPUTS
# ========================================================================================================

print("\n" + "=" * 100)
print("PART 4: SAVING PRESENTATION MATERIALS")
print("=" * 100)

import os
os.makedirs('Presentation_Data', exist_ok=True)

# Save comprehensive dataframe
presentation_df.to_csv('Presentation_Data/comprehensive_data_all_sources.csv', index=False)
print(f"\nOK Comprehensive dataframe saved: Presentation_Data/comprehensive_data_all_sources.csv")
print(f"  Dimensions: {len(presentation_df)} rows x {len(presentation_df.columns)} columns")
print(f"  Period: {presentation_df['date'].min().strftime('%Y-%m')} to {presentation_df['date'].max().strftime('%Y-%m')}")

# Save data sources summary
data_sources_df.to_csv('Presentation_Data/data_sources_summary.csv', index=False)
print(f"\nOK Data sources summary saved: Presentation_Data/data_sources_summary.csv")

# ========================================================================================================
# PART 5: CREATE DATA DISTRIBUTION VISUALIZATIONS
# ========================================================================================================

print("\n" + "=" * 100)
print("PART 5: CREATING DATA DISTRIBUTION VISUALIZATIONS")
print("=" * 100)

# Set visualization style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("plasma")

# Figure 1: Data Coverage Timeline
print("\n[1/3] Creating data coverage timeline...")
fig, ax = plt.subplots(figsize=(16, 10))

timeline_data = [
    ('Google Trends', google_trends['date'].min(), google_trends['date'].max(), '#FDE724'),
    ('CPI', cpi_data['observation_date'].min(), cpi_data['observation_date'].max(), '#B4DE2C'),
    ('CCI', cci_data['observation_date'].min(), cci_data['observation_date'].max(), '#6DCD59'),
    ('Consumer Sentiment', consumer_sentiment['observation_date'].min(), consumer_sentiment['observation_date'].max(), '#35B779'),
    ('Unemployment', unemployment['observation_date'].min(), unemployment['observation_date'].max(), '#1F9E89'),
    ('Retail Sales', retail_sales['observation_date'].min(), retail_sales['observation_date'].max(), '#26828E'),
    ('Saving Rate', saving_rate['observation_date'].min(), saving_rate['observation_date'].max(), '#31688E'),
    ('Retail Transactions', retail_transactions['Transaction Date'].min(), retail_transactions['Transaction Date'].max(), '#404788'),
    ('Census Retail Sales', census_data['observation_date'].min(), census_data['observation_date'].max(), '#481567'),
]

y_positions = range(len(timeline_data))

for i, (name, start, end, color) in enumerate(timeline_data):
    ax.barh(i, (end - start).days, left=start, height=0.6, color=color,
            edgecolor='black', linewidth=1.5, alpha=0.9)

    # Add data period labels
    duration_years = (end - start).days / 365.25
    ax.text(start + (end - start) / 2, i, f'{duration_years:.1f} years',
            ha='center', va='center', fontweight='bold', fontsize=10, color='white')

ax.set_yticks(y_positions)
ax.set_yticklabels([name for name, _, _, _ in timeline_data], fontsize=12, fontweight='bold')
ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_title('Data Coverage Timeline: All Data Sources Used in Analysis\nComprehensive View of Temporal Coverage (1957-2025)',
             fontsize=16, fontweight='bold', pad=20)

# Add recession shading
recession_periods = [
    ('Great Recession', pd.to_datetime('2007-12-01'), pd.to_datetime('2009-06-30')),
    ('COVID-19', pd.to_datetime('2020-02-01'), pd.to_datetime('2020-04-30')),
]

for period_name, start, end in recession_periods:
    ax.axvspan(start, end, alpha=0.2, color='red', zorder=0)

ax.grid(axis='x', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig('Viz/data_coverage_timeline.png', dpi=300, bbox_inches='tight', facecolor='white')
print("  OK Saved: Viz/data_coverage_timeline.png")
plt.close()

# Figure 2: Data Distribution - Key Variables
print("\n[2/3] Creating key variables distribution...")
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

# Plot distributions for key variables
key_vars = [
    ('cci', 'Consumer Confidence Index', presentation_df),
    ('unemployment_rate', 'Unemployment Rate (%)', presentation_df),
    ('cpi', 'Consumer Price Index', presentation_df),
    ('retail_sales_clothing', 'Retail Sales - Clothing ($M)', presentation_df),
    ('personal_saving_rate', 'Personal Saving Rate (%)', presentation_df),
    ('consumer_sentiment', 'Consumer Sentiment Index', presentation_df)
]

for idx, (var, label, data) in enumerate(key_vars):
    if var in data.columns:
        clean_data = data[var].dropna()

        # Histogram with KDE
        axes[idx].hist(clean_data, bins=30, alpha=0.7, color=plt.cm.plasma(idx/6),
                      edgecolor='black', linewidth=1.2)

        # Add KDE line
        from scipy.stats import gaussian_kde
        if len(clean_data) > 10:
            kde = gaussian_kde(clean_data)
            x_range = np.linspace(clean_data.min(), clean_data.max(), 200)
            kde_values = kde(x_range)
            ax2 = axes[idx].twinx()
            ax2.plot(x_range, kde_values, color='darkred', linewidth=2.5, label='Density')
            ax2.set_ylabel('Density', fontsize=10)
            ax2.set_ylim(0, kde_values.max() * 1.2)

        axes[idx].set_xlabel(label, fontsize=11, fontweight='bold')
        axes[idx].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[idx].set_title(f'Distribution: {label}\nMean: {clean_data.mean():.2f}, Std: {clean_data.std():.2f}',
                           fontsize=12, fontweight='bold')
        axes[idx].grid(alpha=0.3, linestyle='--')

plt.suptitle('Distribution of Key Economic Indicators Used in Analysis',
             fontsize=16, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig('Viz/data_distribution_key_variables.png', dpi=300, bbox_inches='tight', facecolor='white')
print("  OK Saved: Viz/data_distribution_key_variables.png")
plt.close()

# Figure 3: Data Processing Flow Diagram
print("\n[3/3] Creating data processing flow diagram...")
fig, ax = plt.subplots(figsize=(18, 14))
ax.axis('off')

# Define flow stages with colors
stages = [
    {
        'title': 'RAW DATA SOURCES',
        'items': [
            'Google Trends\n(2004-2024)\n40 search terms',
            'FRED Economic\nData\n6 indicators',
            'Retail Transactions\n10,000 purchases',
            'Census Retail\nSales\n404 months'
        ],
        'color': '#440154',
        'y_pos': 0.85
    },
    {
        'title': 'DATA CLEANING & INTEGRATION',
        'items': [
            'Date\nstandardization',
            'Missing value\nhandling',
            'Decimal correction\n(CCI)',
            'Time period\nalignment',
            'Merge on\ndate keys'
        ],
        'color': '#31688E',
        'y_pos': 0.63
    },
    {
        'title': 'FEATURE ENGINEERING',
        'items': [
            'Latent variables\n(SEM)',
            'Inflation\nadjustment',
            'Year-over-year\nrates',
            'Recession\nindicators',
            'Category\nclassification'
        ],
        'color': '#35B779',
        'y_pos': 0.41
    },
    {
        'title': 'ANALYSIS METHODS',
        'items': [
            'OLS\nRegression',
            'Correlation\nAnalysis',
            'Time Series\nAnalysis',
            'Price Point\nAnalysis',
            'Recession Period\nAnalysis'
        ],
        'color': '#B4DE2C',
        'y_pos': 0.19
    },
    {
        'title': 'OUTPUTS',
        'items': [
            'Search Behavior\nResults',
            'Purchase Behavior\nResults',
            'Census Replication\nResults',
            '9 Tableau\nExports',
            '7 Visualizations'
        ],
        'color': '#FDE724',
        'y_pos': 0.05
    }
]

box_width = 0.18
box_height = 0.15

for stage_idx, stage in enumerate(stages):
    y_center = stage['y_pos']

    # Draw stage title box
    title_box = plt.Rectangle((0.1, y_center + 0.02), 0.8, 0.05,
                               facecolor=stage['color'], edgecolor='black',
                               linewidth=2, alpha=0.9, transform=ax.transAxes)
    ax.add_patch(title_box)
    ax.text(0.5, y_center + 0.045, stage['title'],
            transform=ax.transAxes, fontsize=14, fontweight='bold',
            ha='center', va='center', color='white')

    # Draw item boxes
    num_items = len(stage['items'])
    total_width = num_items * box_width + (num_items - 1) * 0.02
    start_x = (1.0 - total_width) / 2

    for item_idx, item in enumerate(stage['items']):
        x = start_x + item_idx * (box_width + 0.02)
        item_box = plt.Rectangle((x, y_center - box_height), box_width, box_height,
                                  facecolor='white', edgecolor=stage['color'],
                                  linewidth=2.5, alpha=0.95, transform=ax.transAxes)
        ax.add_patch(item_box)
        ax.text(x + box_width/2, y_center - box_height/2, item,
                transform=ax.transAxes, fontsize=9, ha='center', va='center',
                wrap=True, fontweight='bold')

    # Draw arrows to next stage
    if stage_idx < len(stages) - 1:
        arrow_y_start = y_center - box_height - 0.01
        arrow_y_end = stages[stage_idx + 1]['y_pos'] + 0.07
        ax.annotate('', xy=(0.5, arrow_y_end), xytext=(0.5, arrow_y_start),
                   xycoords='axes fraction', textcoords='axes fraction',
                   arrowprops=dict(arrowstyle='->', lw=3, color='black'))

ax.text(0.5, 0.97, 'DATA PROCESSING PIPELINE: From Raw Data to Final Outputs',
        transform=ax.transAxes, fontsize=18, fontweight='bold', ha='center', va='top')

plt.tight_layout()
plt.savefig('Viz/data_processing_flow.png', dpi=300, bbox_inches='tight', facecolor='white')
print("  OK Saved: Viz/data_processing_flow.png")
plt.close()

# ========================================================================================================
# FINAL SUMMARY
# ========================================================================================================

print("\n" + "=" * 100)
print(" " * 30 + "PRESENTATION DATA COMPILATION COMPLETE")
print("=" * 100)

print(f"\n** COMPREHENSIVE DATAFRAME:")
print(f"  - File: Presentation_Data/comprehensive_data_all_sources.csv")
print(f"  - Dimensions: {len(presentation_df)} rows x {len(presentation_df.columns)} columns")
print(f"  - Period: {presentation_df['date'].min().strftime('%Y-%m')} to {presentation_df['date'].max().strftime('%Y-%m')}")
print(f"\n  Key columns included:")
print(f"    - Economic indicators: CCI, CPI, Unemployment, Consumer Sentiment, Saving Rate")
print(f"    - Search data: 40 Google Trends terms")
print(f"    - Purchase data: Retail transaction aggregates")
print(f"    - Census data: Beauty & fashion sales (NAICS 446, 44812)")
print(f"    - Derived: Inflation rates, recession indicators, temporal features")

print(f"\n** DATA SOURCES SUMMARY:")
print(f"  - File: Presentation_Data/data_sources_summary.csv")
print(f"  - Total sources: {len(data_sources_df)}")

print(f"\n** VISUALIZATIONS CREATED:")
print(f"  - Viz/data_coverage_timeline.png (temporal coverage of all sources)")
print(f"  - Viz/data_distribution_key_variables.png (distribution plots)")
print(f"  - Viz/data_processing_flow.png (pipeline diagram)")

print(f"\n** READY FOR PRESENTATION!")
print(f"  All data compiled and visualized for presentation slides")

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)
