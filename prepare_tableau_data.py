"""
Prepare Recession Indicators Data for Tableau Dashboards
This script formats the analysis results for optimal Tableau integration
"""

import pandas as pd
import numpy as np
from datetime import datetime

def prepare_tableau_outputs():
    """Create Tableau-ready datasets from the recession indicators analysis"""
    
    print("="*60)
    print("PREPARING DATA FOR TABLEAU DASHBOARDS")
    print("="*60)
    
    # Load the data with scores
    df = pd.read_csv('data_with_scores.csv')
    results = pd.read_csv('recession_indicators_results.csv')
    
    # ========================================================================
    # 1. TEMPORAL TRENDS DATA (for Temporal Trends Dashboard)
    # ========================================================================
    print("\n1. Creating Temporal Trends Dataset...")
    
    # Parse date if available, otherwise create sequential months
    if 'date' in df.columns:
        try:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        except:
            # If date parsing fails, create date range
            start_date = pd.to_datetime('2004-01-01')
            df['date'] = pd.date_range(start=start_date, periods=len(df), freq='MS')
    else:
        # Create date range from 2004-01
        start_date = pd.to_datetime('2004-01-01')
        df['date'] = pd.date_range(start=start_date, periods=len(df), freq='MS')
    
    # Create temporal trends dataset
    temporal_cols = ['date', 'cci'] + [col for col in df.columns if col.endswith('_score')]
    temporal_df = df[temporal_cols].copy()
    
    # Melt for Tableau (long format)
    indicator_cols = [col for col in temporal_df.columns if col.endswith('_score')]
    temporal_long = pd.melt(
        temporal_df,
        id_vars=['date', 'cci'],
        value_vars=indicator_cols,
        var_name='indicator',
        value_name='trend_score'
    )
    
    # Clean indicator names
    temporal_long['indicator'] = temporal_long['indicator'].str.replace('_score', '')
    temporal_long['indicator'] = temporal_long['indicator'].str.replace('_', ' ').str.title()
    
    # Add month, quarter, year for filtering
    temporal_long['year'] = temporal_long['date'].dt.year
    temporal_long['month'] = temporal_long['date'].dt.month
    temporal_long['quarter'] = temporal_long['date'].dt.quarter
    temporal_long['year_month'] = temporal_long['date'].dt.to_period('M').astype(str)
    
    # Add economic period markers
    temporal_long['economic_period'] = temporal_long['date'].apply(categorize_economic_period)
    
    temporal_long.to_csv('tableau_temporal_trends.csv', index=False)
    print(f"   [OK] Saved: tableau_temporal_trends.csv ({len(temporal_long)} rows)")
    
    # ========================================================================
    # 2. CATEGORY COMPARISON DATA (for Category Comparison Dashboard)
    # ========================================================================
    print("\n2. Creating Category Comparison Dataset...")
    
    # Merge results with indicator metadata
    category_df = results.copy()
    category_df['indicator_display'] = category_df['Indicator'].str.replace('_', ' ').str.title()
    
    # Add category groupings based on your proposal
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
    
    category_df['category_group'] = category_df['Indicator'].map(category_mapping)
    
    # Add significance level
    category_df['significance_level'] = category_df.apply(
        lambda row: 'Highly Significant' if row['P_value'] < 0.001 
        else 'Significant' if row['P_value'] < 0.05 
        else 'Not Significant', axis=1
    )
    
    # Add correlation direction
    category_df['correlation_direction'] = category_df['Coefficient'].apply(
        lambda x: 'Negative (Inverse)' if x < 0 else 'Positive'
    )
    
    # Calculate "luxury ratio" equivalent (normalized R-squared)
    max_r2 = category_df['R_squared'].max()
    category_df['luxury_ratio'] = category_df['R_squared'] / max_r2 if max_r2 > 0 else 0
    
    category_df.to_csv('tableau_category_comparison.csv', index=False)
    print(f"   [OK] Saved: tableau_category_comparison.csv ({len(category_df)} rows)")
    
    # ========================================================================
    # 3. CORRELATION EXPLORER DATA (for Correlation Explorer Dashboard)
    # ========================================================================
    print("\n3. Creating Correlation Explorer Dataset...")
    
    # Create detailed correlation data for scatter plots
    correlation_data = []
    
    for indicator in results['Indicator']:
        score_col = f'{indicator}_score'
        if score_col in df.columns:
            indicator_data = df[['cci', score_col]].copy()
            indicator_data['indicator'] = indicator.replace('_', ' ').title()
            indicator_data = indicator_data.rename(columns={score_col: 'trend_score'})
            correlation_data.append(indicator_data)
    
    correlation_df = pd.concat(correlation_data, ignore_index=True)
    
    # Add correlation metrics for each indicator
    correlation_metrics = []
    for indicator in results['Indicator']:
        score_col = f'{indicator}_score'
        if score_col in df.columns:
            corr_coef = df['cci'].corr(df[score_col])
            result_row = results[results['Indicator'] == indicator].iloc[0]
            correlation_metrics.append({
                'indicator': indicator.replace('_', ' ').title(),
                'correlation_coefficient': corr_coef,
                'r_squared': result_row['R_squared'],
                'p_value': result_row['P_value'],
                'coefficient': result_row['Coefficient'],
                'significant': result_row['Significant']
            })
    
    correlation_metrics_df = pd.DataFrame(correlation_metrics)
    correlation_metrics_df.to_csv('tableau_correlation_metrics.csv', index=False)
    
    correlation_df.to_csv('tableau_correlation_explorer.csv', index=False)
    print(f"   [OK] Saved: tableau_correlation_explorer.csv ({len(correlation_df)} rows)")
    print(f"   [OK] Saved: tableau_correlation_metrics.csv ({len(correlation_metrics_df)} rows)")
    
    # ========================================================================
    # 4. SUMMARY STATISTICS FOR DASHBOARD KPIs
    # ========================================================================
    print("\n4. Creating Summary Statistics...")
    
    summary_stats = {
        'total_indicators': len(results),
        'significant_indicators': results['Significant'].sum(),
        'avg_r_squared': results['R_squared'].mean(),
        'max_r_squared': results['R_squared'].max(),
        'best_indicator': results.loc[results['R_squared'].idxmax(), 'Indicator'],
        'total_months': len(df),
        'date_range_start': df['date'].min() if 'date' in df.columns else '2004-01',
        'date_range_end': df['date'].max() if 'date' in df.columns else '2024-12',
        'avg_cci': df['cci'].mean(),
        'min_cci': df['cci'].min(),
        'max_cci': df['cci'].max()
    }
    
    summary_df = pd.DataFrame([summary_stats])
    summary_df.to_csv('tableau_summary_stats.csv', index=False)
    print(f"   [OK] Saved: tableau_summary_stats.csv")
    
    # ========================================================================
    # 5. TIME SERIES WITH LAGS (for predictive analysis)
    # ========================================================================
    print("\n5. Creating Lagged Variables for Predictive Analysis...")
    
    lag_df = df[['date', 'cci'] + [col for col in df.columns if col.endswith('_score')]].copy()
    
    # Create lagged versions (3-month and 6-month)
    for col in lag_df.columns:
        if col.endswith('_score'):
            indicator_name = col.replace('_score', '')
            lag_df[f'{indicator_name}_lag3'] = lag_df[col].shift(3)
            lag_df[f'{indicator_name}_lag6'] = lag_df[col].shift(6)
    
    # Calculate correlations with lagged CCI
    lag_df['cci_lag3'] = lag_df['cci'].shift(-3)  # Future CCI
    lag_df['cci_lag6'] = lag_df['cci'].shift(-6)  # Future CCI
    
    lag_df.to_csv('tableau_lagged_analysis.csv', index=False)
    print(f"   [OK] Saved: tableau_lagged_analysis.csv ({len(lag_df)} rows)")
    
    print("\n" + "="*60)
    print("TABLEAU DATA PREPARATION COMPLETE!")
    print("="*60)
    print("\nFiles created:")
    print("  • tableau_temporal_trends.csv - For Temporal Trends Dashboard")
    print("  • tableau_category_comparison.csv - For Category Comparison Dashboard")
    print("  • tableau_correlation_explorer.csv - For Correlation Explorer Dashboard")
    print("  • tableau_correlation_metrics.csv - Correlation summary metrics")
    print("  • tableau_summary_stats.csv - KPI summary statistics")
    print("  • tableau_lagged_analysis.csv - For predictive/leading indicator analysis")
    print("\nThese files are ready to import into Tableau!")

def categorize_economic_period(date):
    """Categorize dates into economic periods"""
    if pd.isna(date):
        return 'Unknown'
    
    year = date.year
    month = date.month
    
    # Great Recession period
    if (year == 2008 and month >= 9) or (year == 2009) or (year == 2010 and month <= 6):
        return 'Great Recession (2008-2010)'
    
    # COVID-19 Pandemic
    if (year == 2020 and month >= 3) or (year == 2021 and month <= 6):
        return 'COVID-19 Pandemic (2020-2021)'
    
    # Post-COVID Recovery
    if (year == 2021 and month >= 7) or (year == 2022):
        return 'Post-COVID Recovery (2021-2022)'
    
    # Inflation Period
    if year == 2023 or (year == 2024 and month <= 6):
        return 'Inflation Period (2023-2024)'
    
    # Pre-Recession
    if year < 2008:
        return 'Pre-Recession (2004-2007)'
    
    # Recovery Period
    if 2010 < year < 2020:
        return 'Recovery Period (2011-2019)'
    
    # Recent
    return 'Recent (2024-2025)'

if __name__ == "__main__":
    prepare_tableau_outputs()

