# Recession Indicators Analysis - Python Version

**Part of the "Little Luxuries" Project - Testing Fashion Trends as Recession Indicators**

This Python script replicates the R analysis for testing fashion trends as recession indicators using Google Trends data and Consumer Confidence Index (CCI). This analysis directly addresses the project's research question: **"Can Fashion and Beauty Trends Actually Predict Economic Sentiment?"**

## Overview

The analysis tests **8 different recession indicators**:
1. **Indie Sleaze** (skinny jeans, cheetah print, leather skirt, disco pants)
2. **Lipstick Index** (lipstick, lip stick, lipgloss, lipliner, liptint)
3. **Maxi Skirt** (maxi skirt, long skirt, boho skirt, maxi dress, long dress)
4. **Big Bag** (hobo bag, tote bag, neverfull, Balenciaga city bag)
5. **High Heel Index** (high heels, stiletto heel, platforms, platform heels, pumps)
6. **Peplums** (peplum tops, peplum dress, peplum blazer, ruffle waist)
7. **Blazers** (blazer, women's blazer, oversized blazer, boyfriend blazer, cropped blazer)
8. **Mini Skirts** (mini skirt, mini dress, micro mini, micro short, micro mini skirt)

## Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas numpy scipy scikit-learn statsmodels matplotlib seaborn openpyxl
```

## Usage

Simply run the script:

```bash
python recession_indicators_analysis.py
```

## What the Script Does

### 1. Data Loading and Cleaning
- Loads data from `All_Variables_Us_Data_Sheet1.xlsx`
- Removes commas from numeric values
- Fixes CCI data issues (missing decimal points)
- Standardizes variables for analysis

### 2. SEM Analysis (Structural Equation Modeling)
For each indicator:
- Creates a latent variable from multiple search terms using Factor Analysis
- Iteratively removes variables with poor factor loadings (< 0.3 or > 0.95)
- Extracts latent scores representing the overall trend

### 3. Regression Analysis
- Tests correlation between each indicator's latent score and Consumer Confidence Index
- Calculates R-squared, p-values, and coefficients
- Identifies statistically significant relationships (p < 0.05)

### 4. Visualizations
- Creates scatter plots for all indicators showing relationship with CCI
- Generates summary bar chart ranking indicators by R-squared

## Output Files

1. **`recession_indicators_results.csv`** - Summary table with all regression results
2. **`data_with_scores.csv`** - Full dataset with latent variable scores added
3. **`scatter_plots_all.png`** - Scatter plots for all indicators
4. **`summary_chart.png`** - Bar chart ranking indicators by variance explained

## Key Findings

Based on the analysis:

**Top Predictors:**
1. 🥇 **Mini Skirts** - 17.4% variance explained (p < 0.000001)
2. 🥈 **Big Bag** - 15.4% variance explained (p < 0.000001)
3. 🥉 **Indie Sleaze** - 11.4% variance explained (p < 0.000001)

**Also Significant:**
- **Blazers** - 9.5% variance (p < 0.000001)
- **High Heel Index** - 9.5% variance (p < 0.000001)
- **Maxi Skirt** - 2.9% variance (p < 0.01)
- **Peplums** - 2.2% variance (p < 0.05)

**Not Significant:**
- **Lipstick Index** - 0.0% variance (p = 0.92)

### Important Finding: Inverse Relationship

All significant indicators show **NEGATIVE** correlations, meaning:
- When fashion trend search interest **increases** ↗️
- Consumer confidence **decreases** ↘️

This is the **opposite** of the traditional "Lipstick Effect" theory and suggests that search behavior (browsing) increases during economic uncertainty, even if actual purchases don't.

## Differences from R Version

This Python version uses:
- **Factor Analysis** (sklearn) instead of lavaan's SEM
- **Automatic variable removal** based on factor loadings
- **statsmodels** for regression analysis

Results may vary slightly from the R version due to different optimization algorithms, but the overall patterns and significance should be consistent.

## Notes

- The script automatically handles missing data and problematic variables
- CCI values with missing decimal points are automatically corrected
- Variables with poor factor loadings are iteratively removed
- All significant relationships show inverse correlations with CCI

## Troubleshooting

If you encounter errors:

1. **Missing packages**: Run `pip install -r requirements.txt`
2. **File not found**: Ensure `All_Variables_Us_Data_Sheet1.xlsx` is in the same directory
3. **Memory issues**: The script processes 252 months of data - ensure sufficient RAM

## Integration with Project Datasets

This analysis is part of a larger project analyzing "treatonomics" and consumer behavior. To integrate with your other datasets:

1. **Run the Tableau preparation script:**
   ```bash
   python prepare_tableau_data.py
   ```
   This creates Tableau-ready CSV files for your three dashboards.

2. **Integrate with retail sales data:**
   ```bash
   python integrate_datasets.py
   ```
   This creates an integration template and instructions for merging with your retail sales and e-commerce datasets.

3. **Import into Tableau:**
   - Use `tableau_temporal_trends.csv` for Temporal Trends Dashboard
   - Use `tableau_category_comparison.csv` for Category Comparison Dashboard
   - Use `tableau_correlation_explorer.csv` for Correlation Explorer Dashboard

See `INTEGRATION_INSTRUCTIONS.md` for detailed steps on merging with your other datasets.

## Project Context

This analysis supports the "Little Luxuries" project by:
- **Verifying the Lipstick Effect**: Testing whether traditional recession indicators hold up with modern data
- **Identifying Modern Treat Categories**: Determining which fashion/beauty categories show counter-cyclical behavior
- **Exploring Predictive Power**: Testing whether search trends can serve as leading indicators of economic sentiment
- **Supporting Dashboard Creation**: Providing data formatted specifically for Tableau visualization

## Key Insights & Hypothesis Alignment

### Summary of Findings

**Hypothesis 1: Does Consumer Behavior Follow the 'Lipstick Effect'?**
- ❌ **REJECTED** for traditional Lipstick Index (R² = 0.00%, p = 0.92)
- ✅ **SUPPORTED** for modern indicators (7 out of 8 are significant)
- **Conclusion**: The "lipstick" has evolved from cosmetics to fashion trends

**Hypothesis 2: How Has 'Treatonomics' Evolved Beyond Traditional Categories?**
- ✅ **CONFIRMED**: Modern little luxuries have shifted categories
- **Top Category**: Fashion Trends (8.68% avg R², 5 significant indicators)
- **Second**: Accessories (12.44% avg R², 2 significant indicators)
- **Bottom**: Beauty & Cosmetics (0.00% avg R², 0 significant indicators)

**Hypothesis 3: Can Fashion Trends Predict Economic Sentiment?**
- ✅ **STRONGLY SUPPORTED**: 7 out of 8 indicators are significant predictors
- **Top Predictor**: Mini Skirts (17.4% variance explained)
- **Critical Discovery**: All relationships are INVERSE (searches ↑ when confidence ↓)

### Critical Discovery: Inverse Relationship

All significant indicators show **NEGATIVE** correlations with Consumer Confidence:
- When fashion trend searches **INCREASE** → Consumer confidence **DECREASES**
- This contradicts traditional "Lipstick Effect" theory
- **Implication**: Search behavior ≠ Purchase behavior
- People browse more when anxious, but may not actually buy

See `KEY_INSIGHTS.txt` for detailed analysis.

## Project Status

### ✅ Completed

#### Data Analysis & Processing
- [x] Converted R script to Python (`recession_indicators_analysis.py`)
- [x] Data loading and cleaning (handles Excel format, fixes CCI data issues)
- [x] SEM analysis using Factor Analysis for all 8 indicators
- [x] Regression analysis testing correlation with Consumer Confidence Index
- [x] Statistical significance testing (7 out of 8 indicators significant)
- [x] Feature engineering (luxury ratio, affordability index, category concentration)

#### Visualizations Created
- [x] Basic scatter plots for all indicators (`scatter_plots_all.png`)
- [x] Summary bar chart ranking indicators (`summary_chart.png`)
- [x] Hypothesis alignment analysis (`hypothesis_alignment_analysis.png`)
- [x] Temporal insights visualization (`temporal_insights_analysis.png`)
- [x] Comparison insights (`comparison_insights.png`)

#### Data Preparation for Tableau
- [x] Temporal trends dataset (`tableau_temporal_trends.csv`)
- [x] Category comparison dataset (`tableau_category_comparison.csv`)
- [x] Correlation explorer dataset (`tableau_correlation_explorer.csv`)
- [x] Correlation metrics summary (`tableau_correlation_metrics.csv`)
- [x] Summary statistics (`tableau_summary_stats.csv`)
- [x] Lagged analysis dataset for predictive analysis (`tableau_lagged_analysis.csv`)

#### Integration & Documentation
- [x] Integration template for merging with retail sales data (`integrated_dataset_template.csv`)
- [x] Integration instructions (`INTEGRATION_INSTRUCTIONS.md`)
- [x] Category summary with groupings (`category_summary.csv`)
- [x] Key insights document (`KEY_INSIGHTS.txt`)
- [x] Project summary (`PROJECT_SUMMARY.md`)
- [x] Complete README documentation

### 🔄 In Progress / Next Steps

#### Purchasing Behavior Data Integration
- [ ] Load retail sales data (Fashion Boutique Sales Data 2025)
- [ ] Load e-commerce transactions dataset
- [ ] Clean and preprocess retail sales data
- [ ] Merge retail sales with recession indicators data
- [ ] Compare search trends vs. actual purchase behavior
- [ ] Test if browsing (Google Trends) translates to buying (retail sales)

#### Additional Analysis
- [ ] Demographic segmentation analysis (age, income brackets)
- [ ] Price point analysis (affordability index by category)
- [ ] Seasonal pattern analysis (holiday effects, seasonal trends)
- [ ] Lag analysis to test leading indicator properties
- [ ] Category concentration analysis (spending clustering)

#### Tableau Dashboard Development
- [ ] **Temporal Trends Dashboard**
  - [ ] Import `tableau_temporal_trends.csv`
  - [ ] Create dual-axis line charts (CCI vs. trend scores)
  - [ ] Add economic period filters
  - [ ] Add interactive time range selector
  - [ ] Add tooltips with key metrics

- [ ] **Category Comparison Dashboard**
  - [ ] Import `tableau_category_comparison.csv`
  - [ ] Create bubble plots (size = R², color = significance)
  - [ ] Add category grouping filters
  - [ ] Create bar charts for luxury ratio by category
  - [ ] Add demographic comparison views

- [ ] **Correlation Explorer Dashboard**
  - [ ] Import `tableau_correlation_explorer.csv`
  - [ ] Create scatter plots with regression lines
  - [ ] Add correlation coefficient displays
  - [ ] Add lag adjustment parameters (3-month, 6-month)
  - [ ] Create heatmap of correlation matrix

#### Final Deliverables
- [ ] Complete Tableau workbook with all 3 dashboards
- [ ] Story points/narrative flow in Tableau
- [ ] Final report summarizing all findings
- [ ] Presentation slides
- [ ] Video walkthrough of dashboards

### 📋 Data Requirements (To Be Added)

#### Retail Sales Data
- Transaction dates (monthly aggregation needed)
- Product categories (map to fashion/beauty/accessories)
- Price points
- Customer demographics (age, income brackets)
- Purchase frequency

#### E-Commerce Data
- Category-level sales volumes
- Timestamp data (monthly aggregation)
- Customer segments
- Seasonal patterns

#### Integration Tasks
- Temporal alignment (aggregate to monthly intervals)
- Category standardization (unified taxonomy)
- Price normalization (inflation adjustment using CPI)
- Feature engineering:
  - Luxury ratio: non-essential spending / total spending
  - Affordability index: price relative to income
  - Category concentration: spending clustering metrics

### 🎯 Key Research Questions to Address with Purchase Data

1. **Does browsing translate to buying?**
   - Compare Google Trends (search) vs. Retail Sales (purchase)
   - Test if inverse relationship holds for actual purchases

2. **Price point analysis**
   - What price range defines "affordable indulgence"?
   - Do lower-priced items show stronger relationships?

3. **Demographic differences**
   - How do age groups differ in little luxury spending?
   - Do income brackets affect the relationship?

4. **Category evolution**
   - Which categories show strongest counter-cyclical behavior?
   - Has the "lipstick" truly shifted to fashion items?

## Citation

If using this analysis, please acknowledge:
- Google Trends data for search term volumes
- Consumer Confidence Index (CCI) data
- Structural Equation Modeling approach for latent variable creation

