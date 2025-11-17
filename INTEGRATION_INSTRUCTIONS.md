
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
merged['luxury_ratio'] = merged['beauty_sales'] + merged['accessories_sales'] /                          (merged['total_sales'] + 1)

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
