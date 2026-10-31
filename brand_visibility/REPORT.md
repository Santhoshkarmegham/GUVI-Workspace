# Project report: Brand Visibility Intelligence Dashboard

## Objective
Analyze listing presence, customer ratings, pricing, platforms, and observed search visibility using a reproducible CSV/API-to-SQL pipeline and interactive Streamlit dashboard.

## Source and quality
The supplied dataset contains 1,320 rows and seven columns. Cleaning removes 94 duplicate listing observations and retains 1,226 records. Unknown values remain in 207 prices, 121 ratings and 20 review counts. Forty-six price outliers are flagged and retained for inspection. Source dimensions, data types and missingness are exported in cleaning_audit.json.

## Descriptive results
- Average known price: INR 35,357.72 (1,019 observations).
- Average known customer rating: 3.79/5 (1,105 observations).
- Known review total: 2,917,517; unknown review counts are excluded.
- Most listed brand: HP, with 157 listings (12.8% of retained records).
- Lowest pooled platform mean price: Flipkart, INR 31,740.76. Category mix may explain this difference.
- Source lacks ranking and original-price fields; no search visibility or discount findings can be supported from the CSV alone.

## Methods and interpretation
Platform names and product titles are normalized, numeric parsing is explicit, non-positive prices and out-of-range ratings become unknown, and fractional or negative review counts are rejected. Known brands are extracted with word-boundary matching. Price bands use documented INR boundaries. Outliers use keyword-level 1.5×IQR. Parameterized SQL drives all sidebar filters. Search positions remain distinct from customer ratings; API-based visibility is 100/position.

## Recommendations
Compare brands within the same keyword and platform before interpreting prices. Inspect flagged prices against source records before adjusting a pricing strategy. Collect dated India API snapshots to establish real search rankings and original prices. Monitor metric coverage alongside averages, especially when filters change. Validate the provided training-style product titles before using these results in commercial decisions.

## Deliverables and validation
Source code, raw CSV copy, clean CSV, SQLite database, audit JSON, dashboard, and this report are included. Automated tests cover ETL edge cases, SQL filtering and all app sections. Live API fetching is implemented but has not been executed without credentials. The project is local; no GitHub repository has been published.
