"""Small, repeatable data import. Run: python database.py."""
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'brickview.db'
TABLES = ['agents', 'listings', 'property_attributes', 'sales', 'buyers', 'india_housing']

def connect():
    con = sqlite3.connect(DB)
    con.execute('PRAGMA foreign_keys = ON')
    return con

def initialize():
    if DB.exists():
        return
    import pandas as pd
    con = connect()
    try:
        con.executescript((ROOT / 'schema.sql').read_text())
        for table, filename in [('agents','agents_cleaned.json'), ('listings','listings_final_expanded.json'), ('property_attributes','property_attributes_final_expanded.json'), ('sales','sales_cleaned.csv'), ('buyers','buyers_cleaned.json')]:
            path = ROOT / 'data' / filename
            rows = json.loads(path.read_text()) if path.suffix == '.json' else list(csv.DictReader(path.open()))
            aliases = {'sqft':'area_sqft', 'date_listed':'listed_date', 'date_sold':'sale_date', 'days_on_market':'days_on_market'}
            rows = [{aliases.get(k.lower(), k.lower()): v for k,v in row.items()} for row in rows]
            if table == 'sales':
                for row in rows:
                    row['sale_id'] = row['listing_id']
            cols = list(rows[0])
            con.executemany(f'INSERT INTO {table} ({",".join(cols)}) VALUES ({",".join("?" for _ in cols)})', [[r[c] for c in cols] for r in rows])
        con.commit()
        for chunk in pd.read_csv(ROOT / 'data/india_housing_prices.csv', chunksize=25000):
            chunk.columns = chunk.columns.str.lower()
            chunk.to_sql('india_housing', con, if_exists='append', index=False)
        con.execute('CREATE INDEX idx_india_city ON india_housing(city)')
        con.execute('CREATE UNIQUE INDEX idx_india_id ON india_housing(id)')
        con.commit()
    except Exception:
        con.close()
        DB.unlink(missing_ok=True)
        raise
    finally:
        con.close()

if __name__ == '__main__':
    initialize()
    with connect() as con:
        for table in TABLES:
            print(table, con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0])
        print('Foreign key errors:', con.execute('PRAGMA foreign_key_check').fetchall())
