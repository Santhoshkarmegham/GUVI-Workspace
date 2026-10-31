"""Export complete normalized tables to cleaned/ as CSV."""
import csv
from database import ROOT, TABLES, initialize, connect
initialize()
output = ROOT / 'cleaned'
output.mkdir(exist_ok=True)
with connect() as con:
    for table in TABLES:
        cursor = con.execute(f'SELECT * FROM {table}')
        with (output / f'{table}.csv').open('w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([c[0] for c in cursor.description])
            writer.writerows(cursor)
print('Exported all tables to', output)
