#!/usr/bin/env python3
"""
Sentence Splitter and SONAR Encoder for Meta LCM Chatbot.
This module handles text preprocessing and concept vector generation.
"""

import os
import time
import logging
import nltk
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class SentenceSplitter:
    """
    Handles splitting text into sentences for processing.
    """
    
    def __init__(self):
        """Initialize the sentence splitter."""
        self.tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    
    def split(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text to split
            
        Returns:
            List of sentences
        """
        if not text or not text.strip():
            return []
        
        try:
            sentences = self.tokenizer.tokenize(text)
            return sentences
        except Exception as e:
            logger.error(f"Error splitting text: {e}")
            # Fallback to simple splitting
            return [s.strip() for s in text.split('.') if s.strip()]

class SONAREncoder:
    """
    Handles encoding text into concept vectors using SONAR.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the SONAR encoder.
        
        Args:
            model_path: Path to the SONAR encoder model
            device: Device to run encoding on ('cuda' or 'cpu')
        """
        self.model_path = model_path or os.path.join(Path(__file__).parent.parent, "models/sonar-encoder")
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Performance metrics
        self.encode_times = []
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the SONAR encoder model."""
        logger.info(f"Loading SONAR encoder from {self.model_path} on {self.device}")
        
        # In a real implementation, this would load the actual SONAR model
        # For this MVP, we'll simulate the model
        
        logger.info("SONAR encoder loaded successfully")
    
    def encode(self, sentences: List[str]) -> List[np.ndarray]:
        """
        Encode sentences into concept vectors.
        
        Args:
            sentences: List of sentences to encode
            
        Returns:
            List of concept vectors (numpy arrays)
        """
        start_time = time.time()
        
        # In a real implementation, this would use the SONAR model to encode sentences
        # For this MVP, we'll simulate the encoding process
        
        # Create mock concept vectors (768-dimensional)
        concept_vectors = [np.random.randn(768) for _ in sentences]
        
        # Record encoding time
        encode_time = time.time() - start_time
        self.encode_times.append(encode_time)
        
        logger.info(f"Encoded {len(sentences)} sentences in {encode_time:.4f} seconds")
        
        return concept_vectors

class SONARDecoder:
    """
    Handles decoding concept vectors back to text using SONAR.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the SONAR decoder.
        
        Args:
            model_path: Path to the SONAR decoder model
            device: Device to run decoding on ('cuda' or 'cpu')
        """
        self.model_path = model_path or os.path.join(Path(__file__).parent.parent, "models/sonar-decoder")
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Performance metrics
        self.decode_times = []
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the SONAR decoder model."""
        logger.info(f"Loading SONAR decoder from {self.model_path} on {self.device}")
        
        # In a real implementation, this would load the actual SONAR model
        # For this MVP, we'll simulate the model
        
        logger.info("SONAR decoder loaded successfully")
    
    def decode(self, concept_vector: np.ndarray) -> str:
        """
        Decode a concept vector back to text.
        
        Args:
            concept_vector: Concept vector to decode
            
        Returns:
            Decoded text
        """
        start_time = time.time()
        
        # In a real implementation, this would use the SONAR model to decode the concept vector
        # For this MVP, we'll simulate the decoding process
        
        # Generate a mock response based on the concept vector
        # In a real implementation, this would be the output of the SONAR decoder
        responses = [
            "This is a simulated response from the SONAR decoder.",
            "The concept vector has been decoded into this text.",
            "The LCM model has generated this response based on the input.",
            "Here's a response that demonstrates the concept-level reasoning capability.",
            "This text was generated from a concept vector, not token by token."
        ]
        response = np.random.choice(responses)
        
        # Record decoding time
        decode_time = time.time() - start_time
        self.decode_times.append(decode_time)
        
        logger.info(f"Decoded concept vector in {decode_time:.4f} seconds")
        
        return response

class TextProcessor:
    """
    Combines sentence splitting, encoding, and decoding for text processing.
    """
    
    def __init__(self):
        """Initialize the text processor with its components."""
        self.splitter = SentenceSplitter()
        self.encoder = SONAREncoder()
        self.decoder = SONARDecoder()
    
    def process_input(self, text: str) -> Tuple[List[str], List[np.ndarray]]:
        """
        Process input text: split into sentences and encode into concept vectors.
        
        Args:
            text: Input text to process
            
        Returns:
            Tuple of (sentences, concept_vectors)
        """
        # Split text into sentences
        sentences = self.splitter.split(text)
        
        # Encode sentences into concept vectors
        concept_vectors = self.encoder.encode(sentences)
        
        return sentences, concept_vectors
    
    def process_output(self, concept_vector: np.ndarray) -> str:
        """
        Process output concept vector: decode into text.
        
        Args:
            concept_vector: Concept vector to decode
            
        Returns:
            Decoded text
        """
        # Decode concept vector into text
        text = self.decoder.decode(concept_vector)
        
        return text

# Simple test function
def test_processor():
    """Test the text processor."""
    # Initialize processor
    processor = TextProcessor()
    
    # Test input text
    test_text = "This is a test sentence. Here's another one. And a third one for good measure."
    
    # Process input
    sentences, concept_vectors = processor.process_input(test_text)
    
    # Print results
    print(f"Input text: {test_text}")
    print(f"Split into {len(sentences)} sentences:")
    for i, sentence in enumerate(sentences):
        print(f"  {i+1}. {sentence}")
    
    print(f"Encoded into {len(concept_vectors)} concept vectors.")
    
    # Test output processing
    if concept_vectors:
        output_text = processor.process_output(concept_vectors[0])
        print(f"Decoded output: {output_text}")
    
    return sentences, concept_vectors

if __name__ == "__main__":
    # Run test if executed directly
    test_processor()
