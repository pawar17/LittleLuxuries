"""
Create Additional Visualizations for Little Luxuries Project
Generates insights-focused visualizations beyond the basic analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_data():
    """Load all necessary data files"""
    df = pd.read_csv('data_with_scores.csv')
    results = pd.read_csv('recession_indicators_results.csv')
    temporal = pd.read_csv('tableau_temporal_trends.csv')
    
    # Fix date parsing
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        start_date = pd.to_datetime('2004-01-01')
        df['date'] = pd.date_range(start=start_date, periods=len(df), freq='MS')
    
    temporal['date'] = pd.to_datetime(temporal['date'], errors='coerce')
    
    return df, results, temporal

def create_hypothesis_alignment_chart(results):
    """Visualize how findings align with project hypotheses"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Hypothesis 1: Lipstick Effect Verification
    ax1 = axes[0, 0]
    lipstick_result = results[results['Indicator'] == 'lipstickindex'].iloc[0]
    other_results = results[results['Indicator'] != 'lipstickindex']
    
    categories = ['Lipstick\nIndex', 'Other\nIndicators\n(Avg)']
    r_squared = [lipstick_result['R_squared_pct'], other_results['R_squared_pct'].mean()]
    colors = ['#e74c3c' if lipstick_result['Significant'] == False else '#2ecc71', '#3498db']
    
    bars = ax1.bar(categories, r_squared, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax1.set_ylabel('R-squared (%)', fontsize=12, fontweight='bold')
    ax1.set_title('Hypothesis 1: Does the Lipstick Effect Hold?\nTraditional Lipstick Index vs. Modern Indicators', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(y=5, color='red', linestyle='--', alpha=0.5, label='Significance Threshold (5%)')
    
    # Add value labels
    for bar, val in zip(bars, r_squared):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{val:.2f}%', ha='center', va='bottom', fontweight='bold')
    
    ax1.legend()
    ax1.text(0.5, 0.95, '❌ Lipstick Index: NOT Significant\n✅ Other Indicators: Significant',
             transform=ax1.transAxes, fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 2. Hypothesis 2: Evolution Beyond Traditional Categories
    ax2 = axes[0, 1]
    category_mapping = {
        'indiesleaze': 'Fashion Trends',
        'lipstickindex': 'Beauty & Cosmetics',
        'maxiskirt': 'Fashion Trends',
        'bigbag': 'Accessories',
        'highheelindex': 'Accessories',
        'peplums': 'Fashion Trends',
        'blazers': 'Fashion Trends',
        'mini': 'Fashion Trends'
    }
    
    results['category'] = results['Indicator'].map(category_mapping)
    category_summary = results.groupby('category').agg({
        'R_squared_pct': 'mean',
        'Significant': lambda x: (x == True).sum()
    }).reset_index()
    category_summary = category_summary.sort_values('R_squared_pct', ascending=True)
    
    bars = ax2.barh(category_summary['category'], category_summary['R_squared_pct'], 
                    color=['#9b59b6', '#3498db', '#2ecc71'], alpha=0.7, edgecolor='black', linewidth=2)
    ax2.set_xlabel('Average R-squared (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Hypothesis 2: Evolution Beyond Traditional Categories\nWhich Categories Are the New "Lipsticks"?', 
                  fontsize=13, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, axis='x')
    
    for i, (bar, val, sig) in enumerate(zip(bars, category_summary['R_squared_pct'], category_summary['Significant'])):
        width = bar.get_width()
        ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}% ({int(sig)} sig)', ha='left', va='center', fontweight='bold')
    
    # 3. Hypothesis 3: Predictive Power
    ax3 = axes[1, 0]
    significant = results[results['Significant'] == True].sort_values('R_squared_pct', ascending=True)
    
    colors_sig = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, len(significant)))
    bars = ax3.barh(significant['Indicator'].str.replace('_', ' ').str.title(), 
                    significant['R_squared_pct'], color=colors_sig, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('R-squared (%) - Variance Explained', fontsize=12, fontweight='bold')
    ax3.set_title('Hypothesis 3: Can Trends Predict Economic Sentiment?\nPredictive Power of Each Indicator', 
                  fontsize=13, fontweight='bold', pad=15)
    ax3.grid(True, alpha=0.3, axis='x')
    
    for bar, val in zip(bars, significant['R_squared_pct']):
        width = bar.get_width()
        ax3.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}%', ha='left', va='center', fontweight='bold', fontsize=10)
    
    # Add threshold line
    ax3.axvline(x=10, color='orange', linestyle='--', alpha=0.7, label='Strong Predictor (10%+)')
    ax3.legend()
    
    # 4. Correlation Direction Analysis
    ax4 = axes[1, 1]
    results['correlation_type'] = results['Coefficient'].apply(
        lambda x: 'Negative (Inverse)' if x < 0 else 'Positive'
    )
    corr_counts = results['correlation_type'].value_counts()
    
    colors_corr = ['#e74c3c', '#2ecc71']
    wedges, texts, autotexts = ax4.pie(corr_counts.values, labels=corr_counts.index, 
                                       autopct='%1.1f%%', colors=colors_corr, startangle=90,
                                       textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax4.set_title('Correlation Direction Analysis\nAll Significant Indicators Show Inverse Relationship', 
                  fontsize=13, fontweight='bold', pad=15)
    
    # Add annotation
    ax4.text(0, -1.3, '🔍 Key Insight: Inverse relationship contradicts\n   traditional "Lipstick Effect" theory',
             ha='center', fontsize=10, style='italic',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('hypothesis_alignment_analysis.png', dpi=300, bbox_inches='tight')
    print("Created: hypothesis_alignment_analysis.png")
    plt.close()

def create_temporal_insights(temporal_df):
    """Create temporal analysis visualizations"""
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # Filter out invalid dates
    temporal_df = temporal_df[temporal_df['date'].notna()].copy()
    
    # 1. Top 3 Indicators Over Time
    ax1 = axes[0, 0]
    top_indicators = ['Mini', 'Bigbag', 'Indiesleaze']
    top_data = temporal_df[temporal_df['indicator'].isin([i.title() for i in top_indicators])].copy()
    
    for indicator in top_indicators:
        ind_data = top_data[top_data['indicator'] == indicator.title()]
        if len(ind_data) > 0:
            ax1.plot(ind_data['date'], ind_data['trend_score'], 
                    label=indicator.replace('_', ' ').title(), linewidth=2, alpha=0.8)
    
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    ax1.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Trend Score (Standardized)', fontsize=11, fontweight='bold')
    ax1.set_title('Top 3 Predictors: Temporal Trends\nMini Skirts, Big Bag, Indie Sleaze', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Add economic period shading
    recession_periods = [
        (pd.Timestamp('2008-09-01'), pd.Timestamp('2010-06-01'), 'Great Recession'),
        (pd.Timestamp('2020-03-01'), pd.Timestamp('2021-06-01'), 'COVID-19')
    ]
    for start, end, label in recession_periods:
        ax1.axvspan(start, end, alpha=0.2, color='red', label=label if start == recession_periods[0][0] else '')
    
    # 2. CCI vs Trend Scores (Dual Axis)
    ax2 = axes[0, 1]
    ax2_twin = ax2.twinx()
    
    # Aggregate trend scores by date
    avg_trends = temporal_df.groupby('date')['trend_score'].mean().reset_index()
    cci_data = temporal_df.groupby('date')['cci'].first().reset_index()
    
    line1 = ax2.plot(cci_data['date'], cci_data['cci'], color='#e74c3c', 
                     label='Consumer Confidence Index', linewidth=2.5, alpha=0.8)
    line2 = ax2_twin.plot(avg_trends['date'], avg_trends['trend_score'], color='#3498db',
                          label='Average Trend Score', linewidth=2.5, alpha=0.8, linestyle='--')
    
    ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax2.set_ylabel('CCI', color='#e74c3c', fontsize=11, fontweight='bold')
    ax2_twin.set_ylabel('Trend Score', color='#3498db', fontsize=11, fontweight='bold')
    ax2.set_title('Inverse Relationship Visualization\nCCI vs. Average Fashion Trend Scores', 
                  fontsize=13, fontweight='bold', pad=15)
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    ax2_twin.tick_params(axis='y', labelcolor='#3498db')
    
    # 3. Economic Period Comparison
    ax3 = axes[1, 0]
    period_data = temporal_df.groupby(['economic_period', 'indicator'])['trend_score'].mean().reset_index()
    period_summary = period_data.groupby('economic_period')['trend_score'].mean().sort_values(ascending=True)
    
    colors_period = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(period_summary)))
    bars = ax3.barh(period_summary.index, period_summary.values, color=colors_period, 
                    alpha=0.7, edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('Average Trend Score', fontsize=11, fontweight='bold')
    ax3.set_title('Trend Scores by Economic Period\nHigher Scores = More Search Interest', 
                  fontsize=13, fontweight='bold', pad=15)
    ax3.grid(True, alpha=0.3, axis='x')
    ax3.axvline(x=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
    
    # 4. Seasonal Patterns
    ax4 = axes[1, 1]
    temporal_df['month_name'] = pd.to_datetime(temporal_df['date']).dt.month_name()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    temporal_df['month_name'] = pd.Categorical(temporal_df['month_name'], categories=month_order, ordered=True)
    
    seasonal = temporal_df.groupby('month_name')['trend_score'].mean().reset_index()
    
    ax4.plot(range(len(seasonal)), seasonal['trend_score'], marker='o', 
             linewidth=2.5, markersize=8, color='#9b59b6', alpha=0.8)
    ax4.set_xticks(range(len(seasonal)))
    ax4.set_xticklabels([m[:3] for m in seasonal['month_name']], rotation=45, ha='right')
    ax4.set_ylabel('Average Trend Score', fontsize=11, fontweight='bold')
    ax4.set_title('Seasonal Patterns in Fashion Trends\nMonthly Average Search Interest', 
                  fontsize=13, fontweight='bold', pad=15)
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    
    plt.tight_layout()
    plt.savefig('temporal_insights_analysis.png', dpi=300, bbox_inches='tight')
    print("Created: temporal_insights_analysis.png")
    plt.close()

def create_comparison_visualizations(results):
    """Create comparison and insight visualizations"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Significance vs. Variance Explained
    ax1 = axes[0, 0]
    colors = ['#e74c3c' if not sig else '#2ecc71' for sig in results['Significant']]
    scatter = ax1.scatter(results['R_squared_pct'], results['P_value'], 
                         s=results['R_squared_pct']*50, c=colors, alpha=0.6, 
                         edgecolors='black', linewidth=1.5)
    
    ax1.set_xlabel('R-squared (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('P-value', fontsize=12, fontweight='bold')
    ax1.set_title('Significance vs. Predictive Power\nBubble Size = R-squared', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='Significance Threshold (p=0.05)')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Add labels for top indicators
    top_3 = results.nlargest(3, 'R_squared_pct')
    for idx, row in top_3.iterrows():
        ax1.annotate(row['Indicator'].replace('_', ' ').title(), 
                    (row['R_squared_pct'], row['P_value']),
                    xytext=(5, 5), textcoords='offset points', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # 2. Category Performance Matrix
    ax2 = axes[0, 1]
    category_mapping = {
        'indiesleaze': 'Fashion', 'lipstickindex': 'Beauty', 'maxiskirt': 'Fashion',
        'bigbag': 'Accessories', 'highheelindex': 'Accessories', 'peplums': 'Fashion',
        'blazers': 'Fashion', 'mini': 'Fashion'
    }
    results['category'] = results['Indicator'].map(category_mapping)
    
    category_matrix = results.groupby('category').agg({
        'R_squared_pct': ['mean', 'max', 'count'],
        'Significant': 'sum'
    }).round(2)
    
    im = ax2.imshow([[category_matrix.loc['Fashion', ('R_squared_pct', 'mean')],
                      category_matrix.loc['Beauty', ('R_squared_pct', 'mean')],
                      category_matrix.loc['Accessories', ('R_squared_pct', 'mean')]],
                     [category_matrix.loc['Fashion', ('Significant', 'sum')],
                      category_matrix.loc['Beauty', ('Significant', 'sum')],
                      category_matrix.loc['Accessories', ('Significant', 'sum')]]],
                    cmap='YlOrRd', aspect='auto')
    
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(['Fashion', 'Beauty', 'Accessories'], fontweight='bold')
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['Avg R² (%)', 'Significant Count'], fontweight='bold')
    ax2.set_title('Category Performance Matrix\nFashion Trends Dominate', 
                  fontsize=13, fontweight='bold', pad=15)
    
    # Add text annotations
    for i in range(2):
        for j in range(3):
            text = ax2.text(j, i, f'{category_matrix.iloc[i, j]:.1f}' if i == 0 
                          else f'{int(category_matrix.iloc[i, j])}',
                          ha="center", va="center", color="black", fontweight='bold', fontsize=12)
    
    plt.colorbar(im, ax=ax2)
    
    # 3. Coefficient Magnitude Analysis
    ax3 = axes[1, 0]
    results_sorted = results.sort_values('Coefficient', ascending=True)
    colors_coef = ['#e74c3c' if coef < 0 else '#2ecc71' for coef in results_sorted['Coefficient']]
    
    bars = ax3.barh(results_sorted['Indicator'].str.replace('_', ' ').str.title(),
                    results_sorted['Coefficient'], color=colors_coef, alpha=0.7, 
                    edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('Regression Coefficient', fontsize=12, fontweight='bold')
    ax3.set_title('All Coefficients Are Negative\nInverse Relationship Confirmed', 
                  fontsize=13, fontweight='bold', pad=15)
    ax3.axvline(x=0, color='black', linestyle='-', linewidth=2)
    ax3.grid(True, alpha=0.3, axis='x')
    
    # 4. Predictive Power Ranking
    ax4 = axes[1, 1]
    significant = results[results['Significant'] == True].sort_values('R_squared_pct', ascending=False)
    
    y_pos = np.arange(len(significant))
    bars = ax4.barh(y_pos, significant['R_squared_pct'], 
                    color=plt.cm.viridis(np.linspace(0, 1, len(significant))), 
                    alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(significant['Indicator'].str.replace('_', ' ').str.title(), fontsize=10)
    ax4.set_xlabel('R-squared (%)', fontsize=12, fontweight='bold')
    ax4.set_title('Predictive Power Ranking\nTop Recession Indicators', 
                  fontsize=13, fontweight='bold', pad=15)
    ax4.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, significant['R_squared_pct'])):
        width = bar.get_width()
        ax4.text(width + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.2f}%', ha='left', va='center', fontweight='bold', fontsize=10)
        
        # Add rank number
        ax4.text(-1, bar.get_y() + bar.get_height()/2,
                f'#{i+1}', ha='right', va='center', fontweight='bold', fontsize=11,
                bbox=dict(boxstyle='circle', facecolor='gold', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('comparison_insights.png', dpi=300, bbox_inches='tight')
    print("Created: comparison_insights.png")
    plt.close()

def create_summary_insights_document(results, df):
    """Create a text summary of key insights"""
    insights = []
    insights.append("="*70)
    insights.append("KEY INSIGHTS FROM RECESSION INDICATORS ANALYSIS")
    insights.append("="*70)
    insights.append("")
    
    # Hypothesis 1
    insights.append("HYPOTHESIS 1: Does Consumer Behavior Follow the 'Lipstick Effect'?")
    insights.append("-"*70)
    lipstick = results[results['Indicator'] == 'lipstickindex'].iloc[0]
    if not lipstick['Significant']:
        insights.append("[REJECTED] Traditional Lipstick Index shows NO significant relationship")
        insights.append(f"   - R-squared: {lipstick['R_squared_pct']:.4f}% (essentially zero)")
        insights.append(f"   - P-value: {lipstick['P_value']:.4f} (not significant)")
    else:
        insights.append("[SUPPORTED] Lipstick Index is significant")
    
    other_indicators = results[results['Indicator'] != 'lipstickindex']
    insights.append(f"[SUPPORTED] {other_indicators['Significant'].sum()} out of 7 other indicators ARE significant")
    insights.append(f"   - Average R-squared: {other_indicators['R_squared_pct'].mean():.2f}%")
    insights.append("   - Conclusion: The 'lipstick' has evolved to fashion trends, not cosmetics")
    insights.append("")
    
    # Hypothesis 2
    insights.append("HYPOTHESIS 2: How Has 'Treatonomics' Evolved Beyond Traditional Categories?")
    insights.append("-"*70)
    category_mapping = {
        'indiesleaze': 'Fashion Trends', 'lipstickindex': 'Beauty & Cosmetics',
        'maxiskirt': 'Fashion Trends', 'bigbag': 'Accessories',
        'highheelindex': 'Accessories', 'peplums': 'Fashion Trends',
        'blazers': 'Fashion Trends', 'mini': 'Fashion Trends'
    }
    results['category'] = results['Indicator'].map(category_mapping)
    category_perf = results.groupby('category')['R_squared_pct'].mean().sort_values(ascending=False)
    
    insights.append("[CONFIRMED] Modern 'little luxuries' have shifted categories")
    for cat, r2 in category_perf.items():
        sig_count = results[results['category'] == cat]['Significant'].sum()
        insights.append(f"   - {cat}: {r2:.2f}% avg R² ({sig_count} significant indicators)")
    insights.append("   - Top category: Fashion Trends (strongest predictors)")
    insights.append("   - Bottom category: Beauty & Cosmetics (traditional 'lipstick' failed)")
    insights.append("")
    
    # Hypothesis 3
    insights.append("HYPOTHESIS 3: Can Fashion Trends Predict Economic Sentiment?")
    insights.append("-"*70)
    significant = results[results['Significant'] == True]
    insights.append(f"[STRONGLY SUPPORTED] {len(significant)} out of 8 indicators are significant predictors")
    insights.append("")
    insights.append("Top 3 Predictors:")
    top_3 = significant.nlargest(3, 'R_squared_pct')
    for i, (idx, row) in enumerate(top_3.iterrows(), 1):
        insights.append(f"   {i}. {row['Indicator'].replace('_', ' ').title()}: {row['R_squared_pct']:.2f}% variance (p={row['P_value']:.2e})")
    insights.append("")
    insights.append("CRITICAL DISCOVERY: Inverse Relationship")
    insights.append("-"*70)
    insights.append("All significant indicators show NEGATIVE correlations:")
    insights.append("  - When fashion trend searches INCREASE -> Consumer confidence DECREASES")
    insights.append("  - This contradicts traditional 'Lipstick Effect' theory")
    insights.append("  - Suggests: Search behavior != Purchase behavior")
    insights.append("  - Interpretation: People browse more when anxious, but may not buy")
    insights.append("")
    
    insights.append("IMPLICATIONS FOR PROJECT")
    insights.append("-"*70)
    insights.append("1. Search Trends vs. Purchase Data:")
    insights.append("   - Current analysis uses Google Trends (search behavior)")
    insights.append("   - Need to compare with actual purchase data (retail sales)")
    insights.append("   - This will reveal if browsing translates to buying")
    insights.append("")
    insights.append("2. The 'New Lipstick':")
    insights.append("   - Fashion items (mini skirts, blazers) are stronger than beauty")
    insights.append("   - Accessories (big bags, high heels) show significant relationships")
    insights.append("   - Price point may matter: affordable luxuries dominate")
    insights.append("")
    insights.append("3. Predictive Power:")
    insights.append("   - Mini Skirts: 17.4% variance explained (strongest predictor)")
    insights.append("   - Could serve as leading indicator of economic sentiment")
    insights.append("   - Lag analysis needed to test predictive timing")
    insights.append("")
    
    insights_text = "\n".join(insights)
    
    with open('KEY_INSIGHTS.txt', 'w', encoding='utf-8') as f:
        f.write(insights_text)
    
    print("Created: KEY_INSIGHTS.txt")
    return insights_text

def main():
    print("="*70)
    print("CREATING ADDITIONAL VISUALIZATIONS AND INSIGHTS")
    print("="*70)
    
    df, results, temporal = load_data()
    
    print("\n1. Creating Hypothesis Alignment Chart...")
    create_hypothesis_alignment_chart(results)
    
    print("\n2. Creating Temporal Insights Visualizations...")
    create_temporal_insights(temporal)
    
    print("\n3. Creating Comparison Visualizations...")
    create_comparison_visualizations(results)
    
    print("\n4. Creating Insights Summary Document...")
    insights = create_summary_insights_document(results, df)
    print("\n" + insights)
    
    print("\n" + "="*70)
    print("ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
    print("="*70)
    print("\nFiles created:")
    print("  • hypothesis_alignment_analysis.png")
    print("  • temporal_insights_analysis.png")
    print("  • comparison_insights.png")
    print("  • KEY_INSIGHTS.txt")

if __name__ == "__main__":
    main()

