#!/usr/bin/env python3
"""
Model Comparison Module for Meta LCM Chatbot.
This module handles comparison between LCM-7B and Llama-7B models.
"""

import os
import time
import logging
import json
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

class ModelComparison:
    """
    Handles comparison between LCM-7B and Llama-7B models.
    Provides metrics for speed, accuracy, reasoning, and multimodal capabilities.
    """
    
    def __init__(self, lcm_model=None, llama_model=None):
        """
        Initialize the model comparison module.
        
        Args:
            lcm_model: LCM model instance (optional)
            llama_model: Llama model instance (optional)
        """
        self.lcm_model = lcm_model
        self.llama_model = llama_model
        self.comparison_metrics = {}
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load pre-defined test cases for model comparison.
        
        Returns:
            Dictionary of test cases by category
        """
        # In a real implementation, these would be loaded from a file or database
        return {
            "general": [
                {"prompt": "Explain the concept of quantum entanglement in simple terms.", "category": "explanation"},
                {"prompt": "What are the main differences between renewable and non-renewable energy sources?", "category": "comparison"}
            ],
            "reasoning": [
                {"prompt": "If a train travels at 60 mph for 3 hours, then at 80 mph for 2 hours, what is the average speed?", "category": "math"},
                {"prompt": "A bat and ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?", "category": "logic"}
            ],
            "creativity": [
                {"prompt": "Write a short poem about artificial intelligence.", "category": "creative"},
                {"prompt": "Invent a new sport that combines elements of basketball and chess.", "category": "creative"}
            ],
            "cross_lingual": [
                {"prompt": "Translate 'The quick brown fox jumps over the lazy dog' to French, Spanish, and German.", "category": "translation"},
                {"prompt": "Explain the concept of 'hygge' from Danish culture.", "category": "cultural"}
            ],
            "multimodal": [
                {"prompt": "Describe what you see in this image: [IMAGE_PLACEHOLDER]", "category": "image_description", "requires_image": True},
                {"prompt": "What emotions does this image convey? [IMAGE_PLACEHOLDER]", "category": "image_emotion", "requires_image": True}
            ]
        }
    
    def compare_responses(self, prompt: str, lcm_response: str, llama_response: str, 
                         lcm_metrics: Dict[str, Any], llama_metrics: Dict[str, Any],
                         image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare responses from LCM and Llama models.
        
        Args:
            prompt: User prompt
            lcm_response: Response from LCM model
            llama_response: Response from Llama model
            lcm_metrics: Performance metrics from LCM model
            llama_metrics: Performance metrics from Llama model
            image_path: Path to image for multimodal prompts (optional)
            
        Returns:
            Dictionary of comparison metrics
        """
        # Calculate basic metrics
        comparison = {
            "prompt": prompt,
            "lcm_response": lcm_response,
            "llama_response": llama_response,
            "speed": {
                "lcm_time": lcm_metrics.get("processing_time", 0),
                "llama_time": llama_metrics.get("processing_time", 0),
                "difference_percent": self._calculate_percentage_difference(
                    lcm_metrics.get("processing_time", 0),
                    llama_metrics.get("processing_time", 0)
                ),
                "faster_model": "LCM" if lcm_metrics.get("processing_time", 0) < llama_metrics.get("processing_time", 0) else "Llama"
            },
            "length": {
                "lcm_chars": len(lcm_response),
                "llama_chars": len(llama_response),
                "difference_percent": self._calculate_percentage_difference(len(lcm_response), len(llama_response)),
                "longer_response": "LCM" if len(lcm_response) > len(llama_response) else "Llama"
            },
            "complexity": {
                "lcm_complexity": self._calculate_text_complexity(lcm_response),
                "llama_complexity": self._calculate_text_complexity(llama_response),
                "difference_percent": self._calculate_percentage_difference(
                    self._calculate_text_complexity(lcm_response),
                    self._calculate_text_complexity(llama_response)
                ),
                "more_complex": "LCM" if self._calculate_text_complexity(lcm_response) > self._calculate_text_complexity(llama_response) else "Llama"
            }
        }
        
        # Add advanced metrics
        comparison.update({
            "reasoning": self._compare_reasoning(prompt, lcm_response, llama_response),
            "creativity": self._compare_creativity(prompt, lcm_response, llama_response),
            "factuality": self._compare_factuality(prompt, lcm_response, llama_response),
            "hallucination_risk": self._compare_hallucination_risk(prompt, lcm_response, llama_response)
        })
        
        # Add multimodal metrics if image is provided
        if image_path:
            comparison.update({
                "multimodal": self._compare_multimodal(prompt, lcm_response, llama_response, image_path)
            })
        
        # Store comparison for later analysis
        self.comparison_metrics[prompt] = comparison
        
        return comparison
    
    def _calculate_percentage_difference(self, value1: float, value2: float) -> float:
        """
        Calculate percentage difference between two values.
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            Percentage difference
        """
        if value1 == 0 and value2 == 0:
            return 0
        
        avg = (value1 + value2) / 2
        if avg == 0:
            return 0
        
        return abs(value1 - value2) / avg * 100
    
    def _calculate_text_complexity(self, text: str) -> float:
        """
        Calculate text complexity score.
        
        Args:
            text: Text to analyze
            
        Returns:
            Complexity score
        """
        # Simple implementation - in a real system, this would be more sophisticated
        words = text.split()
        if not words:
            return 0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        sentence_count = max(1, sentence_count)  # Avoid division by zero
        avg_sentence_length = len(words) / sentence_count
        
        # Weighted score
        return (0.6 * avg_word_length) + (0.4 * avg_sentence_length)
    
    def _compare_reasoning(self, prompt: str, lcm_response: str, llama_response: str) -> Dict[str, Any]:
        """
        Compare reasoning capabilities between models.
        
        Args:
            prompt: User prompt
            lcm_response: Response from LCM model
            llama_response: Response from Llama model
            
        Returns:
            Dictionary of reasoning comparison metrics
        """
        # Simple implementation - in a real system, this would use more sophisticated analysis
        lcm_reasoning_markers = self._count_reasoning_markers(lcm_response)
        llama_reasoning_markers = self._count_reasoning_markers(llama_response)
        
        return {
            "lcm_reasoning_score": lcm_reasoning_markers,
            "llama_reasoning_score": llama_reasoning_markers,
            "difference": lcm_reasoning_markers - llama_reasoning_markers,
            "better_reasoning": "LCM" if lcm_reasoning_markers > llama_reasoning_markers else "Llama"
        }
    
    def _count_reasoning_markers(self, text: str) -> int:
        """
        Count reasoning markers in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Count of reasoning markers
        """
        reasoning_phrases = [
            "because", "therefore", "thus", "as a result", "consequently",
            "first", "second", "third", "finally", "in conclusion",
            "if", "then", "else", "given that", "assuming",
            "however", "although", "despite", "nevertheless", "conversely"
        ]
        
        count = 0
        lower_text = text.lower()
        for phrase in reasoning_phrases:
            count += lower_text.count(phrase)
        
        return count
    
    def _compare_creativity(self, prompt: str, lcm_response: str, llama_response: str) -> Dict[str, Any]:
        """
        Compare creativity between models.
        
        Args:
            prompt: User prompt
            lcm_response: Response from LCM model
            llama_response: Response from Llama model
            
        Returns:
            Dictionary of creativity comparison metrics
        """
        # Simple implementation - in a real system, this would use more sophisticated analysis
        lcm_unique_words = len(set(lcm_response.lower().split()))
        llama_unique_words = len(set(llama_response.lower().split()))
        
        lcm_creativity_score = lcm_unique_words / max(1, len(lcm_response.split()))
        llama_creativity_score = llama_unique_words / max(1, len(llama_response.split()))
        
        return {
            "lcm_creativity_score": round(lcm_creativity_score, 3),
            "llama_creativity_score": round(llama_creativity_score, 3),
            "difference": round(lcm_creativity_score - llama_creativity_score, 3),
            "more_creative": "LCM" if lcm_creativity_score > llama_creativity_score else "Llama"
        }
    
    def _compare_factuality(self, prompt: str, lcm_response: str, llama_response: str) -> Dict[str, Any]:
        """
        Compare factuality between models.
        
        Args:
            prompt: User prompt
            lcm_response: Response from LCM model
            llama_response: Response from Llama model
            
        Returns:
            Dictionary of factuality comparison metrics
        """
        # Simple implementation - in a real system, this would use fact-checking
        lcm_factuality = self._estimate_factuality(lcm_response)
        llama_factuality = self._estimate_factuality(llama_response)
        
        return {
            "lcm_factuality_score": lcm_factuality,
            "llama_factuality_score": llama_factuality,
            "difference": lcm_factuality - llama_factuality,
            "more_factual": "LCM" if lcm_factuality > llama_factuality else "Llama"
        }
    
    def _estimate_factuality(self, text: str) -> float:
        """
        Estimate factuality score of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Factuality score (0-1)
        """
        # Simple implementation - in a real system, this would use fact-checking
        # Here we're using presence of hedging phrases as a proxy for lower factuality
        hedging_phrases = [
            "i think", "probably", "might be", "could be", "possibly",
            "perhaps", "maybe", "in my opinion", "i believe", "seems like"
        ]
        
        hedging_count = 0
        lower_text = text.lower()
        for phrase in hedging_phrases:
            hedging_count += lower_text.count(phrase)
        
        # More hedging = lower factuality score
        factuality = max(0, min(1, 1 - (hedging_count * 0.1)))
        return round(factuality, 2)
    
    def _compare_hallucination_risk(self, prompt: str, lcm_response: str, llama_response: str) -> Dict[str, Any]:
        """
        Compare hallucination risk between models.
        
        Args:
            prompt: User prompt
            lcm_response: Response from LCM model
            llama_response: Response from Llama model
            
        Returns:
            Dictionary of hallucination risk comparison metrics
        """
        # Simple implementation - in a real system, this would use more sophisticated analysis
        lcm_risk = self._estimate_hallucination_risk(lcm_response)
        llama_risk = self._estimate_hallucination_risk(llama_response)
        
        return {
            "lcm_hallucination_risk": lcm_risk,
            "llama_hallucination_risk": llama_risk,
            "difference": lcm_risk - llama_risk,
            "lower_risk": "LCM" if lcm_risk < llama_risk else "Llama"
        }
    
    def _estimate_hallucination_risk(self, text: str) -> float:
        """
        Estimate hallucination risk of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Hallucination risk score (0-1)
        """
        # Simple implementation - in a real system, this would use more sophisticated analysis
        # Here we're using specificity (numbers, dates, names) as a proxy for higher hallucination risk
        specificity_markers = [
            r"\d{4}", r"\d{1,2}/\d{1,2}/\d{2,4}", r"\d{1,3}\.\d{1,3}",
            r"\d{1,3},\d{3}", r"\d{1,3}%", r"Dr\.", r"Prof\."
        ]
        
        specificity_count = 0
        for marker in specificity_markers:
            import re
            specificity_count += len(re.findall(marker, text))
        
        # More specificity without hedging = higher hallucination risk
        hedging_count = self._count_hedging(text)
        
        if hedging_count > 0:
            # Hedging reduces hallucination risk
            risk = specificity_count / (hedging_count * 10 + specificity_count + 1)
        else:
            # No hedging with high specificity = higher risk
            risk = min(1, specificity_count * 0.1)
        
        return round(risk, 2)
    
    def _count_hedging(self, text: str) -> int:
        """
        Count hedging phrases in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Count of hedging phrases
        """
        hedging_phrases = [
            "i think", "probably", "might be", "could be", "possibly",
            "perhaps", "maybe", "in my opinion", "i believe", "seems like"
        ]
        
        count = 0
        lower_text = text.lower()
        for phrase in hedging_phrases:
            count += lower_text.count(phrase)
        
        return count
    
    def _compare_multimodal(self, prompt: str, lcm_response: str, llama_response: str, image_path: str) -> Dict[str, Any]:
        """
        Compare multimodal capabilities between models.
        
        Args:
            prompt: User prompt
            lcm_response: Response from LCM model
            llama_response: Response from Llama model
            image_path: Path to image
            
        Returns:
            Dictionary of multimodal comparison metrics
        """
        # Simple implementation - in a real system, this would use more sophisticated analysis
        # Here we're using image-related vocabulary as a proxy for image understanding
        image_vocabulary = [
            "image", "picture", "photo", "photograph", "visual",
            "color", "shape", "object", "background", "foreground",
          
(Content truncated due to size limit. Use line ranges to read in chunks)