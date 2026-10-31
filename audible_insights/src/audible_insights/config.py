from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data/raw'
CLEAN = ROOT / 'data/processed/books.csv'
AUDIT = ROOT / 'reports/data_quality.json'
