#!/usr/bin/env python3
"""
Download script for Llama-3-8B model.
This script downloads the Llama 3 model from Hugging Face.
"""

import os
import sys
import logging
import torch
from pathlib import Path

# Add parent directory to path to import from config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import settings from config
try:
    from config import settings
    MODEL_DIR = Path(settings.MODELS_DIR)
    LLAMA_MODEL_DIR = MODEL_DIR / "llama-3-8b"
except ImportError:
    # Fallback if config not available
    MODEL_DIR = Path(__file__).parent.parent / "data" / "models"
    LLAMA_MODEL_DIR = MODEL_DIR / "llama-3-8b"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LLAMA_MODEL_DIR, exist_ok=True)
    logger.info(f"Created model directories at {MODEL_DIR}")

def download_llama_model():
    """Download Llama-3-8B model from Hugging Face."""
    logger.info("Downloading Llama-3-8B model...")
    
    # Use transformers to download the model
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Download tokenizer and model
        logger.info("Downloading Llama-3-8B tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B", cache_dir=LLAMA_MODEL_DIR)
        
        logger.info("Downloading Llama-3-8B model (this may take a while)...")
        model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Meta-Llama-3-8B",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            cache_dir=LLAMA_MODEL_DIR
        )
        
        logger.info("Llama-3-8B model downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading Llama-3-8B model: {e}")
        logger.warning("Note: Llama-3 models require acceptance of Meta's license terms on Hugging Face.")
        logger.warning("Please visit https://huggingface.co/meta-llama/Meta-Llama-3-8B and accept the license.")

def check_gpu():
    """Check if GPU is available."""
    if torch.cuda.is_available():
        logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA version: {torch.version.cuda}")
        return True
    else:
        logger.warning("No GPU detected. Running in CPU-only mode will increase latency.")
        return False

def main():
    """Main function to download the Llama 3 model."""
    logger.info("Starting Llama 3 model download process...")
    
    # Check for GPU
    has_gpu = check_gpu()
    
    # Create directories
    create_directories()
    
    # Download model
    download_llama_model()
    
    logger.info("Llama 3 model downloaded successfully!")
    if not has_gpu:
        logger.warning("Note: Running without GPU will significantly increase latency.")

if __name__ == "__main__":
    main()
