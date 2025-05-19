#!/usr/bin/env python3
"""
Metrics and Logging for Meta LCM Chatbot.
This module handles performance metrics collection and logging.
"""

import os
import time
import logging
import json
import psutil
import torch
import numpy as np
from typing import Dict, Any, Optional, List
from pathlib import Path
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(Path(__file__).parent.parent.parent, "chatbot.log"))
    ]
)
logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Collects and exposes performance metrics for the chatbot.
    """
    
    def __init__(self, enable_prometheus: bool = False, prometheus_port: int = 8001):
        """
        Initialize the metrics collector.
        
        Args:
            enable_prometheus: Whether to enable Prometheus metrics
            prometheus_port: Port for Prometheus metrics server
        """
        self.start_time = time.time()
        self.enable_prometheus = enable_prometheus
        self.prometheus_port = prometheus_port
        
        # Performance metrics
        self.request_count = 0
        self.response_times = []
        self.encode_times = []
        self.inference_times = []
        self.decode_times = []
        
        # Initialize Prometheus metrics if enabled
        if enable_prometheus:
            self._init_prometheus()
    
    def _init_prometheus(self):
        """Initialize Prometheus metrics."""
        # Start Prometheus server
        start_http_server(self.prometheus_port)
        
        # Define Prometheus metrics
        self.prom_requests = Counter('lcm_requests_total', 'Total number of requests')
        self.prom_response_time = Histogram('lcm_response_time_seconds', 'Response time in seconds', buckets=[0.1, 0.5, 1.0, 2.0, 5.0])
        self.prom_encode_time = Histogram('lcm_encode_time_seconds', 'Encoding time in seconds', buckets=[0.05, 0.1, 0.2, 0.5, 1.0])
        self.prom_inference_time = Histogram('lcm_inference_time_seconds', 'Inference time in seconds', buckets=[0.05, 0.1, 0.2, 0.5, 1.0])
        self.prom_decode_time = Histogram('lcm_decode_time_seconds', 'Decoding time in seconds', buckets=[0.05, 0.1, 0.2, 0.5, 1.0])
        self.prom_gpu_util = Gauge('lcm_gpu_utilization_percent', 'GPU utilization percentage')
        self.prom_gpu_memory = Gauge('lcm_gpu_memory_used_mb', 'GPU memory used in MB')
        self.prom_cpu_util = Gauge('lcm_cpu_utilization_percent', 'CPU utilization percentage')
        self.prom_memory_util = Gauge('lcm_memory_utilization_percent', 'Memory utilization percentage')
        
        logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
    
    def record_request(self, 
                      response_time: float,
                      encode_time: Optional[float] = None,
                      inference_time: Optional[float] = None,
                      decode_time: Optional[float] = None):
        """
        Record metrics for a request.
        
        Args:
            response_time: Total response time in seconds
            encode_time: Time spent encoding in seconds
            inference_time: Time spent on inference in seconds
            decode_time: Time spent decoding in seconds
        """
        self.request_count += 1
        self.response_times.append(response_time)
        
        if encode_time is not None:
            self.encode_times.append(encode_time)
        
        if inference_time is not None:
            self.inference_times.append(inference_time)
        
        if decode_time is not None:
            self.decode_times.append(decode_time)
        
        # Log metrics
        logger.info(f"Request {self.request_count}: response_time={response_time:.4f}s, "
                   f"encode_time={encode_time:.4f}s if encode_time else 'N/A'}, "
                   f"inference_time={inference_time:.4f}s if inference_time else 'N/A'}, "
                   f"decode_time={decode_time:.4f}s if decode_time else 'N/A'}")
        
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_requests.inc()
            self.prom_response_time.observe(response_time)
            
            if encode_time is not None:
                self.prom_encode_time.observe(encode_time)
            
            if inference_time is not None:
                self.prom_inference_time.observe(inference_time)
            
            if decode_time is not None:
                self.prom_decode_time.observe(decode_time)
    
    def record_system_metrics(self):
        """Record system metrics (CPU, memory, GPU)."""
        metrics = self.get_system_metrics()
        
        # Log metrics
        logger.info(f"System metrics: {json.dumps(metrics)}")
        
        # Update Prometheus metrics if enabled
        if self.enable_prometheus:
            self.prom_cpu_util.set(metrics['cpu_percent'])
            self.prom_memory_util.set(metrics['memory_percent'])
            
            if 'gpu_utilization' in metrics:
                self.prom_gpu_util.set(metrics['gpu_utilization'])
            
            if 'gpu_memory_allocated_mb' in metrics:
                self.prom_gpu_memory.set(metrics['gpu_memory_allocated_mb'])
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system metrics (CPU, memory, GPU).
        
        Returns:
            Dict of system metrics
        """
        metrics = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
        }
        
        # Add GPU metrics if available
        if torch.cuda.is_available():
            metrics.update({
                'gpu_name': torch.cuda.get_device_name(0),
                'gpu_memory_allocated_mb': torch.cuda.memory_allocated() / (1024 * 1024),
                'gpu_memory_reserved_mb': torch.cuda.memory_reserved() / (1024 * 1024),
                'gpu_utilization': torch.cuda.utilization(0),
            })
        
        return metrics
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Dict of performance statistics
        """
        stats = {
            'uptime_seconds': time.time() - self.start_time,
            'request_count': self.request_count,
        }
        
        # Add response time stats if available
        if self.response_times:
            stats.update({
                'response_time': {
                    'mean': np.mean(self.response_times),
                    'median': np.median(self.response_times),
                    'p95': np.percentile(self.response_times, 95),
                    'min': np.min(self.response_times),
                    'max': np.max(self.response_times),
                }
            })
        
        # Add encode time stats if available
        if self.encode_times:
            stats.update({
                'encode_time': {
                    'mean': np.mean(self.encode_times),
                    'median': np.median(self.encode_times),
                    'p95': np.percentile(self.encode_times, 95),
                }
            })
        
        # Add inference time stats if available
        if self.inference_times:
            stats.update({
                'inference_time': {
                    'mean': np.mean(self.inference_times),
                    'median': np.median(self.inference_times),
                    'p95': np.percentile(self.inference_times, 95),
                }
            })
        
        # Add decode time stats if available
        if self.decode_times:
            stats.update({
                'decode_time': {
                    'mean': np.mean(self.decode_times),
                    'median': np.median(self.decode_times),
                    'p95': np.percentile(self.decode_times, 95),
                }
            })
        
        # Add system metrics
        stats.update({
            'system': self.get_system_metrics()
        })
        
        return stats

# Global metrics collector instance
metrics_collector = MetricsCollector()

# Simple test function
def test_metrics():
    """Test the metrics collector."""
    # Record some test metrics
    for _ in range(5):
        # Simulate a request
        response_time = np.random.uniform(0.5, 1.5)
        encode_time = response_time * 0.3
        inference_time = response_time * 0.6
        decode_time = response_time * 0.1
        
        metrics_collector.record_request(
            response_time=response_time,
            encode_time=encode_time,
            inference_time=inference_time,
            decode_time=decode_time
        )
        
        # Simulate system metrics collection
        metrics_collector.record_system_metrics()
        
        # Wait a bit
        time.sleep(0.1)
    
    # Get performance stats
    stats = metrics_collector.get_performance_stats()
    print(json.dumps(stats, indent=2))
    
    return stats

if __name__ == "__main__":
    # Run test if executed directly
    test_metrics()
