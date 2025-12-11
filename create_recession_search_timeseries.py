import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np

# Load the data
df = pd.read_csv(r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Processed_Data\master_dataset_complete.csv')
df['date'] = pd.to_datetime(df['date'])

# Define recession periods (NBER official dates)
recessions = [
    {'name': 'Dot-com Crash', 'start': '2001-03-01', 'end': '2001-11-30'},
    {'name': 'Great Recession', 'start': '2007-12-01', 'end': '2009-06-30'},
    {'name': 'COVID-19 Recession', 'start': '2020-02-01', 'end': '2020-04-30'}
]

# Convert recession dates to datetime
for recession in recessions:
    recession['start'] = pd.to_datetime(recession['start'])
    recession['end'] = pd.to_datetime(recession['end'])

# Create the figure and axis
fig, ax = plt.subplots(figsize=(16, 8))

# Plot the search scores for Lipstick Index and Mini Skirts
ax.plot(df['date'], df['Lipstick Index_score'],
        label='Lipstick Index', linewidth=2.5, color='#E94B3C', alpha=0.8)
ax.plot(df['date'], df['Mini Skirts_score'],
        label='Mini Skirts', linewidth=2.5, color='#6C63FF', alpha=0.8)

# Add recession periods as shaded regions
for recession in recessions:
    # Only shade if the recession is within our data range
    if recession['end'] >= df['date'].min() and recession['start'] <= df['date'].max():
        ax.axvspan(recession['start'], recession['end'],
                  alpha=0.2, color='gray', label='_nolegend_')

        # Add recession label
        mid_date = recession['start'] + (recession['end'] - recession['start']) / 2
        y_position = ax.get_ylim()[1] * 0.95
        ax.text(mid_date, y_position, recession['name'],
               horizontalalignment='center', fontsize=10,
               fontweight='bold', alpha=0.7)

# Customize the plot
ax.set_xlabel('Date', fontsize=14, fontweight='bold')
ax.set_ylabel('Search Score (Standardized)', fontsize=14, fontweight='bold')
ax.set_title('Search Trends: Lipstick Index vs. Mini Skirts\nSuperimposed on Recession Timeline (2004-2024)',
            fontsize=16, fontweight='bold', pad=20)

# Format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
plt.xticks(rotation=45, ha='right')

# Add grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

# Add legend
ax.legend(loc='upper left', fontsize=12, framealpha=0.9)

# Add a custom legend for recession periods
from matplotlib.patches import Patch
recession_patch = Patch(color='gray', alpha=0.2, label='Recession Period')
handles, labels = ax.get_legend_handles_labels()
handles.append(recession_patch)
labels.append('Recession Period')
ax.legend(handles, labels, loc='upper left', fontsize=12, framealpha=0.9)

# Adjust layout
plt.tight_layout()

# Save the figure
output_path = r'C:\Users\aadya\Coding_Projects\LittleLuxuries\Viz\lipstick_miniskirt_recession_timeseries.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Visualization saved to: {output_path}")

# Display the plot
plt.show()

# Print summary statistics
print("\n=== Summary Statistics ===")
print(f"Data period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
print(f"\nLipstick Index Search Score:")
print(f"  Mean: {df['Lipstick Index_score'].mean():.3f}")
print(f"  Std Dev: {df['Lipstick Index_score'].std():.3f}")
print(f"  Min: {df['Lipstick Index_score'].min():.3f}")
print(f"  Max: {df['Lipstick Index_score'].max():.3f}")
print(f"\nMini Skirts Search Score:")
print(f"  Mean: {df['Mini Skirts_score'].mean():.3f}")
print(f"  Std Dev: {df['Mini Skirts_score'].std():.3f}")
print(f"  Min: {df['Mini Skirts_score'].min():.3f}")
print(f"  Max: {df['Mini Skirts_score'].max():.3f}")

# Calculate correlation during different periods
print("\n=== Correlation Analysis ===")
print(f"Overall correlation between Lipstick Index and Mini Skirts: {df['Lipstick Index_score'].corr(df['Mini Skirts_score']):.3f}")

# Correlation during recession periods
for recession in recessions:
    recession_mask = (df['date'] >= recession['start']) & (df['date'] <= recession['end'])
    recession_data = df[recession_mask]
    if len(recession_data) > 0:
        corr = recession_data['Lipstick Index_score'].corr(recession_data['Mini Skirts_score'])
        print(f"{recession['name']}: {corr:.3f}")
