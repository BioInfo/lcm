#!/usr/bin/env python3
"""
Latency and Stress Testing for Meta LCM Chatbot.
This script performs latency and stress testing to evaluate performance under load.
"""

import os
import time
import logging
import json
import requests
import statistics
import numpy as np
import threading
import concurrent.futures
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoint
API_URL = os.environ.get("API_URL", "http://localhost:8000")

class StressTester:
    """
    Performs latency and stress testing for the chatbot.
    """
    
    def __init__(self, api_url: str = API_URL):
        """
        Initialize the stress tester.
        
        Args:
            api_url: URL of the API endpoint
        """
        self.api_url = api_url
        self.results = {}
    
    def send_chat_request(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a chat request and measure response time.
        
        Args:
            message: Message to send
            session_id: Session ID (optional)
            
        Returns:
            Dict with response data and timing
        """
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={"message": message, "session_id": session_id}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response_time": response_time,
                    "session_id": data.get("session_id", session_id),
                    "response": data.get("response", ""),
                    "metrics": data.get("metrics", {})
                }
            else:
                return {
                    "success": False,
                    "response_time": response_time,
                    "error": response.text
                }
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": False,
                "response_time": response_time,
                "error": str(e)
            }
    
    def latency_test(self, num_requests: int = 20) -> Dict[str, Any]:
        """
        Perform latency testing with sequential requests.
        
        Args:
            num_requests: Number of requests to make
            
        Returns:
            Dict of latency test results
        """
        logger.info(f"Starting latency test with {num_requests} sequential requests...")
        
        response_times = []
        success_count = 0
        session_id = None
        
        for i in range(num_requests):
            # Generate test message
            message = f"Latency test message {i+1}: Please provide a brief response."
            
            # Send request
            result = self.send_chat_request(message, session_id)
            
            # Update session ID if not set
            if not session_id and result.get("session_id"):
                session_id = result.get("session_id")
            
            # Record results
            if result.get("success"):
                success_count += 1
                response_times.append(result.get("response_time", 0))
            
            logger.info(f"Request {i+1}: success={result.get('success')}, response_time={result.get('response_time', 0):.4f}s")
            
            # Wait a bit between requests
            time.sleep(0.2)
        
        # Calculate statistics
        if response_times:
            stats = {
                "count": len(response_times),
                "success_rate": success_count / num_requests * 100,
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": np.percentile(response_times, 95),
                "min": min(response_times),
                "max": max(response_times),
            }
        else:
            stats = {
                "count": 0,
                "success_rate": 0,
                "error": "No successful requests"
            }
        
        logger.info(f"Latency test results: {json.dumps(stats, indent=2)}")
        
        # Store results
        self.results["latency_test"] = stats
        
        return stats
    
    def _worker(self, worker_id: int, num_requests: int) -> Dict[str, Any]:
        """
        Worker function for concurrent stress testing.
        
        Args:
            worker_id: Worker ID
            num_requests: Number of requests to make
            
        Returns:
            Dict of worker results
        """
        logger.info(f"Worker {worker_id} starting with {num_requests} requests...")
        
        response_times = []
        success_count = 0
        session_id = None
        
        for i in range(num_requests):
            # Generate test message
            message = f"Stress test from worker {worker_id}, request {i+1}: Please provide a brief response."
            
            # Send request
            result = self.send_chat_request(message, session_id)
            
            # Update session ID if not set
            if not session_id and result.get("session_id"):
                session_id = result.get("session_id")
            
            # Record results
            if result.get("success"):
                success_count += 1
                response_times.append(result.get("response_time", 0))
            
            # Wait a bit between requests (less than in latency test)
            time.sleep(0.1)
        
        # Calculate statistics
        if response_times:
            stats = {
                "count": len(response_times),
                "success_rate": success_count / num_requests * 100,
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "p95": np.percentile(response_times, 95),
                "min": min(response_times),
                "max": max(response_times),
            }
        else:
            stats = {
                "count": 0,
                "success_rate": 0,
                "error": "No successful requests"
            }
        
        logger.info(f"Worker {worker_id} completed: {json.dumps(stats, indent=2)}")
        
        return {
            "worker_id": worker_id,
            "stats": stats,
            "session_id": session_id
        }
    
    def stress_test(self, num_workers: int = 5, requests_per_worker: int = 10) -> Dict[str, Any]:
        """
        Perform stress testing with concurrent requests.
        
        Args:
            num_workers: Number of concurrent workers
            requests_per_worker: Number of requests per worker
            
        Returns:
            Dict of stress test results
        """
        logger.info(f"Starting stress test with {num_workers} workers, {requests_per_worker} requests per worker...")
        
        # Check health before test
        try:
            health_before = requests.get(f"{self.api_url}/health").json()
        except Exception as e:
            health_before = {"error": str(e)}
        
        # Run workers in thread pool
        worker_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit workers
            futures = [executor.submit(self._worker, i, requests_per_worker) for i in range(num_workers)]
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    worker_results.append(result)
                except Exception as e:
                    logger.error(f"Worker error: {e}")
        
        # Check health after test
        try:
            health_after = requests.get(f"{self.api_url}/health").json()
        except Exception as e:
            health_after = {"error": str(e)}
        
        # Aggregate results
        all_response_times = []
        total_success = 0
        total_requests = num_workers * requests_per_worker
        
        for result in worker_results:
            stats = result.get("stats", {})
            success_count = int(stats.get("count", 0))
            total_success += success_count
            
            # Collect response times for aggregate statistics
            if "mean" in stats and "count" in stats and stats["count"] > 0:
                all_response_times.extend([stats.get("mean", 0)] * stats.get("count", 0))
        
        # Calculate aggregate statistics
        if all_response_times:
            aggregate_stats = {
                "total_requests": total_requests,
                "successful_requests": total_success,
                "success_rate": total_success / total_requests * 100,
                "mean": statistics.mean(all_response_times),
                "median": statistics.median(all_response_times),
                "p95": np.percentile(all_response_times, 95),
                "min": min(all_response_times),
                "max": max(all_response_times),
            }
        else:
            aggregate_stats = {
                "total_requests": total_requests,
                "successful_requests": 0,
                "success_rate": 0,
                "error": "No successful requests"
            }
        
        # Prepare results
        results = {
            "aggregate": aggregate_stats,
            "workers": worker_results,
            "health_before": health_before,
            "health_after": health_after
        }
        
        logger.info(f"Stress test aggregate results: {json.dumps(aggregate_stats, indent=2)}")
        
        # Store results
        self.results["stress_test"] = results
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all performance tests.
        
        Returns:
            Dict of all test results
        """
        # Run latency test
        latency_results = self.latency_test()
        
        # Run stress test
        stress_results = self.stress_test()
        
        # Combine results
        all_results = {
            "latency_test": latency_results,
            "stress_test": stress_results,
            "timestamp": time.time(),
            "api_url": self.api_url
        }
        
        # Check if performance meets requirements
        meets_requirements = (
            latency_results.get("median", float("inf")) < 1.0 and  # Median < 1s
            latency_results.get("p95", float("inf")) < 2.0  # P95 < 2s
        )
        
        all_results["meets_requirements"] = meets_requirements
        
        logger.info(f"All tests completed. Meets requirements: {meets_requirements}")
        
        return all_results

# Run tests if executed directly
if __name__ == "__main__":
    tester = StressTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("performance_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n=== Performance Test Summary ===")
    print(f"Latency Test (Median): {results['latency_test'].get('median', 'N/A'):.4f}s")
    print(f"Latency Test (P95): {results['latency_test'].get('p95', 'N/A'):.4f}s")
    print(f"Stress Test Success Rate: {results['stress_test']['aggregate'].get('success_rate', 'N/A'):.2f}%")
    print(f"Meets Requirements: {'YES' if results.get('meets_requirements', False) else 'NO'}")
