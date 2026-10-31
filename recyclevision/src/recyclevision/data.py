"""Inventory images without modifying source data or requiring TensorFlow."""
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from .config import CLASSES, RAW_DATA_DIR

EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

def inventory(root: Path = RAW_DATA_DIR):
    """Find class folders recursively, supporting nested Kaggle archives."""
    records = []
    for path in sorted(Path(root).rglob('*')):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if any(part.startswith('.') or part == '__MACOSX' for part in path.relative_to(root).parts):
            continue
        label = next((part.lower() for part in reversed(path.relative_to(root).parts[:-1]) if part.lower() in CLASSES), None)
        if label is None:
            continue
        row = {'file': str(path.relative_to(root)), 'class': label, 'valid': True, 'width': None, 'height': None}
        try:
            with Image.open(path) as image:
                row['width'], row['height'] = image.size
                image.verify()
        except (OSError, UnidentifiedImageError, Image.DecompressionBombError):
            row['valid'] = False
        records.append(row)
    return records
