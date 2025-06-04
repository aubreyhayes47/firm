"""
Configuration for Law by Keystone, including ethical framework settings.
"""
import os

# Default ethical framework mode: 'standard' or 'catholic_teachings_aligned'
DEFAULT_ETHICAL_FRAMEWORK_MODE = os.getenv('DEFAULT_ETHICAL_FRAMEWORK_MODE', 'catholic_teachings_aligned')

# Path to curated Catholic teachings knowledge base
CATHOLIC_TEACHINGS_KB_PATH = os.getenv('CATHOLIC_TEACHINGS_KB_PATH', './data/catholic_teachings_kb.json')

# Path to store ethical guidelines records
ETHICAL_GUIDELINES_STORAGE_PATH = os.getenv('ETHICAL_GUIDELINES_STORAGE_PATH', './data/ethical_guidelines/')

# Database URI (example, to be set in environment or .env file)
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///law_by_keystone.db')

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', './logs/law_by_keystone.log')
