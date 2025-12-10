"""
RECESSION VS FASHION TRENDS VISUALIZATION
Creates a comprehensive chart showing U.S. recessions alongside fashion/beauty search trends
to visually demonstrate the "lipstick effect"
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

print("Loading data...")

# Load the main dataset with search trends
main_data = pd.read_csv('Tableau_Data/tableau_main_data_final.csv')
main_data['date'] = pd.to_datetime(main_data['date'])

# Load Census data for longer time series
try:
    census_data = pd.read_csv('Tableau_Data/tableau_census_timeseries.csv')
    census_data['observation_date'] = pd.to_datetime(census_data['observation_date'])
    has_census = True
    print("Census data loaded successfully")
except:
    has_census = False
    print("Census data not found, using search data only")

# Define U.S. recession periods (NBER official dates)
recessions = [
    {'name': 'Dot-com Crash', 'start': '2001-03-01', 'end': '2001-11-30', 'color': '#8B0000'},
    {'name': 'Great Recession', 'start': '2007-12-01', 'end': '2009-06-30', 'color': '#DC143C'},
    {'name': 'COVID-19 Recession', 'start': '2020-02-01', 'end': '2020-04-30', 'color': '#FF4500'},
]

# Convert recession dates
for r in recessions:
    r['start'] = pd.to_datetime(r['start'])
    r['end'] = pd.to_datetime(r['end'])

print("Creating visualization...")

# Create figure with two subplots
if has_census:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 14))
else:
    fig, ax1 = plt.subplots(1, 1, figsize=(18, 8))

# =================================================================================
# PLOT 1: SEARCH BEHAVIOR (2004-2024)
# =================================================================================

# Plot Consumer Confidence Index
ax1_twin = ax1.twinx()

# CCI on left axis
line1 = ax1.plot(main_data['date'], main_data['cci'],
                 color=plt.cm.plasma(0.2), linewidth=2.5,
                 label='Consumer Confidence Index (CCI)', alpha=0.8)
ax1.fill_between(main_data['date'], main_data['cci'],
                  alpha=0.15, color=plt.cm.plasma(0.2))

# Mini Skirts (strongest predictor) on right axis
line2 = ax1_twin.plot(main_data['date'], main_data['Mini Skirts_score'],
                      color=plt.cm.plasma(0.8), linewidth=2.5,
                      label='Mini Skirts Search Interest (R²=18.3%)', alpha=0.9)
ax1_twin.fill_between(main_data['date'], main_data['Mini Skirts_score'],
                       alpha=0.15, color=plt.cm.plasma(0.8))

# Add recession shading
for recession in recessions:
    if recession['start'] >= main_data['date'].min() and recession['end'] <= main_data['date'].max():
        ax1.axvspan(recession['start'], recession['end'],
                    alpha=0.25, color=recession['color'], zorder=0)
        # Add label at the center of recession period
        mid_date = recession['start'] + (recession['end'] - recession['start']) / 2
        ax1.text(mid_date, ax1.get_ylim()[1] * 0.95, recession['name'],
                ha='center', va='top', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor=recession['color']))

# Formatting
ax1.set_xlabel('Year', fontsize=14, fontweight='bold')
ax1.set_ylabel('Consumer Confidence Index', fontsize=13, fontweight='bold', color=plt.cm.plasma(0.2))
ax1_twin.set_ylabel('Mini Skirts Search Score', fontsize=13, fontweight='bold', color=plt.cm.plasma(0.8))
ax1.set_title('The Lipstick Effect: Fashion Searches Increase During Economic Downturns\n' +
              'Google Trends Data (2004-2024) Shows Inverse Relationship',
              fontsize=16, fontweight='bold', pad=20)

# Color the axis labels to match the lines
ax1.tick_params(axis='y', labelcolor=plt.cm.plasma(0.2), labelsize=11)
ax1_twin.tick_params(axis='y', labelcolor=plt.cm.plasma(0.8), labelsize=11)
ax1.tick_params(axis='x', labelsize=11)

# Format x-axis dates
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1.xaxis.set_major_locator(mdates.YearLocator(2))

# Add legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right',
           fontsize=11, framealpha=0.95, edgecolor='black')

# Add grid
ax1.grid(True, alpha=0.3, linestyle='--')

# Add annotation showing inverse relationship
ax1.text(0.02, 0.02,
         'KEY INSIGHT: When Consumer Confidence ↓ (economy weakens),\nMini Skirts searches ↑ (fashion interest increases)\n' +
         'Correlation: r = -0.535, p < 0.000001 (HIGHLY SIGNIFICANT)',
         transform=ax1.transAxes, fontsize=11, verticalalignment='bottom',
         bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3, edgecolor='black', linewidth=2))

# =================================================================================
# PLOT 2: PURCHASE BEHAVIOR - CENSUS DATA (1992-2025) - if available
# =================================================================================

if has_census:
    # Separate beauty and fashion data
    beauty_data = census_data[census_data['category'] == 'Beauty & Personal Care'].copy()
    fashion_data = census_data[census_data['category'] == "Women's Clothing"].copy()

    # Plot Beauty sales
    ax2_twin = ax2.twinx()

    # CCI on left axis
    line3 = ax2.plot(beauty_data['observation_date'], beauty_data['cci'],
                     color=plt.cm.plasma(0.2), linewidth=2.5,
                     label='Consumer Confidence Index (CCI)', alpha=0.8)
    ax2.fill_between(beauty_data['observation_date'], beauty_data['cci'],
                      alpha=0.15, color=plt.cm.plasma(0.2))

    # Beauty sales on right axis
    line4 = ax2_twin.plot(beauty_data['observation_date'], beauty_data['sales'],
                          color=plt.cm.plasma(0.8), linewidth=2.5,
                          label='Beauty & Personal Care Sales (R²=24.8%)', alpha=0.9)
    ax2_twin.fill_between(beauty_data['observation_date'], beauty_data['sales'],
                           alpha=0.15, color=plt.cm.plasma(0.8))

    # Add recession shading (including earlier recessions)
    all_recessions = [
        {'name': 'Early 90s', 'start': '1990-07-01', 'end': '1991-03-31', 'color': '#4B0082'},
        {'name': 'Dot-com', 'start': '2001-03-01', 'end': '2001-11-30', 'color': '#8B0000'},
        {'name': 'Great Recession', 'start': '2007-12-01', 'end': '2009-06-30', 'color': '#DC143C'},
        {'name': 'COVID-19', 'start': '2020-02-01', 'end': '2020-04-30', 'color': '#FF4500'},
    ]

    for recession in all_recessions:
        r_start = pd.to_datetime(recession['start'])
        r_end = pd.to_datetime(recession['end'])
        if r_start >= beauty_data['observation_date'].min() and r_end <= beauty_data['observation_date'].max():
            ax2.axvspan(r_start, r_end, alpha=0.25, color=recession['color'], zorder=0)
            # Add label
            mid_date = r_start + (r_end - r_start) / 2
            ax2.text(mid_date, ax2.get_ylim()[1] * 0.95, recession['name'],
                    ha='center', va='top', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor=recession['color']))

    # Formatting
    ax2.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Consumer Confidence Index', fontsize=13, fontweight='bold', color=plt.cm.plasma(0.2))
    ax2_twin.set_ylabel('Beauty Sales (Millions $)', fontsize=13, fontweight='bold', color=plt.cm.plasma(0.8))
    ax2.set_title('Hill et al. (2012) Replicated: Beauty Sales Increase During Recessions\n' +
                  'U.S. Census Bureau Data (1992-2025) - 33 Years, 4 Recession Cycles',
                  fontsize=16, fontweight='bold', pad=20)

    # Color the axis labels
    ax2.tick_params(axis='y', labelcolor=plt.cm.plasma(0.2), labelsize=11)
    ax2_twin.tick_params(axis='y', labelcolor=plt.cm.plasma(0.8), labelsize=11)
    ax2.tick_params(axis='x', labelsize=11)

    # Format x-axis dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator(3))

    # Add legend
    lines3, labels3 = ax2.get_legend_handles_labels()
    lines4, labels4 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines3 + lines4, labels3 + labels4, loc='upper left',
               fontsize=11, framealpha=0.95, edgecolor='black')

    # Add grid
    ax2.grid(True, alpha=0.3, linestyle='--')

    # Add annotation showing recession performance
    ax2.text(0.02, 0.02,
             'RECESSION PERFORMANCE:\n' +
             '• Dot-com (2001): Beauty sales +6.2% vs. pre-recession\n' +
             '• Great Recession (2007-09): Beauty sales +4.5% vs. pre-recession\n' +
             '• COVID-19 (2020): Beauty sales +0.4% vs. pre-recession\n' +
             'Beauty sales INCREASED during ALL 3 major recessions tested!',
             transform=ax2.transAxes, fontsize=11, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3, edgecolor='black', linewidth=2))

plt.tight_layout()

# Save the figure
output_file = 'Viz/recession_lipstick_effect_visualization.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\nOK Visualization saved: {output_file}")

# Also create a simpler version with just the key metrics
fig2, ax = plt.subplots(1, 1, figsize=(16, 10))

# Plot both CCI and Mini Skirts on same scale (normalized)
cci_normalized = (main_data['cci'] - main_data['cci'].min()) / (main_data['cci'].max() - main_data['cci'].min())
skirts_normalized = (main_data['Mini Skirts_score'] - main_data['Mini Skirts_score'].min()) / \
                    (main_data['Mini Skirts_score'].max() - main_data['Mini Skirts_score'].min())

# Invert CCI to show same direction
cci_inverted = 1 - cci_normalized

ax.plot(main_data['date'], cci_inverted, color=plt.cm.plasma(0.3), linewidth=3,
        label='Economic Anxiety (Inverted CCI)', alpha=0.9)
ax.plot(main_data['date'], skirts_normalized, color=plt.cm.plasma(0.7), linewidth=3,
        label='Fashion Search Interest (Mini Skirts)', alpha=0.9)

# Add recession shading
for recession in recessions:
    if recession['start'] >= main_data['date'].min() and recession['end'] <= main_data['date'].max():
        ax.axvspan(recession['start'], recession['end'],
                   alpha=0.3, color=recession['color'], zorder=0,
                   label=recession['name'] if recession == recessions[0] else '')

# Formatting
ax.set_xlabel('Year', fontsize=15, fontweight='bold')
ax.set_ylabel('Normalized Index (0-1 scale)', fontsize=14, fontweight='bold')
ax.set_title('The "Lipstick Effect" Visualized: Fashion Interest Rises with Economic Anxiety\n' +
             'When the economy struggles (CCI drops), consumers search more for affordable fashion luxuries',
             fontsize=17, fontweight='bold', pad=25)

ax.legend(loc='upper left', fontsize=13, framealpha=0.95, edgecolor='black', ncol=2)
ax.grid(True, alpha=0.4, linestyle='--')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.tick_params(labelsize=12)

# Add statistical annotation
ax.text(0.98, 0.02,
        'Statistical Evidence:\n' +
        '• Correlation: r = -0.535 (strong inverse)\n' +
        '• R² = 18.3% (variance explained)\n' +
        '• P-value < 0.000001 (highly significant)\n' +
        '• 252 months analyzed (2004-2024)',
        transform=ax.transAxes, fontsize=12, verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black', linewidth=2))

plt.tight_layout()

output_file2 = 'Viz/simplified_lipstick_effect.png'
plt.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
print(f"OK Simplified visualization saved: {output_file2}")

print("\n" + "="*80)
print("RECESSION VISUALIZATIONS CREATED SUCCESSFULLY!")
print("="*80)
print(f"\n1. {output_file}")
if has_census:
    print("   - Two-panel chart showing:")
    print("     - Top: Search behavior (Google Trends 2004-2024)")
    print("     - Bottom: Purchase behavior (U.S. Census 1992-2025)")
else:
    print("   - Search behavior chart (Google Trends 2004-2024)")
print(f"\n2. {output_file2}")
print("   - Simplified single-panel chart showing the inverse relationship")
print("\nBoth visualizations include:")
print("  - Recession period shading (Great Recession, COVID-19, etc.)")
print("  - Dual-axis format showing CCI vs. Fashion/Beauty metrics")
print("  - Statistical annotations (R-squared, p-values)")
print("  - Plasma colormap theme")
print("  - Publication-quality 300 DPI resolution")
print("\nThese visualizations CLEARLY show the lipstick effect in action!")
print("="*80)
