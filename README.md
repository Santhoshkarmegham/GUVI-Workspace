# BrickView — simple real estate analytics

A beginner-friendly Streamlit app with a local SQLite database. No API keys or database server needed.

## Run on macOS / Linux

```bash
cd /Users/sandy/Documents/ChatGPT/GUVI-V1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501. The first run imports the supplied files. Later runs retain your edits.

## Pages

- **Dashboard:** city, property type, agent, price, listed date and sold status filters; KPIs, map, bar charts, monthly trends and CSV download.
- **SQL explorer:** 31 named analyses with SQL and downloadable results. Uses the full database.
- **Manage records:** view, add, update and delete records in all six tables. Search by ID; browsing supports pagination and sorting. For related records, create parents first and delete children first.
- **India housing:** a separate city comparison in INR lakhs, with paginated detail rows.
- **Data notes:** source interpretation and row counts.

## Files

`app.py` is the UI, `database.py` imports data, `schema.sql` defines the related tables, and `queries.py` holds the analysis SQL. `data/` preserves the supplied source files. `brickview.db` is generated locally and excluded from Git. `REPORT.md` explains the findings and limitations.

## Data relationships

Agents → listings → sales → buyers. Property attributes have a one-to-one relationship with listings. Each supplied sale is uniquely identified by its listing ID, which is also the buyers file's sale_id. India housing is independent and uses its source ID.

JSON fields are flattened already. Names are standardized during import; numeric and boolean values use SQLite numeric storage. Dates are ISO text. The source CSVs are already cleaned and are retained. Export any current table from Manage records; exports include all matching rows. JSON-derived complete tables can be exported with the command below.

```bash
python export_data.py
python -m unittest discover -s tests -v
```

To rebuild from the original data, stop the app and remove `brickview.db`, then restart. This discards local edits. The app is intended for local single-user use; it has no authentication.

## Requirement audit

See `COVERAGE.md` for the requirement-by-requirement review. Screenshots are included in `REPORT.md` and `screenshots/`.
