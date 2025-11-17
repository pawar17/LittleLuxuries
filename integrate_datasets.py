"""
Data Integration Script for Little Luxuries Project
Integrates recession indicators analysis with other project datasets
"""

import pandas as pd
import numpy as np
from datetime import datetime

def integrate_all_datasets():
    """
    Integrate recession indicators data with other project datasets
    This creates a unified dataset for comprehensive analysis
    """
    
    print("="*60)
    print("INTEGRATING ALL DATASETS FOR LITTLE LUXURIES PROJECT")
    print("="*60)
    
    # Load recession indicators data
    print("\n1. Loading Recession Indicators Data...")
    try:
        recession_df = pd.read_csv('data_with_scores.csv')
        if 'date' in recession_df.columns:
            recession_df['date'] = pd.to_datetime(recession_df['date'], errors='coerce')
        else:
            start_date = pd.to_datetime('2004-01-01')
            recession_df['date'] = pd.date_range(start=start_date, periods=len(recession_df), freq='MS')
        print(f"   [OK] Loaded {len(recession_df)} rows from recession indicators")
    except FileNotFoundError:
        print("   ⚠ Warning: data_with_scores.csv not found. Run recession_indicators_analysis.py first.")
        return
    
    # Prepare base dataset with monthly aggregation
    base_df = recession_df[['date', 'cci']].copy()
    base_df['year'] = base_df['date'].dt.year
    base_df['month'] = base_df['date'].dt.month
    base_df['quarter'] = base_df['date'].dt.quarter
    
    # Add recession indicator scores
    indicator_cols = [col for col in recession_df.columns if col.endswith('_score')]
    for col in indicator_cols:
        base_df[col] = recession_df[col].values
    
    # ========================================================================
    # 2. Add feature engineering matching project proposal
    # ========================================================================
    print("\n2. Feature Engineering...")
    
    # Calculate "Luxury Ratio" - normalized sum of all trend scores
    if indicator_cols:
        base_df['luxury_ratio'] = base_df[indicator_cols].sum(axis=1)
        # Normalize to 0-1 scale
        base_df['luxury_ratio'] = (base_df['luxury_ratio'] - base_df['luxury_ratio'].min()) / \
                                  (base_df['luxury_ratio'].max() - base_df['luxury_ratio'].min())
    
    # Calculate "Category Concentration" - variance in trend scores
    if indicator_cols:
        base_df['category_concentration'] = base_df[indicator_cols].std(axis=1)
    
    # Create "Affordability Index" - inverse relationship with CCI
    # Lower CCI = higher affordability index (people seek affordable luxuries)
    base_df['affordability_index'] = 100 - base_df['cci']
    base_df['affordability_index'] = (base_df['affordability_index'] - base_df['affordability_index'].min()) / \
                                     (base_df['affordability_index'].max() - base_df['affordability_index'].min()) * 100
    
    # Economic period categorization
    base_df['economic_period'] = base_df['date'].apply(categorize_economic_period)
    
    # Recession indicator (binary)
    base_df['is_recession'] = base_df['economic_period'].str.contains('Recession|Pandemic|Inflation', case=False, na=False)
    
    print("   [OK] Created luxury_ratio, category_concentration, affordability_index")
    
    # ========================================================================
    # 3. Prepare for integration with other datasets
    # ========================================================================
    print("\n3. Preparing Integration Template...")
    
    # Create integration template with common keys
    integration_template = base_df.copy()
    
    # Add placeholder columns for other datasets
    integration_template['retail_sales_clothing'] = np.nan
    integration_template['ecommerce_transactions'] = np.nan
    integration_template['beauty_sales'] = np.nan
    integration_template['accessories_sales'] = np.nan
    integration_template['fashion_sales'] = np.nan
    
    # Save integration template
    integration_template.to_csv('integrated_dataset_template.csv', index=False)
    print(f"   [OK] Saved: integrated_dataset_template.csv ({len(integration_template)} rows)")
    print("   -> Use this template to merge with your retail sales and e-commerce datasets")
    
    # ========================================================================
    # 4. Create category-level summary
    # ========================================================================
    print("\n4. Creating Category-Level Summary...")
    
    # Load results
    try:
        results = pd.read_csv('recession_indicators_results.csv')
        
        # Create category mapping
        category_mapping = {
            'indiesleaze': {'category': 'Fashion Trends', 'subcategory': 'Indie Sleaze'},
            'lipstickindex': {'category': 'Beauty & Cosmetics', 'subcategory': 'Lipstick Index'},
            'maxiskirt': {'category': 'Fashion Trends', 'subcategory': 'Maxi Skirt'},
            'bigbag': {'category': 'Accessories', 'subcategory': 'Big Bag'},
            'highheelindex': {'category': 'Accessories', 'subcategory': 'High Heel Index'},
            'peplums': {'category': 'Fashion Trends', 'subcategory': 'Peplums'},
            'blazers': {'category': 'Fashion Trends', 'subcategory': 'Blazers'},
            'mini': {'category': 'Fashion Trends', 'subcategory': 'Mini Skirts'}
        }
        
        category_summary = results.copy()
        category_summary['category'] = category_summary['Indicator'].map(
            lambda x: category_mapping.get(x, {}).get('category', 'Other')
        )
        category_summary['subcategory'] = category_summary['Indicator'].map(
            lambda x: category_mapping.get(x, {}).get('subcategory', 'Other')
        )
        
        category_summary.to_csv('category_summary.csv', index=False)
        print(f"   [OK] Saved: category_summary.csv")
        
    except FileNotFoundError:
        print("   ⚠ Warning: recession_indicators_results.csv not found")
    
    # ========================================================================
    # 5. Create instructions for dataset integration
    # ========================================================================
    print("\n5. Creating Integration Instructions...")
    
    instructions = """
# DATASET INTEGRATION INSTRUCTIONS
# =================================

## Files Ready for Integration:
1. integrated_dataset_template.csv - Base dataset with recession indicators and CCI
2. tableau_temporal_trends.csv - Formatted for Temporal Trends Dashboard
3. tableau_category_comparison.csv - Formatted for Category Comparison Dashboard
4. tableau_correlation_explorer.csv - Formatted for Correlation Explorer Dashboard

## Integration Steps:

### Step 1: Load Your Retail Sales Data
```python
retail_sales = pd.read_csv('your_retail_sales_data.csv')
# Ensure you have: date, category, sales_amount columns
```

### Step 2: Aggregate to Monthly Level
```python
retail_sales['date'] = pd.to_datetime(retail_sales['date'])
retail_monthly = retail_sales.groupby(['date', 'category']).agg({
    'sales_amount': 'sum',
    'transaction_count': 'count'
}).reset_index()
```

### Step 3: Merge with Base Dataset
```python
base = pd.read_csv('integrated_dataset_template.csv')
base['date'] = pd.to_datetime(base['date'])

# Merge on date
merged = base.merge(
    retail_monthly,
    on='date',
    how='left'
)
```

### Step 4: Calculate Luxury Metrics
```python
# Luxury Ratio: non-essential spending / total spending
merged['luxury_ratio'] = merged['beauty_sales'] + merged['accessories_sales'] / \
                         (merged['total_sales'] + 1)

# Category Concentration: how spending clusters
merged['category_concentration'] = merged[['beauty_sales', 'fashion_sales', 
                                           'accessories_sales']].std(axis=1)
```

### Step 5: Export for Tableau
```python
merged.to_csv('final_integrated_dataset.csv', index=False)
```

## Key Variables to Include:
- date (monthly)
- cci (Consumer Confidence Index)
- indicator scores (indiesleaze_score, lipstickindex_score, etc.)
- retail_sales_clothing
- ecommerce_transactions
- category-level sales (beauty, fashion, accessories)
- luxury_ratio
- affordability_index
- category_concentration
- economic_period

## Tableau Calculated Fields to Create:
1. Luxury Ratio: SUM([beauty_sales] + [accessories_sales]) / SUM([total_sales])
2. Affordability Index: 100 - [CCI]
3. Category Concentration: STDEV([beauty_sales], [fashion_sales], [accessories_sales])
4. Trend Score Normalized: ([trend_score] - MIN([trend_score])) / (MAX([trend_score]) - MIN([trend_score]))
"""
    
    with open('INTEGRATION_INSTRUCTIONS.md', 'w') as f:
        f.write(instructions)
    
    print("   [OK] Saved: INTEGRATION_INSTRUCTIONS.md")
    
    print("\n" + "="*60)
    print("INTEGRATION PREPARATION COMPLETE!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Load your retail sales and e-commerce datasets")
    print("2. Follow INTEGRATION_INSTRUCTIONS.md to merge datasets")
    print("3. Import integrated data into Tableau")
    print("4. Use tableau_*.csv files for individual dashboard views")

def categorize_economic_period(date):
    """Categorize dates into economic periods"""
    if pd.isna(date):
        return 'Unknown'
    
    year = date.year
    month = date.month
    
    if (year == 2008 and month >= 9) or (year == 2009) or (year == 2010 and month <= 6):
        return 'Great Recession (2008-2010)'
    if (year == 2020 and month >= 3) or (year == 2021 and month <= 6):
        return 'COVID-19 Pandemic (2020-2021)'
    if (year == 2021 and month >= 7) or (year == 2022):
        return 'Post-COVID Recovery (2021-2022)'
    if year == 2023 or (year == 2024 and month <= 6):
        return 'Inflation Period (2023-2024)'
    if year < 2008:
        return 'Pre-Recession (2004-2007)'
    if 2010 < year < 2020:
        return 'Recovery Period (2011-2019)'
    return 'Recent (2024-2025)'

if __name__ == "__main__":
    integrate_all_datasets()

