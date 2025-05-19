#!/usr/bin/env python3
"""
Download script for LCM-7B and Llama-7B models.
This script downloads the necessary models for the LCM Framework.
"""

import os
import sys
import logging
import requests
from tqdm import tqdm
import torch
from pathlib import Path
import shutil
import subprocess

# Add parent directory to path to import from config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import settings from config
try:
    from config import settings
    MODEL_DIR = Path(settings.MODELS_DIR)
    LCM_MODEL_DIR = MODEL_DIR / "lcm-7b"
    LLAMA_MODEL_DIR = MODEL_DIR / "llama-7b"
except ImportError:
    # Fallback if config not available
    MODEL_DIR = Path(__file__).parent.parent / "data" / "models"
    LCM_MODEL_DIR = MODEL_DIR / "lcm-7b"
    LLAMA_MODEL_DIR = MODEL_DIR / "llama-7b"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LCM_MODEL_DIR, exist_ok=True)
    os.makedirs(LLAMA_MODEL_DIR, exist_ok=True)
    logger.info(f"Created model directories at {MODEL_DIR}")

def download_file(url, destination):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    
    with open(destination, 'wb') as file, tqdm(
            desc=os.path.basename(destination),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
        for data in response.iter_content(block_size):
            size = file.write(data)
            bar.update(size)

def download_lcm_model():
    """Download LCM-7B model from Hugging Face."""
    logger.info("Downloading LCM-7B model...")
    
    # Use transformers to download the model
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Download tokenizer and model
        logger.info("Downloading LCM-7B tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("facebook/lcm-7b", cache_dir=LCM_MODEL_DIR)
        
        logger.info("Downloading LCM-7B model (this may take a while)...")
        model = AutoModelForCausalLM.from_pretrained(
            "facebook/lcm-7b", 
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            cache_dir=LCM_MODEL_DIR
        )
        
        logger.info("LCM-7B model downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading LCM-7B model: {e}")
        sys.exit(1)

def download_llama_model():
    """Download Llama-7B model from Hugging Face."""
    logger.info("Downloading Llama-7B model...")
    
    # Use transformers to download the model
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Download tokenizer and model
        logger.info("Downloading Llama-7B tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf", cache_dir=LLAMA_MODEL_DIR)
        
        logger.info("Downloading Llama-7B model (this may take a while)...")
        model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-2-7b-hf", 
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            cache_dir=LLAMA_MODEL_DIR
        )
        
        logger.info("Llama-7B model downloaded successfully")
    except Exception as e:
        logger.error(f"Error downloading Llama-7B model: {e}")
        logger.warning("Note: Llama-2 models require acceptance of Meta's license terms on Hugging Face.")
        logger.warning("Please visit https://huggingface.co/meta-llama/Llama-2-7b-hf and accept the license.")

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
    """Main function to download all models."""
    logger.info("Starting model download process...")
    
    # Check for GPU
    has_gpu = check_gpu()
    
    # Create directories
    create_directories()
    
    # Download models
    download_lcm_model()
    download_llama_model()
    
    logger.info("All models downloaded successfully!")
    if not has_gpu:
        logger.warning("Note: Running without GPU will significantly increase latency.")

if __name__ == "__main__":
    main()
