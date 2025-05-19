#!/usr/bin/env python3
"""
Example script demonstrating how to use SONAR embeddings directly.
This script shows how to encode sentences into the SONAR embedding space
and compute similarity between them.
"""

import os
import sys
import logging
import torch
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Install necessary dependencies if not already installed."""
    # First, check if fairseq2 is installed
    try:
        import fairseq2
        logger.info("fairseq2 is already installed.")
    except ImportError:
        logger.info("Installing fairseq2...")
        # Get PyTorch version
        import torch
        torch_version = torch.__version__.split('+')[0]  # Remove CUDA suffix if present
        
        # Install fairseq2 with the matching PyTorch version
        logger.info(f"Installing fairseq2 for PyTorch {torch_version}...")
        os.system(f"pip install fairseq2==0.4.5 --extra-index-url https://fair.pkg.atmeta.com/fairseq2/whl/pt{torch_version}/cpu")
        logger.info("fairseq2 installed successfully.")
    
    # Then, check if SONAR is installed
    try:
        import sonar
        logger.info("SONAR is already installed.")
    except ImportError:
        logger.info("Installing SONAR...")
        os.system("pip install sonar-space")
        logger.info("SONAR installed successfully.")

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def main():
    """Main function to demonstrate SONAR embeddings."""
    logger.info("Setting up environment...")
    setup_environment()
    
    # Import SONAR after ensuring it's installed
    from sonar.inference_pipelines.text import TextToEmbeddingModelPipeline
    
    logger.info("Loading SONAR text encoder...")
    # Check if GPU is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    # Initialize the SONAR text encoder
    t2vec_model = TextToEmbeddingModelPipeline(
        encoder="text_sonar_basic_encoder",
        tokenizer="text_sonar_basic_encoder",
        device=device,
        dtype=dtype
    )
    
    logger.info(f"SONAR text encoder loaded successfully on {device}.")
    
    # Example sentences
    sentences = [
        "The Large Concept Model (LCM) operates on an explicit higher-level semantic representation.",
        "LCM uses the SONAR embedding space, which supports up to 200 languages in text.",
        "Llama 3 is a large language model developed by Meta.",
        "The LCM Framework provides tools for comparing language models."
    ]
    
    logger.info("Encoding sentences...")
    # Encode sentences into the SONAR embedding space
    embeddings = t2vec_model.predict(sentences, source_lang="eng_Latn")
    
    logger.info(f"Embeddings shape: {embeddings.shape}")
    
    # Convert to numpy for easier manipulation
    embeddings_np = embeddings.cpu().numpy()
    
    # Compute similarity matrix
    logger.info("Computing similarity matrix...")
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            similarity_matrix[i, j] = cosine_similarity(embeddings_np[i], embeddings_np[j])
    
    # Print similarity matrix
    logger.info("Similarity matrix:")
    for i, sentence1 in enumerate(sentences):
        logger.info(f"Sentence {i+1}: {sentence1[:50]}...")
    
    logger.info("\nSimilarity Matrix:")
    for i in range(len(sentences)):
        similarity_row = " ".join([f"{similarity_matrix[i, j]:.4f}" for j in range(len(sentences))])
        logger.info(f"Sentence {i+1}: {similarity_row}")
    
    # Find most similar pair
    max_sim = 0
    max_i, max_j = 0, 0
    for i in range(len(sentences)):
        for j in range(i+1, len(sentences)):
            if similarity_matrix[i, j] > max_sim:
                max_sim = similarity_matrix[i, j]
                max_i, max_j = i, j
    
    logger.info("\nMost similar pair:")
    logger.info(f"Sentence {max_i+1}: {sentences[max_i]}")
    logger.info(f"Sentence {max_j+1}: {sentences[max_j]}")
    logger.info(f"Similarity: {max_sim:.4f}")
    
    logger.info("\nThis demonstrates how to use SONAR embeddings directly for semantic similarity.")
    logger.info("These embeddings can be used for various NLP tasks like clustering, classification, and retrieval.")

if __name__ == "__main__":
    main()