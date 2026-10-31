# GUVI Workspace

Five Python projects in one VS Code workspace: real estate analytics, brand visibility, property data exploration, waste-image classification preparation, and audiobook recommendations.

## Projects and current status

| Project | Folder | What works now | Status and limits | Port |
| --- | --- | --- | --- | --- |
| BrickView — Real Estate Analytics | `brickview/` | SQLite import, dashboard filters, agent dashboard, SQL explorer, record management, India housing analysis, CSV export | Functional analytics app; database edits persist locally | 8501 |
| Brand Visibility Intelligence Dashboard | `brand_visibility/` | Cleaning pipeline, SQLite filters, brand/pricing/platform charts, product explorer, data-quality audit, optional SerpAPI extraction | CSV works offline; live extraction requires credentials. Search ranking and discount metrics need observed API fields | 8502 |
| Real Estate Investment Advisor | `real_estate_investment_advisor/` | Housing catalogue filters, property table, summary metrics, CSV download, data profiling | Dataset explorer only. Investment models, future-price prediction and MLflow are pending | 8503 |
| RecycleVision | `recyclevision/` | Image upload preview, six-class taxonomy, image verification and inventory script | Dataset download and model training are pending. Uploads are not classified yet | 8504 |
| Audible Insights | `audible_insights/` | Book search, detailed book profiles, catalogue charts, content, cluster and hybrid recommendations | Content-based discovery; no user-history evaluation or AWS deployment | 8505 |

## 1. Get the repository

```bash
git clone https://github.com/Santhoshkarmegham/GUVI-Workspace.git
cd GUVI-Workspace
```

If you already cloned the repository, open its folder and use your existing checkout. The commands below run from the repository root, where `GUVI.code-workspace` is located. No personal computer path is required.

Open `GUVI.code-workspace` in VS Code to see the projects separately. A terminal opened inside a project folder needs `cd ..` before running the root-level commands below.

### Branches

`main` is the combined workspace. Project branches are `brand-visibility`, `real-estate-investment-advisor`, `recyclevision` and `audible-insights`. Older project branches can contain fewer projects than `main`.

```bash
git switch main
git pull --ff-only origin main
```

To work on a project branch instead, substitute its branch name. Commit or stash any current work before switching branches.

## 2. Create and activate a virtual environment

Python 3.10 or newer is required by the packaged projects. The current apps were verified with Python 3.14. These instructions install the dependencies for the implemented applications; deep-learning training dependencies are not included yet.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If the environment already exists, just activate it. Activate it again whenever you open a new terminal. The terminal prompt normally shows `(.venv)`.

## 3. Install dependencies

Install everything used by the five current apps:

```bash
python -m pip install --upgrade pip
python -m pip install -r brickview/requirements.txt -r brand_visibility/requirements.txt -r real_estate_investment_advisor/requirements.txt -r recyclevision/requirements.txt -r audible_insights/requirements.txt
```

To install just one project's dependencies, use its requirements file, for example:

```bash
python -m pip install -r audible_insights/requirements.txt
```

## 4. Run an application

Use one command at a time, or open a separate activated terminal for each app you want to run concurrently.

### BrickView

```bash
python -m streamlit run brickview/app.py --server.port 8501
```

Open [localhost:8501](http://localhost:8501). The first launch imports the supplied files into `brickview/data/brickview.db`. Later launches reuse that database, including saved record changes.

### Brand Visibility

```bash
python -m streamlit run brand_visibility/app.py --server.port 8502
```

Open [localhost:8502](http://localhost:8502). The first launch creates the database if it is missing. Use the sidebar filters to explore brands, platforms, keywords, price tiers and ratings.

### Real Estate Investment Advisor

```bash
python -m streamlit run real_estate_investment_advisor/app.py --server.port 8503
```

Open [localhost:8503](http://localhost:8503). Explore the supplied 250,000 housing records using city and property-type filters. This version does not make investment predictions.

### RecycleVision

```bash
python -m streamlit run recyclevision/app.py --server.port 8504
```

Open [localhost:8504](http://localhost:8504). Upload an image to preview it. A trained classifier is not included, so category predictions and confidence scores are unavailable.

### Audible Insights

```bash
python -m streamlit run audible_insights/app.py --server.port 8505
```

Open [localhost:8505](http://localhost:8505). Search the catalogue, select a book to inspect its description and metadata, or choose a favourite book/interests to request recommendations. Recommendation features and clusters are built in memory and cached on first use.

Press **Ctrl+C** in the running terminal to stop any app. Run `deactivate` when you finish using the virtual environment.

## 5. Prepare data and generate reports

### BrickView: initialize and export

```bash
python brickview/scripts/initialize_database.py
python brickview/scripts/export_data.py
```

Raw sources are in `brickview/data/raw/`, the SQL schema is in `brickview/sql/`, and exported tables are written to `brickview/data/processed/`. Initialization keeps an existing database; it does not reset saved edits. Back up the database before any manual rebuild.

### Brand Visibility: clean and rebuild

```bash
python brand_visibility/scripts/prepare_data.py
```

Reads `brand_visibility/data/raw/`, rebuilds `brand_visibility/data/brands.db`, and writes `data/processed/clean_products.csv` and `reports/cleaning_audit.json` inside that project.

Optional live India shopping extraction requires a SerpAPI key. Set `SERPAPI_API_KEY` in your terminal environment, then run:

```bash
python brand_visibility/scripts/prepare_data.py --fetch "wireless headphones"
```

Each explicit fetch may consume API quota. Keep keys out of source files and Git. The supplied CSV has no original prices or search positions: missing discounts and visibility remain unavailable rather than being invented. Customer ratings are distinct from search positions.

### Real Estate Investment Advisor: profile data

```bash
python real_estate_investment_advisor/scripts/profile_data.py
```

Reads `real_estate_investment_advisor/data/raw/india_housing_prices.csv` and writes `reports/data_quality.json`. The report checks missing values, duplicates, non-positive price/area and floor inconsistencies. The supplied price-per-square-foot units need validation before modelling; INR per square foot can be recomputed as `Price_in_Lakhs × 100000 / Size_in_SqFt`.

### RecycleVision: install and inspect images

Download the [six-class garbage dataset](https://www.kaggle.com/datasets/asdasdasasdas/garbage-classification) and extract it into `recyclevision/data/raw/`. Create that folder if it does not exist. Preserve the class folders: `cardboard`, `glass`, `metal`, `paper`, `plastic` and `trash`. Nested archive directories are supported. The `trash` category is not an organic-waste label.

```bash
python recyclevision/scripts/profile_data.py
```

Writes `recyclevision/reports/dataset_inventory.json` with class counts, image dimensions and corrupt-image flags. Without downloaded images, the script reports zero images. Raw images are excluded from Git. CNN/transfer-learning training and model evaluation are not implemented yet.

### Audible Insights: merge the catalogues

```bash
python audible_insights/scripts/prepare_data.py
```

Reads both supplied CSVs in `audible_insights/data/raw/`, normalizes title/author identity, collapses duplicate records and produces `data/processed/books.csv` plus `reports/data_quality.json`. The current merge contains 6,063 books. Advanced-source values take precedence, with basic-source values filling gaps. Invalid `-1` ratings remain unknown. Prices have no declared currency.

Content recommendations use TF-IDF similarity; cluster recommendations restrict candidates to a content cluster. Hybrid ranking combines similarity, customer rating and review popularity. Scores are ranking signals, not probabilities. User-item histories and publication dates are absent, so user-relevance precision/recall and publication-year trends are not available.

## 6. Run the checks

Run each project's tests separately from the repository root:

```bash
python -m unittest discover -s brickview/tests -v
python -m unittest discover -s brand_visibility/tests -v
python -m unittest discover -s real_estate_investment_advisor/tests -v
python -m unittest discover -s recyclevision/tests -v
python -m unittest discover -s audible_insights/tests -v
```

Tests cover database queries and record operations, data cleaning and filtering, schema validation, image inventory, catalogue recommendations and selected Streamlit pages. They do not establish live API access, trained investment/image model performance, or cloud deployment.

## Folder guide

```text
GUVI-Workspace/
├── brickview/
├── brand_visibility/
├── real_estate_investment_advisor/
├── recyclevision/
├── audible_insights/
├── GUVI.code-workspace
├── projects.json
└── README.md
```

Within each project, `app.py` starts the interface, `src/` holds reusable logic, `scripts/` contains executable preparation tasks, `tests/` contains checks, and `requirements.txt` lists dependencies. Where supplied, `data/raw/` preserves source files, `data/processed/` contains generated datasets, and `reports/` contains audit results or screenshots. BrickView also has a `sql/` folder. Folders exist only where the project has actual files; generated directories can appear after a script runs.

## Troubleshooting

- **File not found:** Check that the terminal is at the repository root and that your branch contains the project. If you are inside a project folder, use `python -m streamlit run app.py --server.port 8505` with that project's port instead.
- **Missing Python module:** Activate the virtual environment and install the corresponding requirements file. Use `python -m pip` so installation targets the same interpreter.
- **Port already in use:** Stop the previous app with Ctrl+C or choose a different port with `--server.port`.
- **Missing dataset:** Restore the supplied CSVs to the relevant `data/raw/` folder. RecycleVision images require a separate download.
- **Stale processed data:** Stop the app, run its preparation script, and restart. Brand Visibility rebuilding replaces its product table; BrickView initialization reuses its existing database.
- **Streamlit bare-mode warning during tests:** A missing ScriptRunContext warning can occur under the test runner. Check the final test result for actual failures.
