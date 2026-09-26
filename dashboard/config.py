"""
FraudLens — Dashboard Configuration & Constants
Centralizes application settings, database paths, color palettes, and typography.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "processed" / "fraudlens.db"
POWERBI_DIR = BASE_DIR / "data" / "processed" / "powerbi"
SQL_RESULTS_DIR = BASE_DIR / "data" / "processed" / "sql_results"

# Application Metadata
APP_TITLE = "FraudLens"
APP_SUBTITLE = "Financial Fraud Analytics & Investigation Platform"
APP_TAGLINE = "Analyze. Detect. Investigate. Prevent."
APP_ICON = "🛡️"

# Design System & Palette (Fintech Dark / Clean Theme)
COLORS = {
    "background_dark": "#0F172A",
    "card_dark": "#1E293B",
    "card_border": "#334155",
    "primary_blue": "#38BDF8",
    "secondary_blue": "#0284C7",
    "fraud_crimson": "#F43F5E",
    "fraud_accent": "#E11D48",
    "legit_emerald": "#10B981",
    "warning_amber": "#F59E0B",
    "neutral_light": "#F8FAFC",
    "text_muted": "#94A3B8",
}

# Risk Tier Styling
RISK_COLORS = {
    "Critical": "#F43F5E",
    "High": "#FB923C",
    "Medium": "#FBBF24",
    "Low": "#34D399",
}

# Pagination Settings
DEFAULT_PAGE_SIZE = 25
INVESTIGATION_PAGE_SIZE = 25
