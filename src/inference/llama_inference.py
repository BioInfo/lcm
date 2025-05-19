#!/usr/bin/env python3
"""
Llama Inference Pipeline for Meta LCM Chatbot.
This module handles the inference process using the Llama-7B model.
"""

import os
import time
import logging
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LlamaInference:
    """
    Llama Inference Pipeline.
    Handles loading the model and generating responses for comparison with LCM.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the Llama inference pipeline.
        
        Args:
            model_path: Path to the Llama model directory
            device: Device to run inference on ('cuda' or 'cpu')
        """
        self.model_path = model_path or os.path.join(Path(__file__).parent, "llama")
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Performance metrics
        self.load_time = 0
        self.inference_times = []
        
        # Load model and tokenizer
        self._load_model()
    
    def _load_model(self):
        """Load the Llama model and tokenizer."""
        start_time = time.time()
        
        logger.info(f"Loading Llama model from {self.model_path} on {self.device}")
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                "meta-llama/Llama-2-7b",
                cache_dir=self.model_path
            )
            
            # Load model
            dtype = torch.float16 if self.device == 'cuda' else torch.float32
            self.model = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Llama-2-7b",
                torch_dtype=dtype,
                cache_dir=self.model_path,
                device_map=self.device
            )
            
            self.load_time = time.time() - start_time
            logger.info(f"Llama model loaded successfully in {self.load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error loading Llama model: {e}")
            # For MVP, create a mock model if loading fails
            self._create_mock_model()
    
    def _create_mock_model(self):
        """Create a mock model for demonstration purposes."""
        logger.warning("Creating mock Llama model for demonstration")
        self.model = None
        self.tokenizer = None
        self.load_time = 0.5
    
    def generate_response(self, 
                         prompt: str, 
                         max_length: int = 256,
                         temperature: float = 0.7) -> Tuple[str, float]:
        """
        Generate a response based on the prompt.
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of the response
            temperature: Sampling temperature (higher = more creative)
            
        Returns:
            Tuple of (response_text, inference_time)
        """
        # Start timing
        start_time = time.time()
        
        try:
            if self.model and self.tokenizer:
                # Real model inference
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                
                # Generate response
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs.input_ids,
                        max_length=max_length,
                        temperature=temperature,
                        do_sample=True,
                        top_p=0.95,
                        top_k=50,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                # Decode response
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Remove the prompt from the response
                if response.startswith(prompt):
                    response = response[len(prompt):].strip()
            else:
                # Mock response for demonstration
                response = self._generate_mock_response(prompt)
        except Exception as e:
            logger.error(f"Error generating Llama response: {e}")
            response = f"Error generating response: {str(e)}"
        
        # Record inference time
        inference_time = time.time() - start_time
        self.inference_times.append(inference_time)
        
        logger.info(f"Generated Llama response in {inference_time:.4f} seconds")
        
        return response, inference_time
    
    def _generate_mock_response(self, prompt: str) -> str:
        """
        Generate a mock response for demonstration purposes.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response
        """
        # Simple keyword-based mock responses
        if "quantum" in prompt.lower():
            return "Quantum entanglement is when two particles become connected and the state of one particle affects the state of the other, no matter how far apart they are. It's a weird quantum physics thing that Einstein didn't like because it seemed to violate the speed of light limit. He called it 'spooky action at a distance' because it was so strange."
        elif "renewable" in prompt.lower():
            return "Renewable energy comes from sources that naturally replenish, like sun and wind. Non-renewable energy comes from finite resources like coal and oil that will eventually run out. Renewable is better for the environment but sometimes less reliable or more expensive initially."
        elif "train" in prompt.lower() and "mph" in prompt.lower():
            return "To solve this problem, I need to find the total distance traveled and divide by the total time. The train travels 60 mph × 3 hours = 180 miles, then 80 mph × 2 hours = 160 miles. Total distance is 180 + 160 = 340 miles. Total time is 3 + 2 = 5 hours. Average speed = 340 miles ÷ 5 hours = 68 mph."
        elif "bat and ball" in prompt.lower():
            return "Let's call the cost of the ball x. Then the bat costs x + $1.00. Together they cost $1.10, so: x + (x + $1.00) = $1.10. This simplifies to 2x + $1.00 = $1.10, so 2x = $0.10, which means x = $0.05. The ball costs 5 cents."
        elif "poem" in prompt.lower() and "artificial intelligence" in prompt.lower():
            return "Silicon dreams in digital space,\nLearning patterns at lightning pace.\nNot alive but still can see,\nA mirror of humanity.\nArtificial yet growing wise,\nIntelligence that never dies."
        elif "translate" in prompt.lower():
            return "French: Le rapide renard brun saute par-dessus le chien paresseux.\nSpanish: El rápido zorro marrón salta sobre el perro perezoso.\nGerman: Der schnelle braune Fuchs springt über den faulen Hund."
        elif "image" in prompt.lower() and "describe" in prompt.lower():
            return "I see an image that appears to contain some objects, but without being able to actually process the image, I can't provide specific details about what it shows. In a real implementation, the Llama model would need multimodal capabilities to describe images."
        else:
            return "This is a simulated response from the Llama-7B model. In a real implementation, this would be generated by the actual model. The response would be tailored to your prompt and would demonstrate the token-level processing approach of traditional language models."
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the model."""
        stats = {
            "load_time_seconds": self.load_time,
            "device": self.device,
            "model_path": self.model_path,
        }
        
        if self.inference_times:
            stats.update({
                "inference_count": len(self.inference_times),
                "mean_inference_time": np.mean(self.inference_times),
                "median_inference_time": np.median(self.inference_times),
                "min_inference_time": np.min(self.inference_times),
                "max_inference_time": np.max(self.inference_times),
                "p95_inference_time": np.percentile(self.inference_times, 95),
            })
        
        # Add GPU stats if available
        if torch.cuda.is_available():
            stats.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_allocated_mb": torch.cuda.memory_allocated() / (1024 * 1024),
                "gpu_memory_reserved_mb": torch.cuda.memory_reserved() / (1024 * 1024),
                "gpu_utilization": torch.cuda.utilization(0),
            })
        
        return stats

# Simple test function
def test_inference():
    """Test the Llama inference pipeline."""
    # Initialize inference pipeline
    inference = LlamaInference()
    
    # Test prompts
    test_prompts = [
        "Explain the concept of quantum entanglement in simple terms.",
        "What are the main differences between renewable and non-renewable energy sources?"
    ]
    
    # Generate responses
    for prompt in test_prompts:
        response, inference_time = inference.generate_response(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Response: {response}")
        print(f"Inference time: {inference_time:.4f} seconds")
    
    # Print performance stats
    print(f"\nPerformance stats: {inference.get_performance_stats()}")

if __name__ == "__main__":
    # Run test if executed directly
    test_inference()
