"""
Application configuration and constants
"""

import os
from pathlib import Path

# Application info
APP_NAME = "CBCMGROUPS Email Distribution List Migration Tool"
APP_VERSION = "0.1.0"

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
DOCS_DIR = BASE_DIR / "docs"
TESTS_DIR = BASE_DIR / "tests"

# Runtime directories
BACKUPS_DIR = BASE_DIR / "backups"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"

# Ensure runtime directories exist
BACKUPS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# Logging configuration
LOG_FILE = LOGS_DIR / "migration_tool.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Email validation regex
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# MS365 Configuration
MS365_SCOPES = [
    "https://graph.microsoft.com/.default",
]

# OAuth Configuration
OAUTH_TIMEOUT = 600  # seconds (10 minutes)

# API Configuration
API_RETRY_COUNT = 3
API_RETRY_DELAY = 1  # seconds
API_TIMEOUT = 30  # seconds

# File Configuration
DEFAULT_ENCODING = "utf-8"
FALLBACK_ENCODING = "latin-1"

# Scanning Configuration
# Number of parallel workers for scanning .org files
# Auto-calculated as: min(MAX_SCAN_WORKERS, max(MIN_SCAN_WORKERS, CPU_COUNT * 2))
MIN_SCAN_WORKERS = 4
MAX_SCAN_WORKERS = 16

# Backup Configuration
BACKUP_COMPRESSION = False  # Set to True to enable ZIP compression
BACKUP_RETENTION = 10  # Keep last N backups

# Validation
MIN_DOMAIN_LENGTH = 3
MAX_DISTRIBUTION_LIST_NAME = 254

# Phase 3 Cleanup Configuration
CLEANUP_PREFIX = "!ALIAS "
MS365_SUFFIX = ".ms365"
