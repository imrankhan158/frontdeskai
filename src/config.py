from pathlib import Path
from dotenv import load_dotenv

# Base Paths
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent

# Load environment variables from .env in project root
load_dotenv(ROOT_DIR / ".env")

# Organized Folders
DATA_DIR = ROOT_DIR / "data"
STATIC_DIR = ROOT_DIR / "static"
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
REPORTS_DIR = ROOT_DIR / "reports"

for _dir in (DATA_DIR, STATIC_DIR, KNOWLEDGE_DIR, REPORTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Canonical File Paths
FAQ_PATH = KNOWLEDGE_DIR / "clinic_faq.md"
BOOKINGS_PATH = DATA_DIR / "bookings.json"
TELEMETRY_LOG_PATH = DATA_DIR / "telemetry.json"
BENCHMARKS_JSON_PATH = DATA_DIR / "benchmarks.json"
BENCHMARKS_MD_PATH = REPORTS_DIR / "BENCHMARKS.md"
DATASET_PATH = DATA_DIR / "eval_dataset.json"
REPORT_JSON_PATH = DATA_DIR / "eval_report.json"
REPORT_MD_PATH = REPORTS_DIR / "EVAL_REPORT.md"
EVAL_HISTORY_PATH = DATA_DIR / "eval_history.json"
REPORTS_HISTORY_DIR = REPORTS_DIR / "history"
REPORTS_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
INDEX_HTML_PATH = STATIC_DIR / "index.html"

# Unit Economics
USD_TO_INR = 85.0


def get_faq_content() -> str:
    """Load FAQ knowledge base into memory."""
    if FAQ_PATH.exists():
        return FAQ_PATH.read_text(encoding="utf-8")
    return ""
