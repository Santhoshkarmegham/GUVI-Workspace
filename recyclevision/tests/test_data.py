from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from recyclevision.data import inventory

class InventoryTests(unittest.TestCase):
    def test_nested_classes_and_corrupt_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / 'dataset' / 'plastic'
            target.mkdir(parents=True)
            Image.new('RGB', (20, 10)).save(target / 'valid.jpg')
            (target / 'broken.jpg').write_text('invalid image')
            other = root / 'unlabelled'
            other.mkdir()
            Image.new('RGB', (10, 10)).save(other / 'ignored.png')
            records = inventory(root)
            self.assertEqual(len(records), 2)
            self.assertEqual(sum(row['valid'] for row in records), 1)
            self.assertTrue(all(row['class'] == 'plastic' for row in records))

    def test_empty_dataset(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(inventory(Path(folder)), [])

if __name__ == '__main__':
    unittest.main()
