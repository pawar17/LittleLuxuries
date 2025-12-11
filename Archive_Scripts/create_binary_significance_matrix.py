import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load the data
df = pd.read_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\master_dataset_complete.csv')
df['date'] = pd.to_datetime(df['date'])

print("=== Binary Significance Matrix (1 = Significant, 0 = Not Significant) ===\n")

# Define fashion indicators
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
    'cci',
    'cpi',
    'inflation_rate_yoy',
    'consumer_sentiment',
    'unemployment_rate',
    'retail_sales_clothing',
    'retail_sales_real',
    'personal_saving_rate'
]

# Drop rows with missing data
df_corr = df[fashion_indicators + economic_indicators].dropna()
print(f"Using {len(df_corr)} complete observations\n")

# Calculate correlation and p-value matrices
correlation_matrix = pd.DataFrame(index=fashion_indicators, columns=economic_indicators)
p_value_matrix = pd.DataFrame(index=fashion_indicators, columns=economic_indicators)

for fashion_var in fashion_indicators:
    for econ_var in economic_indicators:
        corr, p_value = stats.pearsonr(df_corr[fashion_var], df_corr[econ_var])
        correlation_matrix.loc[fashion_var, econ_var] = corr
        p_value_matrix.loc[fashion_var, econ_var] = p_value

# Convert to float
correlation_matrix = correlation_matrix.astype(float)
p_value_matrix = p_value_matrix.astype(float)

# Create binary significance matrix (1 = significant at p < 0.05, 0 = not significant)
binary_significance = (p_value_matrix < 0.05).astype(int)

print("=== Binary Significance Matrix ===")
print("1 = Significant (p < 0.05), 0 = Not Significant (p >= 0.05)")
print(binary_significance)
print()

# Count statistics
total_tests = len(fashion_indicators) * len(economic_indicators)
significant = binary_significance.sum().sum()
not_significant = total_tests - significant

print(f"Total correlations tested: {total_tests}")
print(f"Significant (p < 0.05): {significant} ({significant/total_tests*100:.1f}%)")
print(f"Not significant: {not_significant} ({not_significant/total_tests*100:.1f}%)")
print()

# Create labels
fashion_labels = [label.replace('_score', '').replace('_', ' ') for label in fashion_indicators]
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
economic_labels = [econ_label_mapping[col] for col in economic_indicators]

# Create visualization with pink-purple color scheme
fig, ax = plt.subplots(figsize=(12, 10))

# Custom pink-purple colormap
colors = ['#F0E6F6', '#8B5FBF']  # Light pink-purple (0) to dark purple (1)
cmap = sns.blend_palette(colors, as_cmap=True)

# Create heatmap
sns.heatmap(binary_significance, annot=True, fmt='d', cmap=cmap,
            vmin=0, vmax=1, cbar_kws={'label': 'Significance', 'ticks': [0, 1]},
            xticklabels=economic_labels, yticklabels=fashion_labels,
            linewidths=2, linecolor='white', ax=ax,
            annot_kws={'fontsize': 14, 'fontweight': 'bold'})

# Customize colorbar
cbar = ax.collections[0].colorbar
cbar.set_ticks([0.25, 0.75])
cbar.set_ticklabels(['Not Significant\n(p ≥ 0.05)', 'Significant\n(p < 0.05)'])

ax.set_title('Statistical Significance Matrix: Fashion vs Economic Indicators\n1 = Significant (p < 0.05), 0 = Not Significant\n(N=240 observations, 2004-2024)',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Economic Indicators', fontsize=13, fontweight='bold')
ax.set_ylabel('Fashion Indicators', fontsize=13, fontweight='bold')

plt.xticks(rotation=45, ha='right', fontsize=11)
plt.yticks(rotation=0, fontsize=11)
plt.tight_layout()

# Save figure
output_path = r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Viz\binary_significance_matrix.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Binary significance matrix saved to: {output_path}")

plt.close('all')

# Save binary matrix to CSV
binary_significance.to_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\binary_significance_matrix.csv')
print("Binary significance matrix saved to: Processed_Data/binary_significance_matrix.csv")

# Print detailed breakdown
print("\n=== Detailed Breakdown by Fashion Indicator ===")
for i, fashion_var in enumerate(fashion_indicators):
    fashion_label = fashion_labels[i]
    sig_count = binary_significance.loc[fashion_var].sum()
    print(f"{fashion_label}: {sig_count}/{len(economic_indicators)} significant correlations")

print("\n=== Detailed Breakdown by Economic Indicator ===")
for j, econ_var in enumerate(economic_indicators):
    econ_label = economic_labels[j]
    sig_count = binary_significance[econ_var].sum()
    print(f"{econ_label}: {sig_count}/{len(fashion_indicators)} significant correlations")

print("\n=== Analysis Complete ===")
