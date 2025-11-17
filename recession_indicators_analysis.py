"""
Recession Indicators Analysis - Python Version
Converts R script to Python for analyzing fashion trends as recession indicators
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FactorAnalysis
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style for plots
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')
sns.set_palette("husl")

# ============================================================================
# DATA LOADING AND CLEANING
# ============================================================================

def load_and_clean_data(filepath):
    """Load Excel file and clean data"""
    print("Loading data...")
    # Skip first row (title) and use second row as header
    df = pd.read_excel(filepath, header=1)
    
    # Remove commas and convert to numeric
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(',', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Fix CCI data issues (missing decimal points)
    if 'cci' in df.columns:
        # Identify values that are too large (should be around 50-150)
        cci_values = df['cci'].copy()
        # Values > 1000 likely have missing decimal points
        mask = cci_values > 1000
        if mask.any():
            print(f"Found {mask.sum()} CCI values with potential decimal point issues")
            # Convert: 101011 -> 101.011, 100578 -> 100.578
            df.loc[mask, 'cci'] = cci_values[mask] / 1000
    
    print(f"Data loaded: {len(df)} rows, {len(df.columns)} columns")
    print(f"CCI range: {df['cci'].min():.2f} to {df['cci'].max():.2f}")
    
    return df

# ============================================================================
# SEM ANALYSIS USING FACTOR ANALYSIS (Alternative to lavaan)
# ============================================================================

def fit_sem_model(df, indicator_vars, indicator_name, max_iterations=3):
    """
    Fit SEM model using Factor Analysis (similar to lavaan)
    Iteratively removes variables with poor loadings
    """
    # Standardize variables
    scaler = StandardScaler()
    data_subset = df[indicator_vars].copy()
    data_subset_scaled = pd.DataFrame(
        scaler.fit_transform(data_subset),
        columns=indicator_vars,
        index=data_subset.index
    )
    
    # Try fitting with all variables first
    current_vars = indicator_vars.copy()
    best_model = None
    best_vars = None
    
    for iteration in range(max_iterations):
        if len(current_vars) < 2:
            break
            
        try:
            # Fit factor analysis (1 factor = latent variable)
            fa = FactorAnalysis(n_components=1, max_iter=1000, random_state=42)
            fa.fit(data_subset_scaled[current_vars])
            
            # Get factor loadings
            loadings = fa.components_[0]
            
            # Check for problematic loadings (too high > 0.95 or too low < 0.3)
            problematic = []
            for i, (var, loading) in enumerate(zip(current_vars, loadings)):
                if abs(loading) > 0.95 or abs(loading) < 0.3:
                    problematic.append((var, loading))
            
            # If no problematic loadings, use this model
            if not problematic:
                best_model = fa
                best_vars = current_vars.copy()
                break
            
            # Remove most problematic variable and continue to next iteration
            if problematic:
                # Sort by how problematic (distance from good range)
                problematic.sort(key=lambda x: min(abs(x[1]) - 0.95, 0.3 - abs(x[1])))
                worst_var = problematic[0][0]
                print(f"  Iteration {iteration + 1}: Removing {worst_var} (loading: {problematic[0][1]:.3f})")
                current_vars.remove(worst_var)
                # Continue to next iteration to refit with remaining variables
            else:
                break
                
        except Exception as e:
            print(f"  Error in iteration {iteration + 1}: {e}")
            break
    
    # If we removed variables, refit the final model
    if best_model is None and len(current_vars) >= 2:
        try:
            best_model = FactorAnalysis(n_components=1, max_iter=1000, random_state=42)
            best_model.fit(data_subset_scaled[current_vars])
            best_vars = current_vars.copy()
        except Exception as e:
            print(f"  Error fitting final model: {e}")
            return None, None, None
    
    if best_model is None:
        return None, None, None
    
    # Get latent scores using the final set of variables
    latent_scores = best_model.transform(data_subset_scaled[best_vars])
    latent_scores = latent_scores.flatten()
    
    # Get final loadings
    final_loadings = best_model.components_[0]
    
    return latent_scores, best_vars, final_loadings

# ============================================================================
# REGRESSION ANALYSIS
# ============================================================================

def run_regression(df, x_var, y_var='cci'):
    """Run linear regression and return results"""
    X = df[x_var].values
    y = df[y_var].values
    
    # Add constant for intercept
    X_with_const = sm.add_constant(X)
    
    # Fit model
    model = sm.OLS(y, X_with_const).fit()
    
    return model

# ============================================================================
# ANALYSIS FOR EACH INDICATOR
# ============================================================================

def analyze_indicator(df, indicator_name, search_terms, df_results):
    """Complete analysis for one recession indicator"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {indicator_name}")
    print(f"{'='*60}")
    
    # Get columns that start with the indicator prefix
    indicator_vars = [col for col in df.columns if col.startswith(indicator_name.lower())]
    
    if not indicator_vars:
        print(f"  Warning: No variables found for {indicator_name}")
        return df, df_results
    
    print(f"  Found {len(indicator_vars)} variables: {indicator_vars}")
    
    # Fit SEM model
    latent_scores, final_vars, loadings = fit_sem_model(df, indicator_vars, indicator_name)
    
    if latent_scores is None:
        print(f"  Could not fit SEM model. Trying single variable regression...")
        # Try with first variable only
        if len(indicator_vars) > 0:
            var_name = indicator_vars[0]
            df[f'{indicator_name}_score'] = df[var_name].values
            model = run_regression(df, f'{indicator_name}_score')
        else:
            return df, df_results
    else:
        # Add latent scores to dataframe
        df[f'{indicator_name}_score'] = latent_scores
        print(f"  SEM model fitted with {len(final_vars)} variables")
        print(f"  Variables used: {final_vars}")
        if loadings is not None:
            print(f"  Factor loadings: {dict(zip(final_vars, loadings))}")
        
        # Run regression
        model = run_regression(df, f'{indicator_name}_score')
    
    # Extract results
    r_squared = model.rsquared
    p_value = model.pvalues[1] if len(model.pvalues) > 1 else model.pvalues[0]
    coefficient = model.params[1] if len(model.params) > 1 else model.params[0]
    std_err = model.bse[1] if len(model.bse) > 1 else model.bse[0]
    
    # Determine significance
    is_significant = p_value < 0.05
    
    print(f"\n  Regression Results:")
    print(f"    R-squared: {r_squared:.4f} ({r_squared*100:.2f}%)")
    print(f"    Coefficient: {coefficient:.4f}")
    print(f"    P-value: {p_value:.6f}")
    print(f"    Significant: {'YES' if is_significant else 'NO'}")
    
    # Store results
    result_row = {
        'Indicator': indicator_name,
        'R_squared': r_squared,
        'R_squared_pct': r_squared * 100,
        'Coefficient': coefficient,
        'P_value': p_value,
        'Std_Error': std_err,
        'Significant': is_significant,
        'Variables_Used': len(final_vars) if final_vars else 1
    }
    
    df_results = pd.concat([df_results, pd.DataFrame([result_row])], ignore_index=True)
    
    return df, df_results

# ============================================================================
# VISUALIZATIONS
# ============================================================================

def create_scatter_plots(df, indicators, output_file='scatter_plots.png'):
    """Create scatter plots for all significant indicators"""
    n_indicators = len(indicators)
    n_cols = 3
    n_rows = (n_indicators + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    axes = axes.flatten() if n_indicators > 1 else [axes]
    
    for idx, indicator in enumerate(indicators):
        score_col = f'{indicator}_score'
        if score_col not in df.columns:
            continue
        
        ax = axes[idx]
        
        # Create scatter plot
        x = df[score_col].values
        y = df['cci'].values
        
        ax.scatter(x, y, alpha=0.5, s=50)
        
        # Fit and plot regression line
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)
        
        # Calculate R² and p-value for annotation
        model = run_regression(df, score_col)
        r2 = model.rsquared
        pval = model.pvalues[1] if len(model.pvalues) > 1 else model.pvalues[0]
        
        # Format indicator name
        indicator_display = indicator.replace('_', ' ').title()
        
        ax.set_xlabel(f'{indicator_display} Trend Score', fontsize=10)
        ax.set_ylabel('Consumer Confidence Index', fontsize=10)
        ax.set_title(f'{indicator_display}\nR² = {r2:.3f}, p = {pval:.4f}', fontsize=11)
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(len(indicators), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nScatter plots saved to: {output_file}")
    plt.close()

def create_summary_chart(df_results, output_file='summary_chart.png'):
    """Create bar chart of R-squared values"""
    # Sort by R-squared
    df_sorted = df_results.sort_values('R_squared', ascending=True)
    
    # Color by significance
    colors = ['#2ecc71' if sig else '#e74c3c' for sig in df_sorted['Significant']]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    bars = ax.barh(df_sorted['Indicator'], df_sorted['R_squared_pct'], color=colors)
    
    ax.set_xlabel('R-squared (%)', fontsize=12)
    ax.set_ylabel('Indicator', fontsize=12)
    ax.set_title('Recession Indicators: Variance Explained in Consumer Confidence', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels on bars
    for i, (bar, r2) in enumerate(zip(bars, df_sorted['R_squared_pct'])):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{r2:.2f}%', ha='left', va='center', fontsize=9)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', label='Significant (p < 0.05)'),
        Patch(facecolor='#e74c3c', label='Not Significant')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Summary chart saved to: {output_file}")
    plt.close()

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    """Main analysis function"""
    print("="*60)
    print("RECESSION INDICATORS ANALYSIS - PYTHON VERSION")
    print("="*60)
    
    # Load data
    data_file = "All_Variables_Us_Data_Sheet1.xlsx"
    df = load_and_clean_data(data_file)
    
    # Initialize results dataframe
    df_results = pd.DataFrame(columns=[
        'Indicator', 'R_squared', 'R_squared_pct', 'Coefficient', 
        'P_value', 'Std_Error', 'Significant', 'Variables_Used'
    ])
    
    # Define all indicators and their search terms
    indicators = {
        'indiesleaze': ['skinnyjeans', 'cheetahprint', 'furcoat', 'leatherskirt', 'discopants'],
        'lipstickindex': ['lipstick', 'lip_stick', 'lipgloss', 'lipliner', 'liptint'],
        'maxiskirt': ['maxiskirt', 'longskirt', 'bohoskirt', 'maxidress', 'longdress'],
        'bigbag': ['hobobag', 'oversizedbag', 'totebag', 'neverfull', 'balenciagacitybag'],
        'highheelindex': ['highheels', 'stilletoheel', 'platforms', 'platformheels', 'pumps'],
        'peplums': ['peplum', 'peplumtops', 'peplumdress', 'rufflewaist', 'peplumblazer'],
        'blazers': ['blazer', 'womensblazer', 'oversizedblazer', 'boyfriendblazer', 'croppedblazer'],
        'mini': ['miniskirt', 'minidress', 'micromini', 'microshort', 'micominiskirt']
    }
    
    # Analyze each indicator
    for indicator_name in indicators.keys():
        df, df_results = analyze_indicator(df, indicator_name, indicators[indicator_name], df_results)
    
    # Save results
    df_results.to_csv('recession_indicators_results.csv', index=False)
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    print(df_results.to_string(index=False))
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    # Scatter plots for all indicators
    create_scatter_plots(df, list(indicators.keys()), 'scatter_plots_all.png')
    
    # Summary chart
    create_summary_chart(df_results, 'summary_chart.png')
    
    # Save cleaned data with scores
    df.to_csv('data_with_scores.csv', index=False)
    print("\nCleaned data with latent scores saved to: data_with_scores.csv")
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*60}")
    print(f"\nKey Findings:")
    significant = df_results[df_results['Significant'] == True].sort_values('R_squared', ascending=False)
    if len(significant) > 0:
        print(f"\n{len(significant)} out of {len(df_results)} indicators are significant:")
        for idx, row in significant.iterrows():
            print(f"  {row['Indicator']}: R² = {row['R_squared']:.4f} ({row['R_squared_pct']:.2f}%), p = {row['P_value']:.6f}")
    else:
        print("\nNo indicators showed significant relationships with CCI.")
    
    return df, df_results

if __name__ == "__main__":
    df, results = main()

