"""Load source records without changing the original data."""
from pathlib import Path
import pandas as pd
from .config import RAW_DATA_FILE

REQUIRED_COLUMNS = {'ID', 'City', 'Property_Type', 'BHK', 'Size_in_SqFt', 'Price_in_Lakhs'}

def load_housing_data(path: Path = RAW_DATA_FILE) -> pd.DataFrame:
    """Read a CSV and fail clearly when required project columns are absent."""
    data = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f'Missing required columns: {", ".join(sorted(missing))}')
    return data
