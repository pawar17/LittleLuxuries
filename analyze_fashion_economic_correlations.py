import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

pink_navy_grey_colors = [
    "#f4c3d7",
    "#e89bbd",
    "#d76e9b",
    "#b7548e",
    "#8b4c7c",
    "#6d3e6f",
    "#4e2f63",
    "#2e1d45",
    "#1a0f2b"
]

pink_navy_grey_cmap = LinearSegmentedColormap.from_list(
    "pink_navy_grey", pink_navy_grey_colors
)

# Load the data
df = pd.read_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\master_dataset_complete.csv')
df['date'] = pd.to_datetime(df['date'])

print("=== Fashion vs Economic Indicators Correlation Analysis ===\n")

# Define fashion indicators (standardized scores)
fashion_indicators = [
    'Indie Sleaze_score',
    'Lipstick Index_score',
    'Maxi Skirt_score',
    'Big Bag_score',
    'High Heel Index_score',
    'Peplums_score',
    'Blazers_score',
    'Mini Skirts_score'
]

# Define economic indicators
economic_indicators = [
    'cci',  # Consumer Confidence Index
    'cpi',  # Consumer Price Index
    'inflation_rate_yoy',  # Year-over-year inflation rate
    'consumer_sentiment',  # Consumer Sentiment
    'unemployment_rate',  # Unemployment Rate
    'retail_sales_clothing',  # Retail Sales - Clothing
    'retail_sales_real',  # Real Retail Sales
    'personal_saving_rate'  # Personal Saving Rate
]

# Filter out inflation_rate_yoy if it has too many NaN values
available_economic = [col for col in economic_indicators if col in df.columns]
print(f"Available economic indicators: {available_economic}\n")

# Check for missing values
print("Missing values check:")
for indicator in available_economic:
    missing_pct = (df[indicator].isna().sum() / len(df)) * 100
    print(f"  {indicator}: {missing_pct:.1f}% missing")
print()

# Create correlation matrix between fashion and economic indicators
# Only use rows where we have data for inflation_rate_yoy if it exists
if 'inflation_rate_yoy' in available_economic:
    df_corr = df[fashion_indicators + available_economic].dropna()
    print(f"Using {len(df_corr)} rows with complete data (out of {len(df)} total)")
else:
    df_corr = df[fashion_indicators + available_economic]

correlation_matrix = df_corr[fashion_indicators].corrwith(df_corr[available_economic])
correlation_df = pd.DataFrame(correlation_matrix).T

# Create full correlation matrix for heatmap
full_corr_matrix = df_corr[fashion_indicators + available_economic].corr()
fashion_econ_corr = full_corr_matrix.loc[fashion_indicators, available_economic]

print("\n=== Correlation Matrix: Fashion Indicators vs Economic Indicators ===")
print(fashion_econ_corr.round(3))
print()

# Find strongest correlations
print("\n=== Top 10 Strongest Correlations (by absolute value) ===")
correlations_flat = []
for fashion_var in fashion_indicators:
    for econ_var in available_economic:
        corr_value = fashion_econ_corr.loc[fashion_var, econ_var]
        if not pd.isna(corr_value):
            correlations_flat.append({
                'Fashion Indicator': fashion_var,
                'Economic Indicator': econ_var,
                'Correlation': corr_value,
                'Abs_Correlation': abs(corr_value)
            })

correlations_flat_df = pd.DataFrame(correlations_flat)
correlations_flat_df = correlations_flat_df.sort_values('Abs_Correlation', ascending=False)
print(correlations_flat_df.head(10).to_string(index=False))
print()

# Summary statistics by indicator
print("\n=== Summary: Average Correlation with Economic Indicators (by Fashion Indicator) ===")
avg_corr_by_fashion = fashion_econ_corr.abs().mean(axis=1).sort_values(ascending=False)
for indicator, avg_corr in avg_corr_by_fashion.items():
    print(f"  {indicator}: {avg_corr:.3f}")
print()

print("\n=== Summary: Average Correlation with Fashion Indicators (by Economic Indicator) ===")
avg_corr_by_econ = fashion_econ_corr.abs().mean(axis=0).sort_values(ascending=False)
for indicator, avg_corr in avg_corr_by_econ.items():
    print(f"  {indicator}: {avg_corr:.3f}")
print()

# Create heatmap visualization
fig, ax = plt.subplots(figsize=(12, 10))

# Create custom labels for better readability
fashion_labels = [label.replace('_score', '').replace('_', ' ') for label in fashion_indicators]
economic_labels = [
    'Consumer Confidence',
    'CPI',
    'Inflation Rate',
    'Consumer Sentiment',
    'Unemployment',
    'Retail Sales (Clothing)',
    'Real Retail Sales',
    'Personal Saving Rate'
][:len(available_economic)]

# Adjust labels based on available indicators
econ_label_mapping = {
    'cci': 'Consumer Confidence',
    'cpi': 'CPI',
    'inflation_rate_yoy': 'Inflation Rate (YoY)',
    'consumer_sentiment': 'Consumer Sentiment',
    'unemployment_rate': 'Unemployment Rate',
    'retail_sales_clothing': 'Retail Sales (Clothing)',
    'retail_sales_real': 'Real Retail Sales',
    'personal_saving_rate': 'Personal Saving Rate'
}
economic_labels = [econ_label_mapping[col] for col in available_economic]

# Create heatmap
sns.heatmap(fashion_econ_corr, annot=True, fmt='.3f', cmap=pink_navy_grey_cmap, center=0,
            vmin=-1, vmax=1, cbar_kws={'label': 'Correlation Coefficient'},
            xticklabels=economic_labels, yticklabels=fashion_labels,
            linewidths=0.5, linecolor='gray', ax=ax)

ax.set_title('Correlation Heatmap: Fashion Indicators vs Economic Indicators\n(2004-2024)',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Economic Indicators', fontsize=12, fontweight='bold')
ax.set_ylabel('Fashion Indicators', fontsize=12, fontweight='bold')

plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

# Save heatmap
heatmap_path = r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Viz\fashion_economic_correlation_heatmap.png'
plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
print(f"\nHeatmap saved to: {heatmap_path}")

# Create a second visualization: Top correlations bar chart
fig2, ax2 = plt.subplots(figsize=(14, 8))

top_20 = correlations_flat_df.head(20).copy()
top_20['Label'] = top_20['Fashion Indicator'].str.replace('_score', '').str.replace('_', ' ') + '\nvs\n' + top_20['Economic Indicator'].map(econ_label_mapping)
top_20['Color'] = top_20['Correlation'].apply(lambda x: '#E94B3C' if x < 0 else '#6C63FF')

bars = ax2.barh(range(len(top_20)), top_20['Correlation'], color=top_20['Color'], alpha=0.7)
ax2.set_yticks(range(len(top_20)))
ax2.set_yticklabels(top_20['Label'], fontsize=9)
ax2.set_xlabel('Correlation Coefficient', fontsize=12, fontweight='bold')
ax2.set_title('Top 20 Strongest Correlations: Fashion vs Economic Indicators',
              fontsize=14, fontweight='bold', pad=20)
ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='x')

# Add value labels on bars
for i, (idx, row) in enumerate(top_20.iterrows()):
    value = row['Correlation']
    x_pos = value + (0.02 if value > 0 else -0.02)
    ha = 'left' if value > 0 else 'right'
    ax2.text(x_pos, i, f'{value:.3f}', va='center', ha=ha, fontsize=8, fontweight='bold')

plt.tight_layout()

# Save bar chart
barchart_path = r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Viz\fashion_economic_top_correlations.png'
plt.savefig(barchart_path, dpi=300, bbox_inches='tight')
print(f"Bar chart saved to: {barchart_path}")

# Close all figures to avoid blocking
plt.close('all')

# Save detailed correlation table to CSV
output_csv = r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\fashion_economic_correlations.csv'
fashion_econ_corr.to_csv(output_csv)
print(f"Detailed correlation table saved to: {output_csv}")

print("\n=== Analysis Complete ===")
