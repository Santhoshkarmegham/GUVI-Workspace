# Brand Visibility Intelligence Dashboard

A modular Streamlit + SQLite project built from the supplied CSV. The original project in the parent directory remains intact.

## Run
From the repository root:

```sh
.venv/bin/python brand_visibility/pipeline.py
.venv/bin/python -m streamlit run brand_visibility/app.py --server.port 8502
```

For a fresh environment, install `brand_visibility/requirements.txt` first.

## Live extraction
Set `SERPAPI_API_KEY` in your environment, then run:

```sh
.venv/bin/python brand_visibility/pipeline.py --fetch 'wireless headphones'
```

Each explicit fetch requests one Google Shopping India result page. It preserves returned search positions and original prices, skips installment and non-INR offers, saves a dated CSV, and rebuilds the combined dataset. No API key is included or logged. API requests may consume your SerpAPI quota. No live extraction was performed during development because credentials were not provided.

API field reference: https://serpapi.com/shopping-results
API query parameters: https://serpapi.com/google-shopping-api

## Outputs and approach
- `outputs/clean_products.csv`: cleaned, feature-engineered listing observations.
- `outputs/brands.db`: SQLite products table used by all dynamic filters.
- `outputs/cleaning_audit.json`: source dimensions, types, missingness, duplicates and coverage.
- `REPORT.md`: methods, findings, limitations, and recommendations.

Seven app sections cover overview, brands, prices, platforms, search visibility, product inspection, and data quality. SQL filters use bound parameters; identifiers are allowlisted. Search is literal substring matching. Unknown values stay unknown, metrics report their coverage, and an empty selection produces a helpful message.

Brand detection uses the explicit dictionary in `pipeline.py`. Price tiers are INR assumptions: 0–2,500, 2,500–10,000, 10,000–25,000 and above 25,000 (right-inclusive). Outliers use 1.5×IQR within keyword and are flagged rather than removed. Duplicate identity includes source, snapshot and observed position so distinct API observations are retained. API and CSV overlap cannot reliably be resolved without shared product identifiers. Multiple snapshots describe observations, not unique products or time trends.

The CSV does not supply search position, original price or collection date. Ratings are customer ratings, never search ranks. Visibility is 100 / observed position; discounts are calculated only where original price is at least selling price. Missing price, rating, and reviews are not imputed; averages exclude unknown values. Missing delivery is Unknown. Discount percentage denominators include only listings with known discounts; top-10 percentages include only ranked listings.

The supplied model-style product titles include implausible brand/category combinations. Treat these as training data, not verified current market evidence. INR is assumed for the supplied CSV, following the project brief.

## Verification

```sh
.venv/bin/python -m unittest discover -s brand_visibility/tests -v
```

Tests cover dirty numeric input, duplicate identity, unknown metric preservation, observed visibility/discount calculations, SQL parameter safety, rating/price filters, all seven pages, and empty filter results. Live API execution requires credentials and is unverified.
