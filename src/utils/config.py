import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
EXTERNAL_DATA_DIR = DATA_DIR / 'external'
SQL_DIR = BASE_DIR / 'sql'
REPORTS_DIR = BASE_DIR / 'reports'
MODELS_DIR = PROCESSED_DATA_DIR / 'models'

MODELS_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
EXTERNAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_RAW_FILE = Path(os.getenv(
    'DATA_RAW_PATH',
    (RAW_DATA_DIR / 'PS_20174392719_1491204439457_log.csv') if (RAW_DATA_DIR / 'PS_20174392719_1491204439457_log.csv').exists()
    else (Path.home() / '.cache' / 'kagglehub' / 'datasets' / 'ealaxi' / 'paysim1' / 'versions' / '2' / 'PS_20174392719_1491204439457_log.csv')
))

DATABASE_PATH = PROCESSED_DATA_DIR / 'fraudlens.db'
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATABASE_PATH.as_posix()}')

RANDOM_STATE = int(os.getenv('RANDOM_STATE', 42))
ANALYTICAL_SAMPLE_SIZE = int(os.getenv('SAMPLE_SIZE', 500000))

HIGH_AMOUNT_THRESHOLD = 200000.0
HIGH_VELOCITY_THRESHOLD = 3
BALANCE_DRAIN_THRESHOLD = 0.95
SUSPICIOUS_TRANSFER_CASH_WINDOW = 2
