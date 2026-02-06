"""
Configuration settings for Personal Finance Manager
"""
import os

# API Configuration
API_BASE_URL = "https://splendid-annelise-dataserve-3b5684c9.koyeb.app"
BACKUP_ENDPOINT = f"{API_BASE_URL}/backup"
RESTORE_ENDPOINT = f"{API_BASE_URL}/restore"

# Database Configuration
DB_NAME = "finance.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# App Constants
APP_NAME = "Personal Finance Manager"
CURRENCY_SYMBOL = "KES "
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default Categories
DEFAULT_CATEGORIES = {
    "income": [
        "Salary",
        "Freelance",
        "Investment",
        "Gift",
        "Other Income"
    ],
    "expense": [
        "Food & Dining",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Healthcare",
        "Education",
        "Travel",
        "Personal Care",
        "Other Expense"
    ]
}

# Theme Colors
COLORS = {
    "primary": (0.26, 0.52, 0.96, 1),      # Modern Blue #4285F4
    "secondary": (0.18, 0.80, 0.44, 1),    # Green #2ECC71
    "accent": (1, 0.60, 0.20, 1),          # Orange
    "danger": (0.95, 0.26, 0.21, 1),       # Red #F44336
    "background": (0.96, 0.96, 0.96, 1),   # Light Gray
    "card": (1, 1, 1, 1),                  # White
    "text": (0.13, 0.13, 0.13, 1),         # Dark Gray #212121
    "text_light": (0.62, 0.62, 0.62, 1),   # Medium Gray #9E9E9E
    "success": (0.30, 0.69, 0.31, 1),      # Green #4CAF50
    "warning": (1, 0.76, 0.03, 1),         # Amber #FFC107
}

# Budget Settings
DEFAULT_MONTHLY_BUDGET = {
    "Food & Dining": 500,
    "Transportation": 200,
    "Shopping": 300,
    "Entertainment": 150,
    "Bills & Utilities": 400,
    "Healthcare": 200,
    "Education": 100,
    "Travel": 200,
    "Personal Care": 100,
    "Other Expense": 150
}

# Sync Settings
AUTO_SYNC_ENABLED = False  # Manual sync by default
SYNC_TIMEOUT = 30  # seconds
MAX_RETRY_ATTEMPTS = 3
