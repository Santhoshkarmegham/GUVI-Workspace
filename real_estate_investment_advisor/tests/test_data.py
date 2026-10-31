from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from investment_advisor.config import RAW_DATA_FILE
from investment_advisor.data import load_housing_data

class DataTests(unittest.TestCase):
    def test_supplied_dataset(self):
        data = load_housing_data()
        self.assertEqual(data.shape, (250000, 23))
        self.assertEqual(RAW_DATA_FILE.parent.name, 'raw')

    def test_invalid_schema_has_clear_error(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'invalid.csv'
            source.write_text('City\nChennai\n')
            with self.assertRaisesRegex(ValueError, 'Missing required columns'):
                load_housing_data(source)

if __name__ == '__main__':
    unittest.main()
