#!/usr/bin/env python3
"""
Admin Health Endpoint for Meta LCM Chatbot.
This module provides the health check endpoint for the chatbot.
"""

import os
import time
import logging
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import psutil
import torch
import numpy as np

# Import metrics collector
from app.utils.metrics import metrics_collector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns system status, model status, and performance metrics.
    """
    try:
        # Get system metrics
        system_metrics = metrics_collector.get_system_metrics()
        
        # Get performance stats
        performance_stats = metrics_collector.get_performance_stats()
        
        # Check if GPU is available
        gpu_available = torch.cuda.is_available()
        gpu_utilization = system_metrics.get("gpu_utilization") if gpu_available else None
        
        # Check model status (mock for MVP)
        model_loaded = True  # In a real implementation, this would check if the model is loaded
        
        # Prepare response
        response = {
            "status": "ok",
            "timestamp": time.time(),
            "uptime_seconds": performance_stats.get("uptime_seconds", 0),
            "model": {
                "loaded": model_loaded,
                "name": "LCM-7B",
                "version": "1.0.0",
            },
            "hardware": {
                "gpu_available": gpu_available,
                "gpu_name": system_metrics.get("gpu_name") if gpu_available else None,
                "gpu_utilization_percent": gpu_utilization,
                "gpu_memory_allocated_mb": system_metrics.get("gpu_memory_allocated_mb") if gpu_available else None,
                "gpu_memory_reserved_mb": system_metrics.get("gpu_memory_reserved_mb") if gpu_available else None,
            },
            "system": {
                "cpu_percent": system_metrics.get("cpu_percent"),
                "memory_percent": system_metrics.get("memory_percent"),
                "memory_available_mb": system_metrics.get("memory_available_mb"),
            },
            "performance": {
                "request_count": performance_stats.get("request_count", 0),
                "response_time": performance_stats.get("response_time", {}),
                "encode_time": performance_stats.get("encode_time", {}),
                "inference_time": performance_stats.get("inference_time", {}),
                "decode_time": performance_stats.get("decode_time", {}),
            }
        }
        
        # Log health check
        logger.info(f"Health check: {json.dumps(response, default=str)}")
        
        return response
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    """
    Metrics endpoint.
    Returns detailed performance metrics.
    """
    try:
        # Get performance stats
        performance_stats = metrics_collector.get_performance_stats()
        
        # Log metrics request
        logger.info(f"Metrics request: {json.dumps(performance_stats, default=str)}")
        
        return performance_stats
    except Exception as e:
        logger.error(f"Error in metrics endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
