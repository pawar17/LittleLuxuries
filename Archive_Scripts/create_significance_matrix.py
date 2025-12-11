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

print("=== Statistical Significance Analysis ===\n")

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
    'cci',
    'cpi',
    'inflation_rate_yoy',
    'consumer_sentiment',
    'unemployment_rate',
    'retail_sales_clothing',
    'retail_sales_real',
    'personal_saving_rate'
]

# Drop rows with missing inflation_rate_yoy
df_corr = df[fashion_indicators + economic_indicators].dropna()
print(f"Using {len(df_corr)} complete observations\n")

# Calculate correlation matrix
correlation_matrix = df_corr[fashion_indicators].corrwith(df_corr[economic_indicators])
fashion_econ_corr = df_corr[fashion_indicators + economic_indicators].corr()
fashion_econ_corr = fashion_econ_corr.loc[fashion_indicators, economic_indicators]

# Calculate p-values for each correlation
p_value_matrix = pd.DataFrame(index=fashion_indicators, columns=economic_indicators)

print("Calculating p-values for each correlation...\n")
for fashion_var in fashion_indicators:
    for econ_var in economic_indicators:
        # Calculate Pearson correlation and p-value
        corr, p_value = stats.pearsonr(df_corr[fashion_var], df_corr[econ_var])
        p_value_matrix.loc[fashion_var, econ_var] = p_value

# Convert p-values to float
p_value_matrix = p_value_matrix.astype(float)

# Create significance levels
# *** p < 0.001, ** p < 0.01, * p < 0.05, . p < 0.1
significance_matrix = pd.DataFrame(index=fashion_indicators, columns=economic_indicators, dtype=str)
for fashion_var in fashion_indicators:
    for econ_var in economic_indicators:
        p_val = p_value_matrix.loc[fashion_var, econ_var]
        if p_val < 0.001:
            significance_matrix.loc[fashion_var, econ_var] = '***'
        elif p_val < 0.01:
            significance_matrix.loc[fashion_var, econ_var] = '**'
        elif p_val < 0.05:
            significance_matrix.loc[fashion_var, econ_var] = '*'
        elif p_val < 0.1:
            significance_matrix.loc[fashion_var, econ_var] = '.'
        else:
            significance_matrix.loc[fashion_var, econ_var] = 'ns'

# Print summary
print("=== P-Value Matrix ===")
print(p_value_matrix.round(6))
print("\n")

print("=== Significance Matrix ===")
print("Legend: *** p<0.001, ** p<0.01, * p<0.05, . p<0.1, ns = not significant")
print(significance_matrix)
print("\n")

# Count significant correlations
total_tests = len(fashion_indicators) * len(economic_indicators)
sig_001 = (p_value_matrix < 0.001).sum().sum()
sig_01 = ((p_value_matrix >= 0.001) & (p_value_matrix < 0.01)).sum().sum()
sig_05 = ((p_value_matrix >= 0.01) & (p_value_matrix < 0.05)).sum().sum()
sig_10 = ((p_value_matrix >= 0.05) & (p_value_matrix < 0.1)).sum().sum()
not_sig = (p_value_matrix >= 0.1).sum().sum()

print(f"=== Summary of Statistical Significance ===")
print(f"Total correlations tested: {total_tests}")
print(f"p < 0.001 (***): {sig_001} ({sig_001/total_tests*100:.1f}%)")
print(f"p < 0.01  (**):  {sig_01} ({sig_01/total_tests*100:.1f}%)")
print(f"p < 0.05  (*):   {sig_05} ({sig_05/total_tests*100:.1f}%)")
print(f"p < 0.10  (.):   {sig_10} ({sig_10/total_tests*100:.1f}%)")
print(f"Not significant: {not_sig} ({not_sig/total_tests*100:.1f}%)")
print()

# Create labels with better names
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

# Create combined visualization with correlation values and significance stars
fig, axes = plt.subplots(1, 2, figsize=(20, 10))

# Left panel: Correlation heatmap with significance annotations
ax1 = axes[0]
sns.heatmap(fashion_econ_corr, annot=False, fmt='.3f', cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, cbar_kws={'label': 'Correlation Coefficient'},
            xticklabels=economic_labels, yticklabels=fashion_labels,
            linewidths=0.5, linecolor='gray', ax=ax1)

# Add correlation values with significance stars
for i, fashion_var in enumerate(fashion_indicators):
    for j, econ_var in enumerate(economic_indicators):
        corr_val = fashion_econ_corr.loc[fashion_var, econ_var]
        sig_stars = significance_matrix.loc[fashion_var, econ_var]

        # Choose text color based on background
        text_color = 'white' if abs(corr_val) > 0.5 else 'black'

        # Format annotation
        if sig_stars == 'ns':
            annotation = f'{corr_val:.3f}'
        else:
            annotation = f'{corr_val:.3f}\n{sig_stars}'

        ax1.text(j + 0.5, i + 0.5, annotation,
                ha='center', va='center', color=text_color, fontsize=9, fontweight='bold')

ax1.set_title('Correlation Heatmap with Statistical Significance',
              fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Economic Indicators', fontsize=12, fontweight='bold')
ax1.set_ylabel('Fashion Indicators', fontsize=12, fontweight='bold')
plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
plt.setp(ax1.get_yticklabels(), rotation=0)

# Right panel: P-value heatmap
ax2 = axes[1]

# Use log scale for p-values for better visualization
log_p_values = -np.log10(p_value_matrix.astype(float))
log_p_values = log_p_values.replace([np.inf, -np.inf], np.nan)

sns.heatmap(log_p_values, annot=False, cmap='YlOrRd',
            xticklabels=economic_labels, yticklabels=fashion_labels,
            linewidths=0.5, linecolor='gray', ax=ax2,
            cbar_kws={'label': '-log10(p-value)'})

# Add p-value annotations
for i, fashion_var in enumerate(fashion_indicators):
    for j, econ_var in enumerate(economic_indicators):
        p_val = p_value_matrix.loc[fashion_var, econ_var]
        sig_stars = significance_matrix.loc[fashion_var, econ_var]

        if p_val < 0.001:
            annotation = '<0.001\n***'
            text_color = 'white'
        elif p_val < 0.01:
            annotation = f'{p_val:.3f}\n**'
            text_color = 'white'
        elif p_val < 0.05:
            annotation = f'{p_val:.3f}\n*'
            text_color = 'black'
        elif p_val < 0.1:
            annotation = f'{p_val:.3f}\n.'
            text_color = 'black'
        else:
            annotation = f'{p_val:.3f}\nns'
            text_color = 'black'

        ax2.text(j + 0.5, i + 0.5, annotation,
                ha='center', va='center', color=text_color, fontsize=8, fontweight='bold')

ax2.set_title('P-Value Heatmap\n(*** p<0.001, ** p<0.01, * p<0.05, . p<0.1, ns=not sig)',
              fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Economic Indicators', fontsize=12, fontweight='bold')
ax2.set_ylabel('Fashion Indicators', fontsize=12, fontweight='bold')
plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
plt.setp(ax2.get_yticklabels(), rotation=0)

plt.suptitle('Fashion vs Economic Indicators: Correlation & Statistical Significance Analysis\n(N=240 observations, 2004-2024)',
             fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout()

# Save figure
output_path = r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Viz\fashion_economic_significance_matrix.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Significance matrix visualization saved to: {output_path}")

plt.close('all')

# Save matrices to CSV
p_value_matrix.to_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\fashion_economic_pvalues.csv')
significance_matrix.to_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\fashion_economic_significance.csv')
print("P-value matrix saved to: Processed_Data/fashion_economic_pvalues.csv")
print("Significance matrix saved to: Processed_Data/fashion_economic_significance.csv")

# Create detailed interpretation report
print("\n=== DETAILED INTERPRETATION ===\n")

print("STRONGEST SIGNIFICANT CORRELATIONS:\n")
significant_corrs = []
for fashion_var in fashion_indicators:
    for econ_var in economic_indicators:
        p_val = p_value_matrix.loc[fashion_var, econ_var]
        corr_val = fashion_econ_corr.loc[fashion_var, econ_var]
        if p_val < 0.001:
            significant_corrs.append({
                'Fashion': fashion_var.replace('_score', ''),
                'Economic': econ_label_mapping[econ_var],
                'Correlation': corr_val,
                'P-value': p_val,
                'Interpretation': 'Highly significant' if abs(corr_val) > 0.5 else 'Significant'
            })

# Sort by absolute correlation
significant_corrs_df = pd.DataFrame(significant_corrs)
if len(significant_corrs_df) > 0:
    significant_corrs_df['Abs_Corr'] = significant_corrs_df['Correlation'].abs()
    significant_corrs_df = significant_corrs_df.sort_values('Abs_Corr', ascending=False)

    for idx, row in significant_corrs_df.head(15).iterrows():
        direction = "positive" if row['Correlation'] > 0 else "negative"
        strength = "very strong" if abs(row['Correlation']) > 0.8 else "strong" if abs(row['Correlation']) > 0.5 else "moderate"
        print(f"{row['Fashion']} vs {row['Economic']}:")
        print(f"  Correlation: {row['Correlation']:.3f} ({strength} {direction})")
        print(f"  P-value: {row['P-value']:.6f} (p < 0.001)")
        print()

print("\n=== Analysis Complete ===")
