#!/usr/bin/env python3
"""
Setup script for LCM (Large Concept Model) from Meta's GitHub repository.
This script clones the necessary repositories and sets up the environment for LCM.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Add parent directory to path to import from config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import settings from config
try:
    from config import settings
    MODEL_DIR = Path(settings.MODELS_DIR)
    LCM_MODEL_DIR = MODEL_DIR / "lcm"
except ImportError:
    # Fallback if config not available
    MODEL_DIR = Path(__file__).parent.parent / "data" / "models"
    LCM_MODEL_DIR = MODEL_DIR / "lcm"

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
    logger.info(f"Created model directories at {MODEL_DIR}")

def run_command(command, cwd=None):
    """Run a shell command and log the output."""
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            cwd=cwd
        )
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def clone_repositories():
    """Clone the necessary repositories from GitHub."""
    # Create directories for repositories
    repo_dir = Path(MODEL_DIR) / "repos"
    os.makedirs(repo_dir, exist_ok=True)
    
    # Check if large_concept_model repository already exists
    lcm_repo_path = repo_dir / "large_concept_model"
    if lcm_repo_path.exists():
        logger.info(f"LCM repository already exists at {lcm_repo_path}")
    else:
        # Clone the large_concept_model repository
        logger.info("Cloning the large_concept_model repository...")
        if not run_command("git clone https://github.com/facebookresearch/large_concept_model.git", cwd=repo_dir):
            return False
    
    # Check if SONAR repository already exists
    sonar_repo_path = repo_dir / "SONAR"
    if sonar_repo_path.exists():
        logger.info(f"SONAR repository already exists at {sonar_repo_path}")
    else:
        # Clone the SONAR repository
        logger.info("Cloning the SONAR repository...")
        if not run_command("git clone https://github.com/facebookresearch/SONAR.git", cwd=repo_dir):
            return False
    
    return True

def setup_environment():
    """Set up the environment for LCM."""
    repo_dir = Path(MODEL_DIR) / "repos"
    lcm_repo_dir = repo_dir / "large_concept_model"
    
    # Create a README file in the LCM directory with instructions
    readme_content = """# LCM (Large Concept Model) Setup

## Repository Information

The LCM code has been cloned from Meta's GitHub repositories:
- LCM: https://github.com/facebookresearch/large_concept_model
- SONAR: https://github.com/facebookresearch/SONAR

## Important Note

The Meta GitHub repository does not provide pre-trained LCM models for direct download.
Instead, it provides code to train and fine-tune LCM models from scratch.

To use LCM, you have the following options:

1. **Train your own LCM model** using the code in the cloned repository
   - Follow the instructions in the repository's README.md
   - This requires significant computational resources

2. **Use SONAR embeddings directly**
   - SONAR models will be automatically downloaded when using the library
   - See examples in the SONAR repository

3. **Wait for official model releases**
   - Meta may release pre-trained models in the future

## Repository Locations

- LCM code: {lcm_repo_dir}
- SONAR code: {repo_dir}/SONAR
"""
    
    readme_path = LCM_MODEL_DIR / "README.md"
    with open(readme_path, "w") as f:
        f.write(readme_content.format(lcm_repo_dir=lcm_repo_dir, repo_dir=repo_dir))
    
    logger.info(f"Created README file at {readme_path}")
    return True

def main():
    """Main function to set up the LCM environment."""
    logger.info("Starting LCM setup process from GitHub...")
    
    # Create directories
    create_directories()
    
    # Clone repositories
    if not clone_repositories():
        logger.error("Failed to clone repositories. Exiting.")
        sys.exit(1)
    
    # Set up environment
    if not setup_environment():
        logger.error("Failed to set up environment. Exiting.")
        sys.exit(1)
    
    logger.info("LCM environment set up successfully!")
    logger.info(f"The LCM code and documentation are located in the '{LCM_MODEL_DIR}' directory.")
    logger.info("Note: Pre-trained LCM models are not available for direct download from Meta's GitHub repository.")
    logger.info("Please refer to the README.md file in the LCM directory for more information.")

if __name__ == "__main__":
    main()