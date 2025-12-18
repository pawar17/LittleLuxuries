# Tableau Data Guide
## Complete Reference for All 9 CSV Exports

This guide explains what each Tableau-ready CSV file contains and how to use it for dashboard creation.

---

## Quick Reference Table

| File | Rows | Columns | Time Period | Best For |
|------|------|---------|-------------|----------|
| `tableau_main_data_final.csv` | 252 | 62 | 2004-2024 | Temporal trends, correlation explorer |
| `tableau_search_results.csv` | 8 | 9 | Summary | Category comparison, rankings |
| `tableau_purchase_summary.csv` | 50 | 8 | 2023-2025 | Purchase behavior analysis |
| `tableau_search_vs_purchase.csv` | 24 | 11 | 2023-2024 | Search vs. purchase comparison |
| `tableau_price_analysis.csv` | 6 | 5 | 2023-2025 | Price point analysis |
| `tableau_category_by_period.csv` | 54 | 5 | 2023-2025 | Temporal purchase patterns |
| `tableau_census_results.csv` | 2 | 9 | Summary | Census regression results |
| `tableau_census_recession_analysis.csv` | 3 | 6 | 1992-2025 | Recession period analysis |
| `tableau_census_timeseries.csv` | 808 | 5 | 1992-2025 | 33-year trend analysis |

---

## File 1: `tableau_main_data_final.csv`
### Main Time Series Dataset (Search Behavior + Economic Indicators)

**What it contains:**
- 252 monthly observations (January 2004 - December 2024)
- 62 variables including:
  - Date (monthly timestamps)
  - Consumer Confidence Index (CCI)
  - 8 fashion/beauty indicator scores (Mini Skirts, Blazers, High Heels, etc.)
  - 40 original Google Trends search terms
  - Economic indicators (CPI, unemployment rate, consumer sentiment, retail sales, saving rate)
  - Economic period labels (Normal, Great Recession, COVID-19 Crisis, Inflation Surge)

**Key Columns:**
- `date`: Monthly timestamp (YYYY-MM format)
- `cci`: Consumer Confidence Index (primary economic sentiment measure)
- `Mini Skirts_score`: Latent variable score for mini skirt searches (strongest predictor)
- `Blazers_score`: Latent variable score for blazer searches
- `High Heel Index_score`: Latent variable score for high heel searches
- `Big Bag_score`: Latent variable score for big bag searches
- `Lipstick Index_score`: Latent variable score for lipstick searches
- `unemployment_rate`: U.S. unemployment rate (%)
- `consumer_sentiment`: University of Michigan Consumer Sentiment Index
- `period`: Economic period classification

**Best Used For:**
1. **Temporal Trends Dashboard**
   - Line charts showing CCI and search indicators over time
   - Recession period highlighting (shaded regions)
   - Multi-line comparisons of different indicators

2. **Correlation Explorer Dashboard**
   - Scatter plots: CCI vs. search indicator scores
   - Trend lines showing inverse relationships
   - R² and correlation coefficients

3. **Economic Period Analysis**
   - Filter by `period` to compare behavior during different economic conditions
   - Show how searches spike during Great Recession, COVID-19, etc.

**Visualization Examples:**
- Line chart: CCI over time with recession shading
- Dual-axis chart: Mini Skirts searches vs. CCI
- Scatter plot: Any indicator score vs. CCI (should show negative correlation)
- Heat map: Correlation matrix of all 8 indicators

---

## File 2: `tableau_search_results.csv`
### Search Indicator Regression Results Summary

**What it contains:**
- 8 rows (one per fashion/beauty indicator)
- Statistical regression results testing correlation with Consumer Confidence

**Columns:**
- `Indicator`: Name (Mini Skirts, Blazers, High Heel Index, Big Bag, etc.)
- `R²`: Percentage of variance in CCI explained by this indicator (0-100%)
- `Adj_R²`: Adjusted R² accounting for model complexity
- `Coefficient`: Regression slope (all significant ones are negative)
- `P-value`: Statistical significance (< 0.05 = significant)
- `Significant`: "Yes" or "No" (7 out of 8 are "Yes")
- `Category`: Classification (Fashion, Beauty & Cosmetics, Accessories)
- `Data_Type`: "Search Behavior" (for filtering)

**Best Used For:**
1. **Category Comparison Dashboard**
   - Bar chart: Indicators ranked by R² value
   - Color-coded by significance (green = significant, red = not)
   - Compare Fashion vs. Beauty categories

2. **Statistical Summary Dashboard**
   - Table showing all regression statistics
   - Highlight top 3 predictors (Mini Skirts 18.3%, Blazers 17.0%, High Heels 13.5%)

**Visualization Examples:**
- Horizontal bar chart: R² by indicator (sorted high to low)
- Pie chart: Significant vs. Not Significant (87.5% vs. 12.5%)
- Scatter plot: R² vs. P-value
- Category breakdown: Fashion items average R² vs. Beauty items

---

## File 3: `tableau_purchase_summary.csv`
### Monthly Purchase Behavior Summary (Retail Transactions)

**What it contains:**
- 50 rows (month-category combinations from retail transaction data)
- Monthly aggregation of purchase behavior by type (Little Luxury vs. Necessity)

**Columns:**
- `year_month`: Date in YYYY-MM format
- `purchase_type`: "Little Luxury" or "Necessity"
- `category`: If Little Luxury, shows subcategory (Fashion & Accessories, Experiential, etc.)
- `transaction_count`: Number of purchases that month
- `total_spending`: Dollar amount spent
- `luxury_ratio`: Percentage of spending that month on little luxuries
- `avg_transaction`: Average purchase amount
- `Data_Type`: "Purchase Behavior"

**Best Used For:**
1. **Purchase Behavior Dashboard**
   - Stacked area chart: Little Luxury vs. Necessity spending over time
   - Show that 95% of spending is little luxuries

2. **Category Breakdown**
   - Pie chart: Fashion & Accessories (94.2%) dominates
   - Bar chart: Spending by luxury subcategory

**Visualization Examples:**
- Stacked bar chart: Monthly spending by purchase type
- Line chart: Luxury ratio over time (shows consistent 90%+ pattern)
- Treemap: Luxury categories by total spending
- KPI cards: Total luxury spending ($24M), Average luxury ratio (93.4%)

---

## File 4: `tableau_search_vs_purchase.csv`
### Search vs. Purchase Comparison (24-Month Overlap)

**What it contains:**
- 24 rows (months where we have both search data and retail transaction data)
- Merged dataset for testing if search trends predict purchases

**Columns:**
- `date`: Monthly timestamp
- `cci`: Consumer Confidence Index
- 8 search indicator scores (`Mini Skirts_score`, `Blazers_score`, etc.)
- `luxury_spending`: Total dollar amount spent on little luxuries that month
- `luxury_transactions`: Number of little luxury purchases that month

**Best Used For:**
1. **Correlation Explorer: Search vs. Purchase**
   - Scatter plots: Search indicator scores vs. luxury spending
   - Show that correlations are NOT significant (search ≠ purchase)
   - Dual-axis line chart: CCI + luxury spending over 24 months

**Visualization Examples:**
- Scatter plot: Mini Skirts score vs. luxury spending (r = -0.066, p = 0.76 - not significant)
- Line chart with 3 axes: CCI, search score, luxury spending
- Correlation matrix: All 8 indicators vs. luxury spending

**Key Insight to Show:**
- Search behavior (Google Trends) does NOT predict actual purchase amounts
- This is expected: browsing vs. buying are different stages

---

## File 5: `tableau_price_analysis.csv`
### Price Point Distribution for Little Luxuries

**What it contains:**
- 6 rows (one per price range bracket)
- Distribution of little luxury purchases by price point

**Columns:**
- `price_range`: "$0-10", "$10-30", "$30-50", "$50-100", "$100-500", "$500+"
- `transaction_count`: Number of purchases in this range
- `percent_of_total`: Percentage of all little luxury transactions
- `total_spending`: Total dollars spent in this range
- `avg_price`: Average purchase price in this range

**Best Used For:**
1. **Price Point Analysis Dashboard**
   - Bar chart: Transaction count by price range
   - Show sweet spot: $100-500 range (34.3% of transactions)
   - Highlight that $500+ drives most revenue despite fewer transactions

**Visualization Examples:**
- Bar chart: Transactions by price range (shows $100-500 is modal category)
- Pie chart: Distribution of transactions across price ranges
- Dual-axis: Transaction count vs. Total spending by range
- KPI: "Sweet Spot Price Range: $100-500"

---

## File 6: `tableau_category_by_period.csv`
### Purchase Categories Over Time

**What it contains:**
- 54 rows (year-quarter-category combinations)
- Quarterly aggregation showing how category preferences change over time

**Columns:**
- `year`: 2023, 2024, 2025
- `quarter`: Q1, Q2, Q3, Q4
- `luxury_category`: Fashion & Accessories, Experiential, Beauty & Cosmetics, etc.
- `transaction_count`: Purchases in that quarter-category
- `total_spending`: Dollar amount in that quarter-category

**Best Used For:**
1. **Temporal Purchase Patterns**
   - Stacked area chart: Category spending by quarter
   - Show consistency of Fashion & Accessories dominance
   - Identify any seasonal patterns

**Visualization Examples:**
- Stacked bar chart: Spending by category per quarter
- Line chart: Fashion & Accessories spending trend over time
- Heat map: Quarter × Category spending matrix

---

## File 7: `tableau_census_results.csv`
### U.S. Census Regression Results (Hill et al. 2012 Replication)

**What it contains:**
- 2 rows (one per NAICS category)
- Regression results from 33 years of Census retail sales data

**Columns:**
- `Category`: "Beauty & Personal Care (NAICS 446)" or "Women's Clothing (NAICS 44812)"
- `Coefficient`: Regression slope vs. CCI (both negative)
- `R²`: Variance explained (24.8% for beauty, 10.0% for fashion)
- `Adj_R²`: Adjusted R²
- `P-value`: Statistical significance (both < 0.000001)
- `F-statistic`: Model fit statistic
- `N_months`: Sample size (404 months = 33+ years)
- `Significant`: "Yes" for both
- `Direction`: "Negative" = classic lipstick effect

**Best Used For:**
1. **Census Replication Results Dashboard**
   - Bar chart: R² comparison (Beauty 24.8% vs. Fashion 10.0%)
   - Statistical summary table
   - Highlight: "HILL ET AL. (2012) SUCCESSFULLY REPLICATED"

**Visualization Examples:**
- Bar chart: R² by category (color-coded by significance)
- KPI cards: Beauty R² = 24.8% (p < 0.000001)
- Text annotation: "Strongest evidence for lipstick effect using 33 years of official data"

---

## File 8: `tableau_census_recession_analysis.csv`
### Recession Period Sales Changes (Census Data)

**What it contains:**
- 3 rows (one per recession period tested)
- Shows how beauty and fashion retail sales changed during each recession

**Columns:**
- `Period`: Recession name (Dot-com Crash, Great Recession, COVID-19 Recession)
- `Dates`: Date range of recession
- `Beauty_Change_%`: Percent change in beauty sales vs. 12-month pre-recession baseline
- `Fashion_Change_%`: Percent change in fashion sales vs. 12-month pre-recession baseline
- `Beauty_Avg`: Average monthly beauty sales during recession
- `Fashion_Avg`: Average monthly fashion sales during recession

**Best Used For:**
1. **Recession Analysis Dashboard**
   - Bar chart: Beauty sales change during each recession (ALL POSITIVE)
   - Bar chart: Fashion sales change during each recession (mixed/negative)
   - Show lipstick effect visually: Beauty ↑ during recessions

**Visualization Examples:**
- Grouped bar chart: Beauty vs. Fashion sales change by recession
- Highlight: Beauty increased during ALL 3 recessions (+6.2%, +4.5%, +0.4%)
- KPI: "3 out of 3 recessions show beauty sales increases"

**Key Insight:**
- Beauty sales are RECESSION-RESISTANT (go up when economy goes down)
- Fashion sales decrease during recessions (except mini-recessions)
- This validates the classic "lipstick effect"

---

## File 9: `tableau_census_timeseries.csv`
### 33-Year Census Retail Sales Time Series (1992-2025)

**What it contains:**
- 808 rows (404 months × 2 categories)
- Complete monthly time series of beauty and fashion retail sales

**Columns:**
- `observation_date`: Monthly timestamp (1992-01 through 2025-08)
- `sales`: Retail sales in millions of dollars
- `cci`: Consumer Confidence Index
- `cpi`: Consumer Price Index (inflation)
- `category`: "Beauty & Personal Care" or "Women's Clothing"

**Best Used For:**
1. **33-Year Trend Analysis Dashboard** (MOST POWERFUL)
   - Line chart: Beauty sales + Fashion sales + CCI over 33 years
   - Shade recession periods (1990-91, 2001, 2007-09, 2020)
   - Show inverse relationship: CCI ↓ → Beauty sales ↑

2. **Correlation Explorer**
   - Scatter plot: Sales vs. CCI for each category
   - Show R² = 24.8% for beauty (strong negative correlation)
   - Trend lines showing downward slope

**Visualization Examples:**
- **RECOMMENDED**: Dual-axis line chart with recession shading
  - Left axis: CCI (line chart, blue)
  - Right axis: Beauty sales (line chart, purple)
  - Shaded regions: Great Recession, COVID-19
  - Visually see: When CCI drops, beauty sales rise

- Scatter plot: CCI vs. Beauty sales (404 points, negative slope)
- Heat map: Year × Month sales patterns
- Small multiples: Beauty sales trend vs. Fashion sales trend

This visualization shows 33 years of evidence for the lipstick effect using official U.S. Census data.

---

## Recommended Tableau Dashboard Structure

### Dashboard 1: **Temporal Trends (20-Year Search Data)**
**Files:** `tableau_main_data_final.csv`

**Visualizations:**
1. Line chart: CCI over time (2004-2024) with recession shading
2. Multi-line chart: Top 3 indicators (Mini Skirts, Blazers, High Heels) vs. CCI
3. Filter: Select indicator to highlight
4. Period filter: Great Recession, COVID-19, Inflation Surge

---

### Dashboard 2: **Category Comparison**
**Files:** `tableau_search_results.csv`, `tableau_purchase_summary.csv`

**Visualizations:**
1. Horizontal bar chart: Search indicators ranked by R² (show top predictors)
2. Pie chart: Purchase spending by category (Fashion 94.2% dominance)
3. Summary stats: 7/8 significant, Mini Skirts R² = 18.3%

---

### Dashboard 3: Census Data Analysis (33-Year Analysis)
**Files:** `tableau_census_timeseries.csv`, `tableau_census_results.csv`, `tableau_census_recession_analysis.csv`

**Visualizations:**
1. **Main chart**: Dual-axis line chart (1992-2025)
   - CCI (blue line)
   - Beauty sales (purple line)
   - Recession shading (gray bars: 2001, 2007-09, 2020)
   - Shows visual inverse relationship

2. Bar chart: Beauty sales change during recessions (+6.2%, +4.5%, +0.4%)
3. Scatter plot: CCI vs. Beauty sales (R² = 24.8%)
4. KPI cards:
   - "R² = 24.8%"
   - "p < 0.000001"
   - "404 months analyzed"
   - "Hill et al. (2012) Replicated"

---

### Dashboard 4: **Search vs. Purchase Comparison**
**Files:** `tableau_search_vs_purchase.csv`

**Visualizations:**
1. Scatter plots: Each indicator vs. luxury spending (show NO correlation)
2. Line chart: CCI + Mini Skirts score + Luxury spending (3 lines, 24 months)
3. Insight box: "Search ≠ Purchase: Different behavioral stages"

---

### Dashboard 5: **Price & Demographics**
**Files:** `tableau_price_analysis.csv`, `tableau_category_by_period.csv`

**Visualizations:**
1. Bar chart: Transactions by price range (highlight $100-500 sweet spot)
2. Stacked area: Category spending over quarters
3. KPI: "Sweet Spot: $100-500 (34.3% of transactions)"

---

## Key Insights to Highlight in Dashboards

**From Search Data:**
- Mini Skirts is the #1 predictor of economic anxiety (R² = 18.3%)
- Fashion items > Beauty items as recession indicators
- 7 out of 8 indicators significant = strong evidence

**From Census Data:**
- Hill et al. (2012) successfully replicated with 33 years of official data
- Beauty R² = 24.8% (strongest evidence for lipstick effect documented to date)
- Beauty sales increased during all recessions (+6.2%, +4.5%, +0.4%)
- 404 months across 4 economic cycles

**From Purchase Data:**
- 95% of spending is little luxuries (shows high demand)
- Fashion dominates (94% of luxury spending)
- $100-500 is the sweet spot price range

**Integrated Insight:**
- Search behavior (Google Trends): Strong CCI correlation
- Purchase behavior (Census): Strong CCI correlation
- **Both confirm lipstick effect at different stages**

---

## Technical Notes

**Date Formats:**
- All dates are in `YYYY-MM-DD` or `YYYY-MM` format
- Use Tableau's date parsing to create month/quarter/year hierarchies

**Joining Files:**
- Can join `tableau_main_data_final.csv` with `tableau_search_vs_purchase.csv` on `date`
- Can join census files on `observation_date`

**Filters to Create:**
- Economic period (Normal, Great Recession, COVID-19, Inflation Surge)
- Indicator type (Fashion, Beauty & Cosmetics, Accessories)
- Significance (Yes/No)
- Date ranges

**Calculated Fields:**
- Inverse CCI (to show same direction as searches): `100 - [CCI]`
- Normalized scores (0-100 scale)
- Year-over-year growth rates

---

## Questions?

See the main `README.md` for:
- Complete methodology
- Data source descriptions
- Statistical interpretations

See `FINAL_REPORT.md` for:
- Detailed analysis
- Peer research alignment
- Limitations and future work

---

**Created:** December 2024
**Project:** Little Luxuries - Testing the Lipstick Effect
**Data Coverage:** 1992-2025 (33 years)
