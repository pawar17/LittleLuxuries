import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load the census timeseries data (1992-2025)
df = pd.read_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Tableau_Data\tableau_census_timeseries.csv')
df['observation_date'] = pd.to_datetime(df['observation_date'])

print("=== Census Data Significance Matrix (1992-2025) ===\n")
print(f"Total observations: {len(df)}")
print(f"Date range: {df['observation_date'].min()} to {df['observation_date'].max()}")
print(f"Categories: {df['category'].unique().tolist()}\n")

# Pivot data to have separate columns for Beauty and Fashion sales
df_pivot = df.pivot(index='observation_date', columns='category', values='sales').reset_index()
df_pivot.columns = ['observation_date', 'beauty_sales', 'fashion_sales']

# Merge back with economic indicators (they're the same for both categories)
df_econ = df[df['category'] == 'Beauty & Personal Care'][['observation_date', 'cci', 'cpi']].copy()
df_final = df_pivot.merge(df_econ, on='observation_date', how='left')

# Drop any rows with missing values
df_final = df_final.dropna()

print(f"Complete observations after merging: {len(df_final)}\n")

# Calculate additional economic indicators
# Year-over-year inflation rate
df_final['inflation_yoy'] = df_final['cpi'].pct_change(12) * 100

# Growth rates for sales
df_final['beauty_growth'] = df_final['beauty_sales'].pct_change(12) * 100
df_final['fashion_growth'] = df_final['fashion_sales'].pct_change(12) * 100

# Remove NaN values created by pct_change(12)
df_final = df_final.dropna()

print(f"Observations after calculating growth rates: {len(df_final)}\n")

# Define variables for analysis
fashion_variables = [
    'beauty_sales',
    'fashion_sales',
    'beauty_growth',
    'fashion_growth'
]

economic_variables = [
    'cci',
    'cpi',
    'inflation_yoy'
]

# Calculate correlation and p-value matrices
correlation_matrix = pd.DataFrame(index=fashion_variables, columns=economic_variables)
p_value_matrix = pd.DataFrame(index=fashion_variables, columns=economic_variables)

print("Calculating correlations and p-values...\n")
for fashion_var in fashion_variables:
    for econ_var in economic_variables:
        corr, p_value = stats.pearsonr(df_final[fashion_var], df_final[econ_var])
        correlation_matrix.loc[fashion_var, econ_var] = corr
        p_value_matrix.loc[fashion_var, econ_var] = p_value

# Convert to float
correlation_matrix = correlation_matrix.astype(float)
p_value_matrix = p_value_matrix.astype(float)

# Create binary significance matrix (1 = significant at p < 0.05, 0 = not significant)
binary_significance = (p_value_matrix < 0.05).astype(int)

print("=== Correlation Matrix ===")
print(correlation_matrix.round(3))
print()

print("=== P-Value Matrix ===")
print(p_value_matrix.round(6))
print()

print("=== Binary Significance Matrix ===")
print("1 = Significant (p < 0.05), 0 = Not Significant (p >= 0.05)")
print(binary_significance)
print()

# Count statistics
total_tests = len(fashion_variables) * len(economic_variables)
significant = binary_significance.sum().sum()
not_significant = total_tests - significant

print(f"Total correlations tested: {total_tests}")
print(f"Significant (p < 0.05): {significant} ({significant/total_tests*100:.1f}%)")
print(f"Not significant: {not_significant} ({not_significant/total_tests*100:.1f}%)")
print()

# Create readable labels
fashion_labels = {
    'beauty_sales': 'Beauty Sales',
    'fashion_sales': 'Fashion Sales',
    'beauty_growth': 'Beauty Growth (YoY%)',
    'fashion_growth': 'Fashion Growth (YoY%)'
}

economic_labels = {
    'cci': 'Consumer Confidence Index',
    'cpi': 'Consumer Price Index',
    'inflation_yoy': 'Inflation Rate (YoY%)'
}

fashion_display = [fashion_labels[var] for var in fashion_variables]
economic_display = [economic_labels[var] for var in economic_variables]

# Create visualization with pink-purple color scheme
fig, ax = plt.subplots(figsize=(10, 8))

# Custom pink-purple colormap
colors = ['#F0E6F6', '#8B5FBF']  # Light pink-purple (0) to dark purple (1)
cmap = sns.blend_palette(colors, as_cmap=True)

# Create heatmap
sns.heatmap(binary_significance, annot=True, fmt='d', cmap=cmap,
            vmin=0, vmax=1, cbar_kws={'label': 'Significance', 'ticks': [0, 1]},
            xticklabels=economic_display, yticklabels=fashion_display,
            linewidths=2, linecolor='white', ax=ax,
            annot_kws={'fontsize': 16, 'fontweight': 'bold'})

# Customize colorbar
cbar = ax.collections[0].colorbar
cbar.set_ticks([0.25, 0.75])
cbar.set_ticklabels(['Not Significant\n(p ≥ 0.05)', 'Significant\n(p < 0.05)'])

ax.set_title('Statistical Significance Matrix: Fashion/Beauty vs Economic Indicators\nCensus Retail Sales Data (1992-2025)\n1 = Significant (p < 0.05), 0 = Not Significant',
             fontsize=15, fontweight='bold', pad=20)
ax.set_xlabel('Economic Indicators', fontsize=13, fontweight='bold')
ax.set_ylabel('Fashion & Beauty Variables', fontsize=13, fontweight='bold')

plt.xticks(rotation=45, ha='right', fontsize=11)
plt.yticks(rotation=0, fontsize=11)
plt.tight_layout()

# Save figure
output_path = r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Viz\census_binary_significance_matrix.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Binary significance matrix saved to: {output_path}")

plt.close('all')

# Save matrices to CSV
binary_significance.to_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\census_binary_significance_matrix.csv')
correlation_matrix.to_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\census_correlation_matrix.csv')
p_value_matrix.to_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\census_pvalue_matrix.csv')

print("Matrices saved to Processed_Data/")
print()

# Print detailed results
print("=== Detailed Results ===\n")
for fashion_var in fashion_variables:
    fashion_label = fashion_labels[fashion_var]
    print(f"\n{fashion_label}:")
    for econ_var in economic_variables:
        econ_label = economic_labels[econ_var]
        corr = correlation_matrix.loc[fashion_var, econ_var]
        p_val = p_value_matrix.loc[fashion_var, econ_var]
        sig = "SIGNIFICANT" if binary_significance.loc[fashion_var, econ_var] == 1 else "Not significant"

        # Interpret correlation strength
        if abs(corr) > 0.7:
            strength = "very strong"
        elif abs(corr) > 0.5:
            strength = "strong"
        elif abs(corr) > 0.3:
            strength = "moderate"
        else:
            strength = "weak"

        direction = "positive" if corr > 0 else "negative"

        print(f"  vs {econ_label}: r={corr:.3f} (p={p_val:.6f}) - {sig}")
        print(f"     [{strength} {direction} correlation]")

print("\n=== Analysis Complete ===")
