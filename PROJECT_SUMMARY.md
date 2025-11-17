# Little Luxuries Project - Analysis Summary

## Overview

This analysis converts the R recession indicators script to Python and prepares data for your Tableau dashboards. It directly addresses your research question: **"Can Fashion and Beauty Trends Actually Predict Economic Sentiment?"**

## Key Findings

### ✅ 7 out of 8 Indicators Are Statistically Significant

**Top Predictors:**
1. **Mini Skirts** - 17.4% variance explained (p < 0.000001) 🥇
2. **Big Bag** - 15.4% variance explained (p < 0.000001) 🥈
3. **Indie Sleaze** - 11.4% variance explained (p < 0.000001) 🥉

**Also Significant:**
- Blazers - 9.5% variance
- High Heel Index - 9.5% variance
- Maxi Skirt - 2.9% variance
- Peplums - 2.2% variance

**Not Significant:**
- Lipstick Index - 0.0% variance (p = 0.92) ❌

### 🔍 Critical Discovery: Inverse Relationship

**All significant indicators show NEGATIVE correlations** with Consumer Confidence Index:
- When fashion trend searches **INCREASE** ↗️
- Consumer confidence **DECREASES** ↘️

This contradicts the traditional "Lipstick Effect" theory and suggests:
- **Search behavior ≠ Purchase behavior** during economic uncertainty
- People browse more when anxious, but may not actually buy
- Google Trends captures *aspiration* and *window shopping*, not consumption

## Files Created

### Core Analysis Files
1. **`recession_indicators_analysis.py`** - Main analysis script (converts R to Python)
2. **`data_with_scores.csv`** - Full dataset with latent variable scores (252 months)
3. **`recession_indicators_results.csv`** - Summary of all regression results
4. **`scatter_plots_all.png`** - Scatter plots for all indicators
5. **`summary_chart.png`** - Bar chart ranking indicators by R-squared

### Tableau Dashboard Files
6. **`tableau_temporal_trends.csv`** - For Temporal Trends Dashboard (2,016 rows)
7. **`tableau_category_comparison.csv`** - For Category Comparison Dashboard (8 rows)
8. **`tableau_correlation_explorer.csv`** - For Correlation Explorer Dashboard (2,016 rows)
9. **`tableau_correlation_metrics.csv`** - Correlation summary metrics (8 rows)
10. **`tableau_summary_stats.csv`** - KPI summary statistics
11. **`tableau_lagged_analysis.csv`** - For predictive/leading indicator analysis (252 rows)

### Integration Files
12. **`integrated_dataset_template.csv`** - Template for merging with retail sales data
13. **`category_summary.csv`** - Category-level summary with groupings
14. **`INTEGRATION_INSTRUCTIONS.md`** - Step-by-step integration guide

### Documentation
15. **`README.md`** - Complete documentation
16. **`PROJECT_SUMMARY.md`** - This file
17. **`requirements.txt`** - Python package dependencies

## How This Fits Your Project

### Research Questions Addressed

✅ **"Can Fashion and Beauty Trends Actually Predict Economic Sentiment?"**
- YES! 7 indicators show significant predictive power
- Mini Skirts and Big Bag are strongest predictors (17.4% and 15.4% variance)

✅ **"Does Consumer Behavior Really Follow the 'Lipstick Effect'?"**
- NO - The traditional Lipstick Index shows NO significant relationship (p = 0.92)
- However, OTHER indicators (Mini Skirts, Big Bag, Blazers) DO show relationships
- The relationship is INVERSE - searches increase when confidence decreases

✅ **"How Has 'Treatonomics' Evolved Beyond Traditional Categories?"**
- Fashion trends (Mini Skirts, Blazers, Indie Sleaze) are stronger predictors than beauty
- Accessories (Big Bag, High Heels) show significant relationships
- The "new lipstick" appears to be fashion items, not cosmetics

### Dashboard Integration

**Temporal Trends Dashboard:**
- Use `tableau_temporal_trends.csv`
- Shows time-series patterns of trend scores vs. CCI
- Includes economic period markers (Great Recession, COVID, etc.)
- Ready for dual-axis line charts

**Category Comparison Dashboard:**
- Use `tableau_category_comparison.csv`
- Shows R-squared, significance levels, correlation directions
- Includes category groupings (Fashion Trends, Beauty & Cosmetics, Accessories)
- Ready for bubble plots and bar charts

**Correlation Explorer Dashboard:**
- Use `tableau_correlation_explorer.csv` and `tableau_correlation_metrics.csv`
- Shows scatter plots with CCI vs. trend scores
- Includes correlation coefficients and p-values
- Ready for interactive exploration with regression overlays

### Next Steps

1. **Import Tableau files into your dashboards**
   - Each CSV is formatted specifically for its corresponding dashboard
   - Column names are Tableau-friendly
   - Data is in optimal format (long format for temporal, wide for comparisons)

2. **Integrate with retail sales data**
   - Use `integrated_dataset_template.csv` as base
   - Follow `INTEGRATION_INSTRUCTIONS.md` for merging steps
   - Add your retail sales, e-commerce transactions, and category-level sales

3. **Create calculated fields in Tableau**
   - Luxury Ratio: Normalized sum of trend scores
   - Affordability Index: 100 - CCI
   - Category Concentration: Standard deviation of category scores
   - Trend Score Normalized: Min-max normalization

4. **Build your dashboards**
   - Temporal Trends: Dual-axis line charts with filters
   - Category Comparison: Bubble plots with size = R-squared, color = significance
   - Correlation Explorer: Scatter plots with regression lines and tooltips

## Methodology

### Structural Equation Modeling (SEM)
- Uses Factor Analysis to create latent variables from multiple search terms
- Iteratively removes variables with poor factor loadings (< 0.3 or > 0.95)
- Extracts latent scores representing overall trend strength

### Regression Analysis
- Tests correlation between latent scores and Consumer Confidence Index
- Calculates R-squared, p-values, coefficients
- Identifies statistically significant relationships (p < 0.05)

### Data Cleaning
- Automatically fixes CCI data issues (missing decimal points)
- Handles missing values and outliers
- Standardizes variables for analysis

## Key Insights for Your Project

1. **The Lipstick Effect is Dead (or Evolved)**
   - Traditional lipstick index shows no relationship
   - Modern "lipstick" = fashion items (mini skirts, blazers, bags)

2. **Search Behavior ≠ Purchase Behavior**
   - Inverse relationship suggests browsing increases during uncertainty
   - Google Trends captures aspiration, not consumption
   - Important distinction for retailers and economists

3. **Fashion Trends Are Strong Predictors**
   - Mini Skirts: 17.4% variance explained
   - Big Bag: 15.4% variance explained
   - These could serve as leading indicators

4. **Price Point Matters**
   - Accessories and fashion items (affordable luxuries) show strongest relationships
   - Suggests consumers seek small indulgences during uncertainty

## For Your Presentation

### Key Talking Points:
- "We tested 8 recession indicators and found 7 are statistically significant"
- "Mini Skirts and Big Bag explain 17% and 15% of variance in consumer confidence"
- "The traditional Lipstick Index shows no relationship - the 'lipstick' has evolved"
- "We discovered an inverse relationship: searches increase when confidence decreases"
- "This suggests search behavior (browsing) differs from purchase behavior"

### Visualizations to Highlight:
- Summary chart showing R-squared rankings
- Scatter plots showing inverse relationships
- Temporal trends showing spikes during economic downturns
- Category comparison showing Fashion Trends dominate

## Technical Notes

- **Data Period**: January 2004 - December 2024 (252 months)
- **Method**: Factor Analysis + Linear Regression
- **Significance Threshold**: p < 0.05
- **Software**: Python (pandas, sklearn, statsmodels) → Tableau

## Questions for Further Analysis

1. Can we predict CCI changes using lagged trend scores? (See `tableau_lagged_analysis.csv`)
2. How do these patterns differ by demographic? (Requires integration with retail data)
3. Do actual sales follow the same patterns as search trends? (Requires retail sales data)
4. Which price points show strongest relationships? (Requires price data integration)

---

**Ready for Tableau!** All data files are formatted and ready to import into your dashboards.

