import pandas as pd
import numpy as np

# Load the search results data
search_results = pd.read_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Tableau_Data\tableau_search_results.csv')

print("=== Creating Enhanced Search Indicator Ranking for Tableau ===\n")

# Create rankings based on different metrics
search_results['Rank_by_R2'] = search_results['R²'].rank(ascending=False, method='min').astype(int)
search_results['Rank_by_Coefficient'] = search_results['Coefficient'].abs().rank(ascending=False, method='min').astype(int)
search_results['Rank_by_Pvalue'] = search_results['P-value'].rank(ascending=True, method='min').astype(int)
search_results['Rank_by_Fscore'] = search_results['F-statistic'].rank(ascending=False, method='min').astype(int)

# Calculate composite score (weighted average of rankings)
# Lower rank number = better
weights = {
    'R2': 0.4,          # Explanatory power is most important
    'Pvalue': 0.3,      # Statistical significance
    'Fscore': 0.2,      # Overall model fit
    'Coefficient': 0.1  # Effect size
}

search_results['Composite_Score'] = (
    search_results['Rank_by_R2'] * weights['R2'] +
    search_results['Rank_by_Pvalue'] * weights['Pvalue'] +
    search_results['Rank_by_Fscore'] * weights['Fscore'] +
    search_results['Rank_by_Coefficient'] * weights['Coefficient']
)

search_results['Overall_Rank'] = search_results['Composite_Score'].rank(ascending=True, method='min').astype(int)

# Add tier classification
def classify_tier(row):
    if row['Overall_Rank'] <= 3:
        return 'Tier 1: Strong Indicators'
    elif row['Overall_Rank'] <= 5:
        return 'Tier 2: Moderate Indicators'
    else:
        return 'Tier 3: Weak Indicators'

search_results['Tier'] = search_results.apply(classify_tier, axis=1)

# Add significance level
def significance_level(p_value):
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return 'ns'

search_results['Significance_Level'] = search_results['P-value'].apply(significance_level)

# Add interpretation fields
def interpret_r2(r2):
    if r2 >= 0.15:
        return 'High Explanatory Power'
    elif r2 >= 0.10:
        return 'Moderate Explanatory Power'
    elif r2 >= 0.05:
        return 'Low Explanatory Power'
    else:
        return 'Very Low Explanatory Power'

search_results['R2_Interpretation'] = search_results['R²'].apply(interpret_r2)

# Add percentage versions for better Tableau display
search_results['R2_Percent'] = search_results['R²'] * 100
search_results['Adj_R2_Percent'] = search_results['Adj_R²'] * 100

# Reorder columns for better Tableau experience
columns_order = [
    'Overall_Rank',
    'Indicator',
    'Category',
    'Data_Type',
    'Tier',
    'Significant',
    'Significance_Level',
    'R²',
    'R2_Percent',
    'Adj_R²',
    'Adj_R2_Percent',
    'R2_Interpretation',
    'Coefficient',
    'P-value',
    'F-statistic',
    'Std_Error',
    'Rank_by_R2',
    'Rank_by_Coefficient',
    'Rank_by_Pvalue',
    'Rank_by_Fscore',
    'Composite_Score'
]

search_ranking = search_results[columns_order].copy()

# Sort by overall rank
search_ranking = search_ranking.sort_values('Overall_Rank')

# Display results
print(search_ranking[['Overall_Rank', 'Indicator', 'Category', 'Tier', 'R2_Percent', 'Significance_Level']])
print()

# Save to CSV
output_path = r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Tableau_Data\tableau_search_indicators_ranking.csv'
search_ranking.to_csv(output_path, index=False)
print(f"Search indicators ranking saved to: {output_path}")

# Create a summary table
print("\n=== Summary by Tier ===")
tier_summary = search_ranking.groupby('Tier').agg({
    'Indicator': 'count',
    'R2_Percent': 'mean',
    'P-value': 'mean'
}).round(3)
tier_summary.columns = ['Count', 'Avg R² %', 'Avg P-value']
print(tier_summary)

print("\n=== Summary by Category ===")
category_summary = search_ranking.groupby('Category').agg({
    'Indicator': 'count',
    'R2_Percent': 'mean',
    'Overall_Rank': 'mean'
}).round(2)
category_summary.columns = ['Count', 'Avg R² %', 'Avg Overall Rank']
print(category_summary)

print("\n=== Top 5 Indicators ===")
top5 = search_ranking.head(5)[['Overall_Rank', 'Indicator', 'Category', 'R2_Percent', 'Coefficient', 'P-value']]
print(top5.to_string(index=False))

print("\n=== Analysis Complete ===")
