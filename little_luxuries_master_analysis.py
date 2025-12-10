"""
========================================================================================================
LITTLE LUXURIES PROJECT - MASTER ANALYSIS SCRIPT
========================================================================================================

Project: Testing the "Lipstick Effect" and Treatonomics Using Search and Purchase Data
Team: Tanushree Paidichetty, Sruthi Visvanathan, Aadya Pawar

RESEARCH QUESTIONS:
1. Does consumer behavior follow the "Lipstick Effect"? (Hill et al. 2012)
2. How has "treatonomics" evolved beyond traditional categories?
3. Can fashion/beauty trends predict economic sentiment?

METHODOLOGY:
- Structural Equation Modeling (SEM) for latent variable creation
- Linear regression for correlation analysis
- Demographic segmentation and price point analysis
- Temporal pattern analysis with economic indicators
- Comparison of SEARCH behavior (Google Trends) vs PURCHASE behavior (retail sales)

DATA SOURCES:
1. Google Trends: Fashion/beauty search volumes (2004-2024)
2. Consumer Confidence Index (CCI): Economic sentiment
3. Consumer Price Index (CPI): Inflation adjustment
4. FRED Economic Data: Unemployment, consumer sentiment, retail sales
5. Retail Transaction Data: Actual purchase behavior with demographics

ALIGNMENT WITH PEER-REVIEWED RESEARCH:
- Hill et al. (2012): "Boosting Beauty in an Economic Decline"
- 2019 Study: "Evidence for the lipstick effect during the Great Recession"

OUTPUTS:
- Comprehensive analysis results
- Statistical visualizations
- Tableau-ready datasets
- Detailed findings report
========================================================================================================
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FactorAnalysis
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    try:
        plt.style.use('seaborn-whitegrid')
    except:
        plt.style.use('ggplot')

sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11

print("="*100)
print(" "*30 + "LITTLE LUXURIES PROJECT")
print(" "*25 + "Comprehensive Treatonomics Analysis")
print("="*100)
print(f"\nAnalysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n" + "="*100)


# ========================================================================================================
# PART 1: DATA LOADING AND INTEGRATION
# ========================================================================================================

def load_google_trends_data(filepath='Data_Sources/All_Variables_Us_Data_Sheet1.xlsx'):
    """Load and clean Google Trends data with CCI"""
    print("\n" + "="*100)
    print("PART 1A: LOADING GOOGLE TRENDS & CONSUMER CONFIDENCE DATA")
    print("="*100)

    df = pd.read_excel(filepath, header=1)

    # Clean numeric columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(',', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fix CCI decimal point issues
    if 'cci' in df.columns:
        cci_values = df['cci'].copy()
        mask = cci_values > 1000
        if mask.any():
            df.loc[mask, 'cci'] = cci_values[mask] / 1000

        mask2 = (df['cci'] > 150) & (df['cci'] < 1000)
        if mask2.any():
            mask3 = df['cci'] > 200
            if mask3.any():
                df.loc[mask3, 'cci'] = df.loc[mask3, 'cci'] / 100

    # Ensure date column
    if 'date' in df.columns:
        if df['date'].dtype == 'object':
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if df['date'].isna().all():
            start_date = pd.to_datetime('2004-01-01')
            df['date'] = pd.date_range(start=start_date, periods=len(df), freq='MS')

    print(f"\nOK Google Trends data loaded: {len(df)} months")
    print(f"  Date range: {df['date'].min().strftime('%Y-%m')} to {df['date'].max().strftime('%Y-%m')}")
    print(f"  CCI range: {df['cci'].min():.2f} to {df['cci'].max():.2f}")
    print(f"  Total search terms: {len([c for c in df.columns if c not in ['date', 'cci']])}")

    return df


def load_fred_data():
    """Load all FRED economic indicators"""
    print("\n" + "="*100)
    print("PART 1B: LOADING FRED ECONOMIC INDICATORS")
    print("="*100)

    fred_data = {}

    # CPI - Consumer Price Index
    try:
        cpi = pd.read_csv('Data_Sources/CPILFESL.csv')
        cpi['observation_date'] = pd.to_datetime(cpi['observation_date'])
        fred_data['CPI'] = cpi
        print(f"\nOK CPI loaded: {len(cpi)} observations ({cpi['observation_date'].min().strftime('%Y-%m')} to {cpi['observation_date'].max().strftime('%Y-%m')})")
    except:
        print("\nX CPI file not found")

    # Consumer Sentiment
    try:
        umcsent = pd.read_csv('Data_Sources/UMCSENT.csv')
        umcsent['observation_date'] = pd.to_datetime(umcsent['observation_date'])
        fred_data['Consumer_Sentiment'] = umcsent
        print(f"OK Consumer Sentiment loaded: {len(umcsent)} observations")
    except:
        print("X Consumer Sentiment file not found")

    # Unemployment Rate
    try:
        unrate = pd.read_csv('Data_Sources/UNRATE.csv')
        unrate['observation_date'] = pd.to_datetime(unrate['observation_date'])
        fred_data['Unemployment'] = unrate
        print(f"OK Unemployment Rate loaded: {len(unrate)} observations")
    except:
        print("X Unemployment file not found")

    # Retail Sales - Clothing & Accessories
    try:
        retail = pd.read_csv('Data_Sources/MRTSSM448USN.csv')
        retail['observation_date'] = pd.to_datetime(retail['observation_date'])
        fred_data['Retail_Sales'] = retail
        print(f"OK Retail Sales (Clothing) loaded: {len(retail)} observations")
    except:
        print("X Retail Sales file not found")

    # Personal Saving Rate
    try:
        psavert = pd.read_csv('Data_Sources/PSAVERT.csv')
        psavert['observation_date'] = pd.to_datetime(psavert['observation_date'])
        fred_data['Saving_Rate'] = psavert
        print(f"OK Personal Saving Rate loaded: {len(psavert)} observations")
    except:
        print("X Saving Rate file not found")

    return fred_data


def load_retail_transactions():
    """Load retail transaction data for purchase behavior analysis"""
    print("\n" + "="*100)
    print("PART 1C: LOADING RETAIL TRANSACTION DATA (PURCHASE BEHAVIOR)")
    print("="*100)

    try:
        retail_df = pd.read_csv('Data_Sources/spending_patterns_detailed.csv')
        retail_df['Transaction Date'] = pd.to_datetime(retail_df['Transaction Date'])

        print(f"\nOK Retail transactions loaded: {len(retail_df):,} transactions")
        print(f"  Date range: {retail_df['Transaction Date'].min().strftime('%Y-%m-%d')} to {retail_df['Transaction Date'].max().strftime('%Y-%m-%d')}")
        print(f"  Total spending: ${retail_df['Total Spent'].sum():,.2f}")
        print(f"  Unique customers: {retail_df['Customer ID'].nunique():,}")
        print(f"\n  Product categories ({retail_df['Category'].nunique()}):")
        for cat, count in retail_df['Category'].value_counts().head(10).items():
            print(f"    - {cat}: {count:,} transactions")

        return retail_df
    except Exception as e:
        print(f"\nX Error loading retail data: {e}")
        return None


def integrate_all_data(google_trends_df, fred_data):
    """Integrate all data sources into master dataset"""
    print("\n" + "="*100)
    print("PART 1D: INTEGRATING ALL DATA SOURCES")
    print("="*100)

    master_df = google_trends_df.copy()

    # Merge CPI
    if 'CPI' in fred_data:
        cpi_df = fred_data['CPI'].copy()
        master_df = master_df.merge(cpi_df, left_on='date', right_on='observation_date', how='left')
        master_df.rename(columns={'CPILFESL': 'cpi'}, inplace=True)
        master_df.drop('observation_date', axis=1, inplace=True, errors='ignore')

        # Calculate inflation metrics
        base_cpi = master_df['cpi'].iloc[0]
        master_df['cpi_index'] = master_df['cpi'] / base_cpi
        master_df['inflation_rate_yoy'] = master_df['cpi'].pct_change(12) * 100
        print(f"\nOK CPI integrated - Cumulative inflation: {(master_df['cpi_index'].iloc[-1] - 1) * 100:.1f}%")

    # Merge Consumer Sentiment
    if 'Consumer_Sentiment' in fred_data:
        sent_df = fred_data['Consumer_Sentiment'].copy()
        master_df = master_df.merge(sent_df, left_on='date', right_on='observation_date', how='left')
        master_df.rename(columns={'UMCSENT': 'consumer_sentiment'}, inplace=True)
        master_df.drop('observation_date', axis=1, inplace=True, errors='ignore')
        print(f"OK Consumer Sentiment integrated")

    # Merge Unemployment
    if 'Unemployment' in fred_data:
        unemp_df = fred_data['Unemployment'].copy()
        master_df = master_df.merge(unemp_df, left_on='date', right_on='observation_date', how='left')
        master_df.rename(columns={'UNRATE': 'unemployment_rate'}, inplace=True)
        master_df.drop('observation_date', axis=1, inplace=True, errors='ignore')
        print(f"OK Unemployment Rate integrated")

    # Merge Retail Sales
    if 'Retail_Sales' in fred_data:
        retail_df = fred_data['Retail_Sales'].copy()
        master_df = master_df.merge(retail_df, left_on='date', right_on='observation_date', how='left')
        master_df.rename(columns={'MRTSSM448USN': 'retail_sales_clothing'}, inplace=True)
        master_df.drop('observation_date', axis=1, inplace=True, errors='ignore')

        # Calculate real (inflation-adjusted) retail sales
        if 'cpi_index' in master_df.columns:
            master_df['retail_sales_real'] = master_df['retail_sales_clothing'] / master_df['cpi_index']
        print(f"OK Retail Sales (Clothing) integrated")

    # Merge Saving Rate
    if 'Saving_Rate' in fred_data:
        save_df = fred_data['Saving_Rate'].copy()
        master_df = master_df.merge(save_df, left_on='date', right_on='observation_date', how='left')
        master_df.rename(columns={'PSAVERT': 'personal_saving_rate'}, inplace=True)
        master_df.drop('observation_date', axis=1, inplace=True, errors='ignore')
        print(f"OK Personal Saving Rate integrated")

    # Add economic period indicators
    master_df['year'] = master_df['date'].dt.year
    master_df['month'] = master_df['date'].dt.month
    master_df['quarter'] = master_df['date'].dt.quarter

    # Define recession/crisis periods
    master_df['period'] = 'Normal'
    master_df.loc[(master_df['date'] >= '2007-12-01') & (master_df['date'] <= '2009-06-30'), 'period'] = 'Great Recession'
    master_df.loc[(master_df['date'] >= '2020-02-01') & (master_df['date'] <= '2020-04-30'), 'period'] = 'COVID-19 Crisis'
    master_df.loc[(master_df['date'] >= '2022-01-01') & (master_df['date'] <= '2023-06-30'), 'period'] = 'Inflation Surge'

    print(f"\nOK Master dataset created: {len(master_df)} months × {len(master_df.columns)} variables")
    print(f"\nEconomic periods:")
    print(master_df['period'].value_counts().to_string())

    return master_df


# ========================================================================================================
# PART 2: SEARCH BEHAVIOR ANALYSIS (GOOGLE TRENDS)
# ========================================================================================================

def create_latent_variables(df, indicators_dict):
    """Create latent variables using Factor Analysis (SEM approach)"""
    print("\n" + "="*100)
    print("PART 2A: CREATING LATENT VARIABLES FROM SEARCH TERMS")
    print("="*100)

    scaler = StandardScaler()
    scores_df = df[['date', 'cci']].copy()

    for indicator_name, search_terms in indicators_dict.items():
        print(f"\n-> Processing: {indicator_name}")
        print(f"  Search terms: {', '.join(search_terms)}")

        # Extract relevant columns
        available_terms = [term for term in search_terms if term in df.columns]

        if len(available_terms) < 2:
            print(f"  X Insufficient data (need at least 2 terms)")
            continue

        X = df[available_terms].copy()

        # Handle missing values
        X = X.fillna(X.mean())

        # Standardize
        X_scaled = scaler.fit_transform(X)

        # Factor Analysis
        fa = FactorAnalysis(n_components=1, random_state=42)
        latent_score = fa.fit_transform(X_scaled)

        scores_df[f'{indicator_name}_score'] = latent_score.flatten()
        print(f"  OK Latent variable created (variance explained: {fa.noise_variance_.mean():.3f})")

    return scores_df


def analyze_search_correlations(scores_df):
    """Analyze correlations between search trends and economic indicators"""
    print("\n" + "="*100)
    print("PART 2B: SEARCH BEHAVIOR CORRELATION ANALYSIS")
    print("="*100)

    results = []
    score_columns = [col for col in scores_df.columns if col.endswith('_score')]

    print(f"\nTesting {len(score_columns)} indicators against Consumer Confidence Index\n")
    print("-" * 100)

    for score_col in score_columns:
        indicator_name = score_col.replace('_score', '')

        # Prepare data
        X = scores_df[score_col].values.reshape(-1, 1)
        y = scores_df['cci'].values

        # Add constant for intercept
        X_with_const = sm.add_constant(X)

        # OLS Regression
        model = sm.OLS(y, X_with_const).fit()

        # Store results
        results.append({
            'Indicator': indicator_name,
            'Coefficient': model.params[1],
            'R²': model.rsquared,
            'Adj_R²': model.rsquared_adj,
            'P-value': model.pvalues[1],
            'F-statistic': model.fvalue,
            'Std_Error': model.bse[1],
            'Significant': 'Yes' if model.pvalues[1] < 0.05 else 'No'
        })

        # Print result
        sig_symbol = "OK" if model.pvalues[1] < 0.05 else "X"
        print(f"{sig_symbol} {indicator_name:20s} | R²={model.rsquared*100:5.1f}% | Coef={model.params[1]:7.3f} | p={model.pvalues[1]:.6f}")

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('R²', ascending=False)

    print("-" * 100)
    print(f"\nSummary: {results_df['Significant'].value_counts().get('Yes', 0)}/{len(results_df)} indicators significant (p < 0.05)")

    return results_df


# ========================================================================================================
# PART 3: PURCHASE BEHAVIOR ANALYSIS (RETAIL TRANSACTIONS)
# ========================================================================================================

def categorize_little_luxuries(retail_df):
    """Categorize purchases into little luxuries vs necessities"""
    print("\n" + "="*100)
    print("PART 3A: CATEGORIZING PURCHASE BEHAVIOR")
    print("="*100)

    # Define little luxury categories based on proposal
    little_luxury_categories = {
        'Beauty & Cosmetics': ['Personal Hygiene'],  # Includes cosmetics/beauty items
        'Fashion & Accessories': ['Shopping'],  # Clothing, accessories, shoes
        'Food Treats': ['Food'],  # Gourmet food, treats
        'Experiential': ['Friend Activities', 'Travel', 'Hobbies', 'Fitness'],  # Experiences
        'Gifts': ['Gifts'],  # Gift purchases
    }

    necessity_categories = ['Groceries', 'Housing and Utilities', 'Transportation',
                           'Medical/Dental', 'Subscriptions']

    # Create luxury classification
    retail_df['purchase_type'] = 'Other'
    retail_df['luxury_category'] = 'Other'

    for luxury_type, categories in little_luxury_categories.items():
        mask = retail_df['Category'].isin(categories)
        retail_df.loc[mask, 'purchase_type'] = 'Little Luxury'
        retail_df.loc[mask, 'luxury_category'] = luxury_type

    retail_df.loc[retail_df['Category'].isin(necessity_categories), 'purchase_type'] = 'Necessity'

    print(f"\nOK Purchases categorized:")
    print(f"\n  Purchase Type Distribution:")
    for ptype, count in retail_df['purchase_type'].value_counts().items():
        pct = count / len(retail_df) * 100
        total_spend = retail_df[retail_df['purchase_type'] == ptype]['Total Spent'].sum()
        print(f"    - {ptype}: {count:,} transactions ({pct:.1f}%) - ${total_spend:,.2f}")

    print(f"\n  Little Luxury Categories:")
    luxury_df = retail_df[retail_df['purchase_type'] == 'Little Luxury']
    for cat, count in luxury_df['luxury_category'].value_counts().items():
        total_spend = luxury_df[luxury_df['luxury_category'] == cat]['Total Spent'].sum()
        avg_price = total_spend / count
        print(f"    - {cat}: {count:,} transactions - ${total_spend:,.2f} (avg: ${avg_price:.2f})")

    return retail_df


def analyze_purchase_patterns(retail_df):
    """Analyze purchase patterns over time"""
    print("\n" + "="*100)
    print("PART 3B: TEMPORAL PURCHASE PATTERN ANALYSIS")
    print("="*100)

    # Aggregate by month
    retail_df['year_month'] = retail_df['Transaction Date'].dt.to_period('M')

    monthly_summary = retail_df.groupby(['year_month', 'purchase_type']).agg({
        'Total Spent': ['sum', 'count', 'mean'],
        'Customer ID': 'nunique'
    }).reset_index()

    monthly_summary.columns = ['year_month', 'purchase_type', 'total_spending',
                               'transaction_count', 'avg_transaction', 'unique_customers']
    monthly_summary['year_month'] = monthly_summary['year_month'].dt.to_timestamp()

    # Calculate luxury ratio
    total_by_month = monthly_summary.groupby('year_month')['total_spending'].sum().reset_index()
    total_by_month.columns = ['year_month', 'total_monthly_spending']

    monthly_summary = monthly_summary.merge(total_by_month, on='year_month')
    monthly_summary['spending_share'] = (monthly_summary['total_spending'] /
                                         monthly_summary['total_monthly_spending'] * 100)

    print(f"\nOK Monthly aggregation complete: {len(monthly_summary)} month-category combinations")
    print(f"  Date range: {monthly_summary['year_month'].min().strftime('%Y-%m')} to {monthly_summary['year_month'].max().strftime('%Y-%m')}")

    # Calculate luxury ratio metric
    luxury_ratio = monthly_summary[monthly_summary['purchase_type'] == 'Little Luxury'].copy()
    luxury_ratio = luxury_ratio[['year_month', 'spending_share']].rename(
        columns={'spending_share': 'luxury_ratio_pct'})

    print(f"\n  Average Luxury Ratio: {luxury_ratio['luxury_ratio_pct'].mean():.1f}%")
    print(f"  Range: {luxury_ratio['luxury_ratio_pct'].min():.1f}% - {luxury_ratio['luxury_ratio_pct'].max():.1f}%")

    return monthly_summary, luxury_ratio


def analyze_price_points(retail_df):
    """Analyze price point sweet spots for little luxuries"""
    print("\n" + "="*100)
    print("PART 3C: PRICE POINT ANALYSIS")
    print("="*100)

    luxury_df = retail_df[retail_df['purchase_type'] == 'Little Luxury'].copy()

    # Define price ranges
    bins = [0, 10, 30, 50, 100, 500, float('inf')]
    labels = ['$0-10', '$10-30', '$30-50', '$50-100', '$100-500', '$500+']
    luxury_df['price_range'] = pd.cut(luxury_df['Total Spent'], bins=bins, labels=labels)

    price_analysis = luxury_df.groupby('price_range').agg({
        'Total Spent': ['count', 'sum', 'mean'],
        'Customer ID': 'nunique'
    }).reset_index()

    price_analysis.columns = ['price_range', 'transaction_count', 'total_spent',
                              'avg_transaction', 'unique_customers']

    print(f"\nOK Price point analysis for Little Luxuries:\n")
    print("-" * 80)
    for _, row in price_analysis.iterrows():
        pct = row['transaction_count'] / price_analysis['transaction_count'].sum() * 100
        print(f"  {row['price_range']:10s} | {row['transaction_count']:5,} transactions ({pct:5.1f}%) | "
              f"Total: ${row['total_spent']:10,.0f} | Avg: ${row['avg_transaction']:6.2f}")
    print("-" * 80)

    # Identify sweet spot
    sweet_spot = price_analysis.loc[price_analysis['transaction_count'].idxmax()]
    print(f"\n  ** Sweet Spot: {sweet_spot['price_range']} range with {sweet_spot['transaction_count']:,} transactions")

    return price_analysis


# ========================================================================================================
# PART 4: INTEGRATED ANALYSIS - SEARCH VS PURCHASE BEHAVIOR
# ========================================================================================================

def compare_search_vs_purchase(master_df, monthly_purchase_summary):
    """Compare search behavior trends with actual purchase behavior"""
    print("\n" + "="*100)
    print("PART 4: SEARCH vs PURCHASE BEHAVIOR COMPARISON")
    print("="*100)
    print("\nThis analysis directly addresses Hill et al. (2012) by comparing:")
    print("  - Search behavior (Google Trends) - what people SEARCH for")
    print("  - Purchase behavior (Retail data) - what people actually BUY")

    # Merge datasets
    luxury_purchases = monthly_purchase_summary[
        monthly_purchase_summary['purchase_type'] == 'Little Luxury'
    ][['year_month', 'total_spending', 'transaction_count']].copy()
    luxury_purchases.columns = ['date', 'luxury_spending', 'luxury_transactions']

    # Get relevant search scores
    search_cols = ['date', 'cci'] + [col for col in master_df.columns if col.endswith('_score')]
    search_data = master_df[search_cols].copy()

    # Merge
    comparison_df = search_data.merge(luxury_purchases, on='date', how='left')

    # Analyze correlations
    print(f"\nOK Datasets merged: {comparison_df['luxury_spending'].notna().sum()} overlapping months")

    # Test correlations for overlapping period
    overlap_df = comparison_df.dropna(subset=['luxury_spending'])

    if len(overlap_df) > 10:
        print(f"\n Correlation Analysis (n={len(overlap_df)} months):\n")
        print("-" * 100)

        # Luxury spending vs CCI
        corr_cci, p_cci = stats.pearsonr(overlap_df['cci'], overlap_df['luxury_spending'])
        print(f"  Luxury Spending vs CCI:         r={corr_cci:6.3f}, p={p_cci:.4f} {'OK Sig' if p_cci < 0.05 else 'X NS'}")

        # Luxury transactions vs CCI
        corr_trans, p_trans = stats.pearsonr(overlap_df['cci'], overlap_df['luxury_transactions'])
        print(f"  Luxury Transactions vs CCI:     r={corr_trans:6.3f}, p={p_trans:.4f} {'OK Sig' if p_trans < 0.05 else 'X NS'}")

        print("\n  Top Search Indicators vs Luxury Spending:")
        for col in search_cols[2:]:  # Skip date and cci
            if col in overlap_df.columns:
                valid_data = overlap_df[[col, 'luxury_spending']].dropna()
                if len(valid_data) > 10:
                    corr, p = stats.pearsonr(valid_data[col], valid_data['luxury_spending'])
                    indicator_name = col.replace('_score', '')
                    print(f"    - {indicator_name:25s} r={corr:6.3f}, p={p:.4f} {'OK' if p < 0.05 else 'X'}")

        print("-" * 100)

    return comparison_df


# ========================================================================================================
# PART 5: VISUALIZATIONS
# ========================================================================================================

def create_visualizations(master_df, search_results, retail_df, comparison_df):
    """Create comprehensive visualizations"""
    print("\n" + "="*100)
    print("PART 5: GENERATING VISUALIZATIONS")
    print("="*100)

    # 1. Search Indicator Rankings
    print("\n-> Creating search indicator rankings visualization...")
    fig, ax = plt.subplots(figsize=(12, 8))

    search_results_sorted = search_results.sort_values('R²', ascending=True)
    colors = ['#2ecc71' if sig == 'Yes' else '#e74c3c' for sig in search_results_sorted['Significant']]

    ax.barh(search_results_sorted['Indicator'], search_results_sorted['R²'] * 100, color=colors)
    ax.set_xlabel('R² (% Variance Explained)', fontsize=12, fontweight='bold')
    ax.set_title('Fashion/Beauty Search Trends as Recession Indicators\n(Correlation with Consumer Confidence Index)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax.grid(axis='x', alpha=0.3)

    # Add significance markers
    for i, (idx, row) in enumerate(search_results_sorted.iterrows()):
        text = f"R²={row['R²']*100:.1f}%, p={'<0.001' if row['P-value'] < 0.001 else f'{row['P-value']:.3f}'}"
        ax.text(row['R²'] * 100 + 0.3, i, text, va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('Viz/search_indicators_ranking.png', dpi=300, bbox_inches='tight')
    print("  OK Saved: Viz/search_indicators_ranking.png")
    plt.close()

    # 2. Temporal Trends - Search vs Economic Indicators
    print("-> Creating temporal trends visualization...")
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))

    # CCI over time
    axes[0].plot(master_df['date'], master_df['cci'], color='#3498db', linewidth=2)
    axes[0].set_ylabel('Consumer Confidence\nIndex', fontsize=11, fontweight='bold')
    axes[0].set_title('Economic Indicators Over Time', fontsize=13, fontweight='bold')
    axes[0].grid(alpha=0.3)
    axes[0].fill_between(master_df['date'], master_df['cci'], alpha=0.2, color='#3498db')

    # Shade recession periods
    for period, color in [('Great Recession', '#e74c3c'), ('COVID-19 Crisis', '#f39c12'),
                          ('Inflation Surge', '#9b59b6')]:
        period_df = master_df[master_df['period'] == period]
        if len(period_df) > 0:
            for ax in axes:
                ax.axvspan(period_df['date'].min(), period_df['date'].max(),
                          alpha=0.15, color=color, label=period)

    # Unemployment over time
    if 'unemployment_rate' in master_df.columns:
        axes[1].plot(master_df['date'], master_df['unemployment_rate'],
                    color='#e74c3c', linewidth=2)
        axes[1].set_ylabel('Unemployment\nRate (%)', fontsize=11, fontweight='bold')
        axes[1].grid(alpha=0.3)

    # Top search indicator over time
    top_indicator = search_results.iloc[0]['Indicator']
    if f'{top_indicator}_score' in master_df.columns:
        axes[2].plot(master_df['date'], master_df[f'{top_indicator}_score'],
                    color='#2ecc71', linewidth=2)
        axes[2].set_ylabel(f'{top_indicator}\nSearch Score', fontsize=11, fontweight='bold')
        axes[2].set_xlabel('Year', fontsize=11, fontweight='bold')
        axes[2].grid(alpha=0.3)

    axes[0].legend(loc='upper right', framealpha=0.9)
    plt.tight_layout()
    plt.savefig('Viz/temporal_trends.png', dpi=300, bbox_inches='tight')
    print("  OK Saved: Viz/temporal_trends.png")
    plt.close()

    # 3. Purchase Behavior - Category Distribution
    if retail_df is not None:
        print("-> Creating purchase behavior visualization...")
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Purchase type distribution
        purchase_summary = retail_df.groupby('purchase_type')['Total Spent'].sum().sort_values(ascending=False)
        colors_pie = ['#2ecc71', '#e74c3c', '#95a5a6']
        axes[0].pie(purchase_summary.values, labels=purchase_summary.index, autopct='%1.1f%%',
                   colors=colors_pie, startangle=90)
        axes[0].set_title('Spending Distribution by Purchase Type', fontsize=12, fontweight='bold')

        # Little luxury categories
        luxury_cats = retail_df[retail_df['purchase_type'] == 'Little Luxury'].groupby(
            'luxury_category')['Total Spent'].sum().sort_values(ascending=True)
        axes[1].barh(luxury_cats.index, luxury_cats.values, color='#3498db')
        axes[1].set_xlabel('Total Spending ($)', fontsize=11, fontweight='bold')
        axes[1].set_title('Little Luxury Categories', fontsize=12, fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig('Viz/purchase_behavior_analysis.png', dpi=300, bbox_inches='tight')
        print("  OK Saved: Viz/purchase_behavior_analysis.png")
        plt.close()

    # 4. Search vs Purchase Comparison
    print("-> Creating search vs purchase comparison...")
    overlap_df = comparison_df.dropna(subset=['luxury_spending'])

    if len(overlap_df) > 10:
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        # Normalize for dual axis
        cci_norm = (overlap_df['cci'] - overlap_df['cci'].min()) / (overlap_df['cci'].max() - overlap_df['cci'].min())
        spend_norm = (overlap_df['luxury_spending'] - overlap_df['luxury_spending'].min()) / (overlap_df['luxury_spending'].max() - overlap_df['luxury_spending'].min())

        axes[0].plot(overlap_df['date'], cci_norm, label='Consumer Confidence (normalized)',
                    color='#3498db', linewidth=2, marker='o', markersize=4)
        axes[0].plot(overlap_df['date'], spend_norm, label='Luxury Spending (normalized)',
                    color='#2ecc71', linewidth=2, marker='s', markersize=4)
        axes[0].set_ylabel('Normalized Values', fontsize=11, fontweight='bold')
        axes[0].set_title('Consumer Confidence vs Actual Luxury Spending\n(Normalized Comparison)',
                         fontsize=13, fontweight='bold')
        axes[0].legend(loc='best')
        axes[0].grid(alpha=0.3)

        # Scatter plot
        axes[1].scatter(overlap_df['cci'], overlap_df['luxury_spending'],
                       alpha=0.6, s=100, color='#9b59b6')

        # Add regression line
        z = np.polyfit(overlap_df['cci'], overlap_df['luxury_spending'], 1)
        p = np.poly1d(z)
        axes[1].plot(overlap_df['cci'], p(overlap_df['cci']), "r--", linewidth=2, alpha=0.8)

        corr, p_val = stats.pearsonr(overlap_df['cci'], overlap_df['luxury_spending'])
        axes[1].text(0.05, 0.95, f'r = {corr:.3f}\np = {p_val:.4f}',
                    transform=axes[1].transAxes, fontsize=12, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        axes[1].set_xlabel('Consumer Confidence Index', fontsize=11, fontweight='bold')
        axes[1].set_ylabel('Luxury Spending ($)', fontsize=11, fontweight='bold')
        axes[1].set_title('Correlation: Consumer Confidence vs Luxury Spending',
                         fontsize=13, fontweight='bold')
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig('Viz/search_vs_purchase_comparison.png', dpi=300, bbox_inches='tight')
        print("  OK Saved: Viz/search_vs_purchase_comparison.png")
        plt.close()

    print("\nOK All visualizations created successfully!")


# ========================================================================================================
# PART 6: TABLEAU DATA EXPORT
# ========================================================================================================

def export_tableau_data(master_df, search_results, retail_df, monthly_purchase_summary,
                       price_analysis, comparison_df):
    """Export comprehensive datasets for Tableau"""
    print("\n" + "="*100)
    print("PART 6: EXPORTING TABLEAU-READY DATASETS")
    print("="*100)

    # 1. Main time series data
    tableau_main = master_df.copy()
    print(f"\n-> Tableau Main Data: {len(tableau_main)} rows × {len(tableau_main.columns)} columns")
    tableau_main.to_csv('Tableau_Data/tableau_main_data_final.csv', index=False)
    print("  OK Saved: Tableau_Data/tableau_main_data_final.csv")

    # 2. Search results summary
    search_results['Category'] = search_results['Indicator'].map({
        'Indie Sleaze': 'Fashion',
        'Lipstick Index': 'Beauty & Cosmetics',
        'Maxi Skirt': 'Fashion',
        'Big Bag': 'Accessories',
        'High Heel Index': 'Fashion',
        'Peplums': 'Fashion',
        'Blazers': 'Fashion',
        'Mini Skirts': 'Fashion'
    })
    search_results['Data_Type'] = 'Search Behavior'
    print(f"\n-> Search Results: {len(search_results)} indicators")
    search_results.to_csv('Tableau_Data/tableau_search_results.csv', index=False)
    print("  OK Saved: Tableau_Data/tableau_search_results.csv")

    # 3. Purchase behavior summary
    if retail_df is not None and monthly_purchase_summary is not None:
        monthly_purchase_summary['Data_Type'] = 'Purchase Behavior'
        print(f"\n-> Purchase Summary: {len(monthly_purchase_summary)} month-category combinations")
        monthly_purchase_summary.to_csv('Tableau_Data/tableau_purchase_summary.csv', index=False)
        print("  OK Saved: Tableau_Data/tableau_purchase_summary.csv")

        # 4. Price analysis
        price_analysis['Data_Type'] = 'Price Analysis'
        print(f"\n-> Price Analysis: {len(price_analysis)} price ranges")
        price_analysis.to_csv('Tableau_Data/tableau_price_analysis.csv', index=False)
        print("  OK Saved: Tableau_Data/tableau_price_analysis.csv")

    # 5. Comparison dataset (search vs purchase)
    if comparison_df is not None:
        comparison_export = comparison_df.dropna(subset=['luxury_spending'])
        if len(comparison_export) > 0:
            print(f"\n-> Search vs Purchase Comparison: {len(comparison_export)} overlapping months")
            comparison_export.to_csv('Tableau_Data/tableau_search_vs_purchase.csv', index=False)
            print("  OK Saved: Tableau_Data/tableau_search_vs_purchase.csv")

    # 6. Category analysis by period
    if retail_df is not None:
        retail_df_copy = retail_df.copy()
        retail_df_copy['year'] = retail_df_copy['Transaction Date'].dt.year
        retail_df_copy['quarter'] = retail_df_copy['Transaction Date'].dt.quarter

        category_period = retail_df_copy.groupby(['year', 'quarter', 'luxury_category']).agg({
            'Total Spent': ['sum', 'mean', 'count'],
            'Customer ID': 'nunique'
        }).reset_index()
        category_period.columns = ['year', 'quarter', 'luxury_category', 'total_spent',
                                   'avg_spent', 'transaction_count', 'unique_customers']

        print(f"\n-> Category by Period: {len(category_period)} year-quarter-category combinations")
        category_period.to_csv('Tableau_Data/tableau_category_by_period.csv', index=False)
        print("  OK Saved: Tableau_Data/tableau_category_by_period.csv")

    print("\nOK All Tableau datasets exported successfully!")
    print("\n TABLEAU DASHBOARD STRUCTURE:")
    print("  Dashboard 1 - Temporal Trends: Use Tableau_Data/tableau_main_data_final.csv")
    print("  Dashboard 2 - Category Comparison: Use Tableau_Data/tableau_search_results.csv + Tableau_Data/tableau_purchase_summary.csv")
    print("  Dashboard 3 - Correlation Explorer: Use Tableau_Data/tableau_search_vs_purchase.csv")
    print("  Dashboard 4 - Price & Demographics: Use Tableau_Data/tableau_price_analysis.csv + Tableau_Data/tableau_category_by_period.csv")


# ========================================================================================================
# MAIN EXECUTION
# ========================================================================================================

def main():
    """Main analysis workflow"""

    # PART 1: Load all data
    google_trends_df = load_google_trends_data()
    fred_data = load_fred_data()
    retail_df = load_retail_transactions()
    master_df = integrate_all_data(google_trends_df, fred_data)

    # PART 2: Search behavior analysis
    indicators_dict = {
        'Indie Sleaze': ['indiesleaze_skinnyjeans', 'indiesleaze_cheetahprint', 'indiesleaze_furcoat',
                        'indiesleaze_leatherskirt', 'indiesleaze_discopants'],
        'Lipstick Index': ['lipstickindex_lipstick', 'lipstickindex_lip_stick', 'lipstickindex_lipgloss',
                          'lipstickindex_lipliner', 'lipstickindex_liptint'],
        'Maxi Skirt': ['maxiskirt_maxiskirt', 'maxiskirt_longskirt', 'maxiskirt_bohoskirt',
                      'maxiskirt_maxidress', 'maxiskirt_longdress'],
        'Big Bag': ['bigbag_hobobag', 'bigbag_oversizedbag', 'bigbag_totebag',
                   'bigbag_neverfull', 'bigbag_balenciagacitybag'],
        'High Heel Index': ['highheelindex_highheels', 'highheelindex_stilletoheel', 'highheelindex_platforms',
                           'highheelindex_platformheels', 'highheelindex_pumps'],
        'Peplums': ['peplums_peplum', 'peplums_peplumtops', 'peplums_peplumdress',
                   'peplums_rufflewaist', 'peplums_peplumblazer'],
        'Blazers': ['blazers_blazer', 'blazers_womensblazer', 'blazers_oversizedblazer',
                   'blazers_boyfriendblazer', 'blazers_croppedblazer'],
        'Mini Skirts': ['mini_miniskirt', 'mini_minidress', 'mini_micromini',
                       'mini_microshort', 'mini_micominiskirt']
    }

    scores_df = create_latent_variables(google_trends_df, indicators_dict)
    master_df = master_df.merge(scores_df[[col for col in scores_df.columns if col.endswith('_score')]],
                                left_index=True, right_index=True, how='left')

    search_results = analyze_search_correlations(scores_df)

    # PART 3: Purchase behavior analysis
    monthly_purchase_summary = None
    price_analysis = None

    if retail_df is not None:
        retail_df = categorize_little_luxuries(retail_df)
        monthly_purchase_summary, luxury_ratio = analyze_purchase_patterns(retail_df)
        price_analysis = analyze_price_points(retail_df)

    # PART 4: Compare search vs purchase
    comparison_df = None
    if retail_df is not None and monthly_purchase_summary is not None:
        comparison_df = compare_search_vs_purchase(master_df, monthly_purchase_summary)

    # PART 5: Create visualizations
    create_visualizations(master_df, search_results, retail_df, comparison_df)

    # PART 6: Export for Tableau
    export_tableau_data(master_df, search_results, retail_df, monthly_purchase_summary,
                       price_analysis, comparison_df)

    # Save master dataset
    print("\n" + "="*100)
    print("SAVING COMPLETE DATASET")
    print("="*100)
    # Save processed datasets (intermediate outputs)
    import os
    os.makedirs('Processed_Data', exist_ok=True)
    
    master_df.to_csv('Processed_Data/master_dataset_complete.csv', index=False)
    print(f"\nOK Master dataset saved: Processed_Data/master_dataset_complete.csv ({len(master_df)} rows × {len(master_df.columns)} columns)")

    search_results.to_csv('Processed_Data/search_indicators_results_final.csv', index=False)
    print(f"OK Search results saved: Processed_Data/search_indicators_results_final.csv")

    if retail_df is not None:
        retail_df.to_csv('Processed_Data/retail_transactions_processed.csv', index=False)
        print(f"OK Retail data saved: Processed_Data/retail_transactions_processed.csv")

    # Final summary
    print("\n" + "="*100)
    print(" "*35 + "ANALYSIS COMPLETE!")
    print("="*100)
    print(f"\nCompletion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n KEY FINDINGS:")
    print(f"  - Search Indicators: {search_results['Significant'].value_counts().get('Yes', 0)}/{len(search_results)} significant")
    print(f"  - Top Predictor: {search_results.iloc[0]['Indicator']} (R² = {search_results.iloc[0]['R²']*100:.1f}%)")
    if retail_df is not None:
        luxury_pct = len(retail_df[retail_df['purchase_type'] == 'Little Luxury']) / len(retail_df) * 100
        print(f"  - Little Luxury Purchases: {luxury_pct:.1f}% of all transactions")
    print("\nOK Ready for Tableau dashboard creation")
    print("OK Ready for final report writing")
    print("\n" + "="*100)


if __name__ == "__main__":
    main()
