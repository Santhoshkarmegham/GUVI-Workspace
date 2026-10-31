"""Export complete normalized tables to data/processed/ as CSV."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import csv
from brickview.database import ROOT, TABLES, initialize, connect
initialize()
output = ROOT / 'data/processed'
output.mkdir(exist_ok=True)
with connect() as con:
    for table in TABLES:
        cursor = con.execute(f'SELECT * FROM {table}')
        with (output / f'{table}.csv').open('w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([c[0] for c in cursor.description])
            writer.writerows(cursor)
print('Exported all tables to', output)
