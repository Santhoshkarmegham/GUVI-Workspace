"""Auditable CSV + SerpAPI ETL, SQLite storage, and parameterized filters."""
from pathlib import Path
import argparse
import json
import os
import re
import sqlite3
import urllib.parse
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'outputs/brands.db'
BRANDS = ['Samsung', 'Apple', 'Philips', 'Dell', 'HP', 'Boat', 'Puma', 'Nike', 'Sony', 'Lenovo', 'Asus', 'LG', 'OnePlus', 'Xiaomi', 'Adidas']

def numeric(s):
    text = s.astype('string').str.strip().str.replace(',', '', regex=False)
    text = text.str.replace(r'^(?:₹|INR\s*)', '', regex=True).str.strip()
    return pd.to_numeric(text, errors='coerce').astype(float)

def clean(raw):
    d = raw.copy()
    d.columns = d.columns.str.strip().str.lower()
    audit = {'input_rows': len(d), 'input_columns': len(d.columns), 'original_dtypes': d.dtypes.astype(str).to_dict(), 'missing_percent_before': (d.isna().mean()*100).round(2).to_dict()}
    for col in ['keyword', 'title', 'platform', 'delivery']:
        if col not in d: d[col] = 'Unknown'
        d[col] = d[col].fillna('Unknown').astype(str).str.replace(r'!+', '', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip().replace('', 'Unknown')
    d['platform'] = d.platform.str.title().replace({'Hp': 'HP'})
    d['keyword'] = d.keyword.str.lower()
    if 'source' not in d: d['source'] = 'Provided CSV'
    if 'snapshot' not in d: d['snapshot'] = 'Provided CSV (date unknown)'
    for col in ['price', 'raw_price', 'rating', 'reviews', 'position']:
        if col not in d: d[col] = float('nan')
        d[col] = numeric(d[col])
    for col in ['price', 'raw_price']:
        d.loc[d[col] <= 0, col] = float('nan')
    d.loc[~d.rating.between(0, 5), 'rating'] = float('nan')
    for col in ['reviews', 'position']:
        valid = d[col].ge(0 if col == 'reviews' else 1) & d[col].mod(1).eq(0)
        d.loc[~valid, col] = float('nan')
    # Preserve missing metrics: unknown reviews are not zero; ratings are not rank.
    key = ['keyword', 'title', 'platform', 'price', 'source', 'snapshot', 'position']
    before = len(d)
    d = d.drop_duplicates(key).reset_index(drop=True)
    audit['duplicate_rows_removed'] = before - len(d)
    pattern = r'\b(' + '|'.join(re.escape(b) for b in BRANDS) + r')\b'
    canonical = {b.lower(): b for b in BRANDS}
    d['brand'] = d.title.str.extract(pattern, flags=re.I, expand=False).str.lower().map(canonical).fillna('Unknown')
    d['visibility_score'] = 100 / d.position
    d['discount_pct'] = ((d.raw_price-d.price)/d.raw_price*100).where(d.raw_price.ge(d.price) & d.price.notna())
    d['price_range'] = pd.cut(d.price, bins=[0, 2500, 10000, 25000, float('inf')], labels=['Budget · <2.5k', 'Value · 2.5–10k', 'Premium · 10–25k', 'Luxury · >25k']).astype('string').fillna('Unknown')
    q = d.groupby('keyword').price.transform(lambda s: s.quantile(.25))
    upper = d.groupby('keyword').price.transform(lambda s: s.quantile(.75))
    d['price_outlier'] = ((d.price < q-1.5*(upper-q)) | (d.price > upper+1.5*(upper-q))).astype(int)
    audit.update(clean_rows=len(d), missing_after=d.isna().sum().to_dict(), outliers_flagged=int(d.price_outlier.sum()), ranked_rows=int(d.position.notna().sum()), discount_known_rows=int(d.discount_pct.notna().sum()))
    return d, audit

def build():
    frames = [pd.read_csv(ROOT / 'data/brand_dirty_dataset.csv')]
    for file in sorted((ROOT/'data').glob('api_*.csv')):
        frames.append(pd.read_csv(file))
    data, audit = clean(pd.concat(frames, ignore_index=True))
    DB.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as con:
        data.to_sql('products', con, if_exists='replace', index=False)
        con.execute('CREATE INDEX IF NOT EXISTS filters ON products(brand, platform, keyword)')
    data.to_csv(ROOT/'outputs/clean_products.csv', index=False)
    (ROOT/'outputs/cleaning_audit.json').write_text(json.dumps(audit, indent=2))
    return audit

def query(filters=None, search='', rating=(0.,5.), include_unrated=True, price=None):
    clauses, params = [], []
    for col, values in (filters or {}).items():
        if col not in {'brand', 'platform', 'keyword', 'price_range', 'source'}: raise ValueError('Invalid filter')
        if values:
            clauses.append(f'"{col}" IN ({",".join("?" for _ in values)})'); params.extend(values)
    if search:
        clauses.append("instr(lower(title), lower(?)) > 0"); params.append(search)
    clauses.append('(rating BETWEEN ? AND ?' + (' OR rating IS NULL)' if include_unrated else ')'))
    params.extend(rating)
    if price:
        clauses.append('price BETWEEN ? AND ?'); params.extend(price)
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query('SELECT * FROM products WHERE ' + ' AND '.join(clauses), con, params=params)

def fetch(keyword):
    key = os.environ.get('SERPAPI_API_KEY')
    if not key: raise ValueError('Set SERPAPI_API_KEY before fetching live data.')
    params = urllib.parse.urlencode(dict(engine='google_shopping', q=keyword, gl='in', hl='en', api_key=key))
    # India scope keeps API prices comparable with the INR CSV. No paid requests without this CLI command.
    try:
        with urllib.request.urlopen('https://serpapi.com/search.json?' + params, timeout=45) as response:
            payload = json.load(response)
    except Exception:
        raise RuntimeError('API request failed; check connectivity and your SerpAPI account.') from None
    if payload.get('error'): raise RuntimeError('SerpAPI reported an error. Check your account and query.')
    stamp = pd.Timestamp.now(tz='UTC').isoformat()
    rows = []
    for r in payload.get('shopping_results', []):
        if r.get('installment'): continue
        if r.get('price') and not re.search(r'₹|INR', r['price'], re.I): continue
        rows.append(dict(keyword=keyword, title=r.get('title'), price=r.get('extracted_price'), raw_price=r.get('extracted_old_price'), rating=r.get('rating'), reviews=r.get('reviews'), platform=r.get('source'), delivery=r.get('delivery'), position=r.get('position'), source='SerpAPI · India', snapshot=stamp))
    if not rows: raise RuntimeError('No eligible INR, non-installment shopping results returned.')
    output = ROOT/'data'/('api_' + pd.Timestamp.now(tz='UTC').strftime('%Y%m%d_%H%M%S_%f') + '.csv')
    pd.DataFrame(rows).to_csv(output, index=False)
    return len(rows)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', metavar='KEYWORD', help='Fetch live India shopping results using SERPAPI_API_KEY')
    args = parser.parse_args()
    if args.fetch: print(f'Fetched {fetch(args.fetch)} API records')
    print(json.dumps(build(), indent=2))
