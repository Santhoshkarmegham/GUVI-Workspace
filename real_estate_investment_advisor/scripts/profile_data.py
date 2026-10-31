"""Run from any directory to write a source-data quality report."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from investment_advisor.config import REPORTS_DIR
from investment_advisor.data import load_housing_data

def main():
    data = load_housing_data()
    report = {
        'rows': len(data), 'columns': len(data.columns),
        'dtypes': data.dtypes.astype(str).to_dict(),
        'missing_values': data.isna().sum().to_dict(),
        'exact_duplicates': int(data.duplicated().sum()),
        'duplicate_ids': int(data.ID.duplicated().sum()),
        'non_positive_area': int(data.Size_in_SqFt.le(0).sum()),
        'non_positive_price': int(data.Price_in_Lakhs.le(0).sum()),
        'floor_above_total': int(data.Floor_No.gt(data.Total_Floors).sum()),
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORTS_DIR / 'data_quality.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    print('Saved reports/data_quality.json')

if __name__ == '__main__':
    main()
