from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from audible_insights.data import prepare
if __name__=='__main__':
    books=prepare()
    print(f'Prepared {len(books):,} books; saved data/processed/books.csv and reports/data_quality.json')
