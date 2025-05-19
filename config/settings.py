"""
Configuration settings for the LCM Framework.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# API settings
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8000"))
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Model settings
DEFAULT_MODEL_PATH = os.environ.get("MODEL_PATH", str(MODELS_DIR / "lcm-7b"))
LLAMA_MODEL_PATH = os.environ.get("LLAMA_MODEL_PATH", str(MODELS_DIR / "llama-7b"))
USE_GPU = os.environ.get("USE_GPU", "True").lower() in ("true", "1", "t")

# UI settings
UI_THEME = os.environ.get("UI_THEME", "default")
UI_TITLE = os.environ.get("UI_TITLE", "LCM Framework")
UI_DESCRIPTION = os.environ.get("UI_DESCRIPTION", "Language Model Comparison Framework")

# Logging settings
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Performance settings
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1024"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))