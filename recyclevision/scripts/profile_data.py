"""Write an image inventory and class-count report without changing raw data."""
import json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from recyclevision.config import CLASSES, REPORTS_DIR
from recyclevision.data import inventory

def main():
    records = inventory()
    counts = Counter(row['class'] for row in records if row['valid'])
    report = {'images_found': len(records), 'invalid_images': sum(not row['valid'] for row in records), 'valid_images_by_class': {label: counts[label] for label in CLASSES}, 'images': records}
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / 'dataset_inventory.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'Found {len(records)} images. Saved reports/dataset_inventory.json')
    if not records:
        print('Dataset not installed yet. Extract the Kaggle dataset into data/raw/.')

if __name__ == '__main__':
    main()
