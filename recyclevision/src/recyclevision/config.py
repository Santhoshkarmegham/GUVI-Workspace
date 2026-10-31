"""Portable paths and the six-class source taxonomy."""
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw'
MODELS_DIR = PROJECT_ROOT / 'models'
REPORTS_DIR = PROJECT_ROOT / 'reports'
CLASSES = ('cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash')
