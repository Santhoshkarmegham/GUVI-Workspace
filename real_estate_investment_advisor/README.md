# Real Estate Investment Advisor: Predicting Property Profitability & Future Value

New project in the GUVI workspace, on the `real-estate-investment-advisor` branch.

## Current status
Project setup and dataset explorer are available. Model training, evaluation and MLflow integration are pending. The brief describes rule-derived investment labels and synthetic five-year price targets; these must be explicitly documented as assumptions rather than verified investment outcomes or real future-price forecasts.

## Run
From this project's terminal in the GUVI workspace:

```sh
../.venv/bin/python -m streamlit run app.py --server.port 8503
```

Or from the repository root:

```sh
.venv/bin/python -m streamlit run real_estate_investment_advisor/app.py --server.port 8503
```

The application reads the supplied `data/raw/india_housing_prices.csv` using a relative project path. No personal computer path is required.

## Planned deliverables from the brief
- Clean and validate housing data, including area, floor consistency and price-per-square-foot units.
- Analyze pricing, size, location, amenities, ownership and transport accessibility.
- Define transparent Good_Investment and Future_Price_5Y targets.
- Compare at least five classifiers and five regressors with held-out evaluation and leakage controls.
- Track parameters, metrics and models with MLflow and register selected models.
- Add a property input form, model outputs, confidence interpretation and feature importance.

Keep target-generating inputs and deterministic target rules clearly documented so evaluation is not misrepresented as evidence of real-world forecasting accuracy.

## Supplied dataset
The project-local CSV contains 250,000 rows and 23 columns, with no missing cells or exact duplicate rows. It matches the dataset previously used by BrickView, but is kept here independently for this project. The raw file is preserved without changes.

Initial inspection shows floor numbers exceeding total floors and a Price_per_SqFt field apparently expressed in lakhs per square foot. Validate these fields before modelling; recompute INR per square foot as Price_in_Lakhs × 100,000 / Size_in_SqFt. No observed future prices or investment outcome labels are supplied.

## Folder structure

```text
real_estate_investment_advisor/
├── app.py                       # Streamlit entry point
├── requirements.txt             # Runtime dependencies
├── pyproject.toml               # Installable Python package configuration
├── .gitignore                   # Generated files and local secrets
├── data/
│   ├── raw/                     # Original supplied CSV, preserved unchanged
│   └── processed/               # Generated cleaned datasets
├── src/investment_advisor/
│   ├── __init__.py
│   ├── config.py                # Portable project paths
│   └── data.py                  # Dataset loading and schema checks
├── scripts/
│   └── profile_data.py          # Reproducible data-quality report
├── tests/
│   └── test_data.py             # Data-loading validation
├── docs/
│   └── methodology.md           # Assumptions and implementation status
├── notebooks/                   # Exploratory analysis notebooks
├── models/                      # Generated trained model artifacts
└── reports/
    └── figures/                 # Generated charts and screenshots
```

Training, feature engineering and prediction modules should be added under `src/investment_advisor/` when implemented. Generated models and MLflow runs are excluded from Git.

## Data-quality report
From this project folder:

```sh
../.venv/bin/python scripts/profile_data.py
../.venv/bin/python -m unittest discover -s tests -v
```

The profiling script writes `reports/data_quality.json`. Raw data is never modified by this script.
