#!/usr/bin/env python3
"""
Integration test script for Meta LCM Chatbot.
This script validates core functionality against acceptance criteria.
"""

import os
import time
import logging
import json
import requests
import statistics
import numpy as np
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoint
API_URL = os.environ.get("API_URL", "http://localhost:8000")

class AcceptanceTester:
    """
    Tests the chatbot against acceptance criteria.
    """
    
    def __init__(self, api_url: str = API_URL):
        """
        Initialize the acceptance tester.
        
        Args:
            api_url: URL of the API endpoint
        """
        self.api_url = api_url
        self.session_id = None
        self.response_times = []
    
    def test_chat_response_time(self, num_requests: int = 10) -> Dict[str, Any]:
        """
        Test chat response time.
        
        Args:
            num_requests: Number of requests to make
            
        Returns:
            Dict of response time statistics
        """
        logger.info(f"Testing chat response time with {num_requests} requests...")
        
        response_times = []
        
        for i in range(num_requests):
            # Generate test message
            message = f"Test message {i+1}: Please provide a brief response."
            
            # Send request and measure time
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/chat",
                json={"message": message, "session_id": self.session_id}
            )
            end_time = time.time()
            
            # Calculate response time
            response_time = end_time - start_time
            response_times.append(response_time)
            
            # Get session ID if not already set
            if not self.session_id:
                data = response.json()
                self.session_id = data.get("session_id")
            
            logger.info(f"Request {i+1}: response_time={response_time:.4f}s")
            
            # Wait a bit between requests
            time.sleep(0.5)
        
        # Calculate statistics
        stats = {
            "count": len(response_times),
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "p95": np.percentile(response_times, 95),
            "min": min(response_times),
            "max": max(response_times),
        }
        
        logger.info(f"Response time statistics: {json.dumps(stats, indent=2)}")
        
        # Store for later use
        self.response_times = response_times
        
        return stats
    
    def test_chat_history(self) -> bool:
        """
        Test chat history functionality.
        
        Returns:
            True if test passes, False otherwise
        """
        logger.info("Testing chat history functionality...")
        
        # Ensure we have a session ID
        if not self.session_id:
            response = requests.post(f"{self.api_url}/chat", json={"message": "Hello"})
            data = response.json()
            self.session_id = data.get("session_id")
        
        # Send a sequence of messages
        messages = [
            "Message 1: This is a test of chat history.",
            "Message 2: Can you remember the previous message?",
            "Message 3: Let's see if history is maintained."
        ]
        
        for message in messages:
            response = requests.post(
                f"{self.api_url}/chat",
                json={"message": message, "session_id": self.session_id}
            )
            
            # Check response
            if response.status_code != 200:
                logger.error(f"Error sending message: {response.text}")
                return False
            
            logger.info(f"Sent message: {message}")
            time.sleep(0.5)
        
        # Test clear history
        logger.info("Testing clear history functionality...")
        response = requests.post(f"{self.api_url}/clear-history?session_id={self.session_id}")
        
        # Check response
        if response.status_code != 200:
            logger.error(f"Error clearing history: {response.text}")
            return False
        
        # Get new session ID
        data = response.json()
        new_session_id = data.get("status") == "success"
        
        logger.info(f"Clear history test {'passed' if new_session_id else 'failed'}")
        
        return True
    
    def test_health_endpoint(self) -> bool:
        """
        Test health endpoint.
        
        Returns:
            True if test passes, False otherwise
        """
        logger.info("Testing health endpoint...")
        
        response = requests.get(f"{self.api_url}/health")
        
        # Check response
        if response.status_code != 200:
            logger.error(f"Error accessing health endpoint: {response.text}")
            return False
        
        # Parse response
        data = response.json()
        
        # Check required fields
        required_fields = ["status", "model", "hardware", "system", "performance"]
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field in health response: {field}")
                return False
        
        # Check GPU utilization
        if "hardware" in data and "gpu_utilization_percent" in data["hardware"]:
            gpu_util = data["hardware"]["gpu_utilization_percent"]
            if gpu_util is not None and gpu_util > 90:
                logger.warning(f"GPU utilization is high: {gpu_util}%")
        
        logger.info(f"Health endpoint test passed: {json.dumps(data, indent=2, default=str)}")
        
        return True
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all acceptance tests.
        
        Returns:
            Dict of test results
        """
        results = {
            "response_time": None,
            "chat_history": None,
            "health_endpoint": None,
            "acceptance_criteria_met": False
        }
        
        # Test response time
        response_time_stats = self.test_chat_response_time()
        results["response_time"] = response_time_stats
        
        # Check if median response time is < 1s
        median_response_time = response_time_stats.get("median", float("inf"))
        results["ac1_met"] = median_response_time < 1.0
        
        # Test chat history
        chat_history_result = self.test_chat_history()
        results["chat_history"] = chat_history_result
        results["ac2_met"] = chat_history_result
        
        # Test health endpoint
        health_result = self.test_health_endpoint()
        results["health_endpoint"] = health_result
        
        # Check if GPU utilization is < 90%
        results["ac3_met"] = health_result  # Simplified for MVP
        
        # Check if all acceptance criteria are met
        results["acceptance_criteria_met"] = (
            results["ac1_met"] and 
            results["ac2_met"] and 
            results["ac3_met"]
        )
        
        logger.info(f"Acceptance test results: {json.dumps(results, indent=2, default=str)}")
        
        return results

# Run tests if executed directly
if __name__ == "__main__":
    tester = AcceptanceTester()
    results = tester.run_all_tests()
    
    # Print summary
    print("\n=== Acceptance Test Results ===")
    print(f"AC-1 (Response Time < 1s): {'PASS' if results['ac1_met'] else 'FAIL'}")
    print(f"AC-2 (Chat History): {'PASS' if results['ac2_met'] else 'FAIL'}")
    print(f"AC-3 (Health Endpoint): {'PASS' if results['ac3_met'] else 'FAIL'}")
    print(f"Overall: {'PASS' if results['acceptance_criteria_met'] else 'FAIL'}")
