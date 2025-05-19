#!/usr/bin/env python3
"""
Comparison API Endpoints for Meta LCM Chatbot.
This module provides API endpoints for comparing LCM and Llama models.
"""

import os
import time
import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import numpy as np

# Import model inference modules
from app.models.inference import LCMInference
from app.models.llama_inference import LlamaInference
from app.models.comparison import ModelComparison

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/comparison", tags=["comparison"])

# Initialize models (lazy loading)
lcm_model = None
llama_model = None
comparison_module = None

# Define request/response models
class ComparisonRequest(BaseModel):
    """Comparison request model."""
    prompt: str = Field(..., description="User prompt for comparison")
    session_id: Optional[str] = Field(None, description="Session ID (optional)")
    test_case_category: Optional[str] = Field(None, description="Test case category (optional)")
    use_test_case: bool = Field(False, description="Whether to use a pre-defined test case")

class ComparisonResponse(BaseModel):
    """Comparison response model."""
    prompt: str = Field(..., description="User prompt or test case")
    lcm_response: str = Field(..., description="Response from LCM model")
    llama_response: str = Field(..., description="Response from Llama model")
    comparison_metrics: Dict[str, Any] = Field(..., description="Comparison metrics")
    session_id: str = Field(..., description="Session ID")
    processing_time: float = Field(..., description="Total processing time")

class TestCaseListResponse(BaseModel):
    """Test case list response model."""
    categories: List[str] = Field(..., description="Available test case categories")
    test_cases: Dict[str, List[Dict[str, Any]]] = Field(..., description="Test cases by category")

class ComparisonSummaryResponse(BaseModel):
    """Comparison summary response model."""
    total_comparisons: int = Field(..., description="Total number of comparisons")
    lcm_wins: int = Field(..., description="Number of metrics where LCM won")
    llama_wins: int = Field(..., description="Number of metrics where Llama won")
    tie: int = Field(..., description="Number of metrics where there was a tie")
    lcm_win_percentage: float = Field(..., description="Percentage of metrics where LCM won")
    llama_win_percentage: float = Field(..., description="Percentage of metrics where Llama won")

def get_lcm_model():
    """Get or initialize LCM model."""
    global lcm_model
    if lcm_model is None:
        lcm_model = LCMInference()
    return lcm_model

def get_llama_model():
    """Get or initialize Llama model."""
    global llama_model
    if llama_model is None:
        llama_model = LlamaInference()
    return llama_model

def get_comparison_module():
    """Get or initialize comparison module."""
    global comparison_module
    if comparison_module is None:
        comparison_module = ModelComparison()
    return comparison_module

@router.post("/compare", response_model=ComparisonResponse)
async def compare_models(request: ComparisonRequest, background_tasks: BackgroundTasks):
    """
    Compare LCM and Llama models on the same prompt.
    
    Args:
        request: Comparison request
        background_tasks: Background tasks
        
    Returns:
        ComparisonResponse with both model responses and comparison metrics
    """
    try:
        start_time = time.time()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get models
        lcm = get_lcm_model()
        llama = get_llama_model()
        comparison = get_comparison_module()
        
        # Get prompt (either from request or test case)
        prompt = request.prompt
        image_path = None
        
        if request.use_test_case:
            # Get test case
            test_case = comparison.get_test_case(request.test_case_category)
            prompt = test_case["prompt"]
            
            # Check if test case requires an image
            if test_case.get("requires_image", False):
                # In a real implementation, this would use a pre-defined image
                # For MVP, we'll just note that an image would be used
                image_path = "/path/to/test/image.jpg"  # Placeholder
        
        # Generate responses from both models
        lcm_response, lcm_time = "", 0
        llama_response, llama_time = "", 0
        
        # For MVP, we'll use mock responses to avoid loading both models
        # In a real implementation, these would be actual model outputs
        if hasattr(lcm, 'generate_from_concepts'):
            # This would be replaced with actual concept vector generation
            mock_concepts = [np.random.randn(768) for _ in range(3)]
            next_concept, lcm_time = lcm.generate_from_concepts(mock_concepts)
            lcm_response = f"This is a simulated response from the LCM-7B model using concept-level reasoning. The response would be tailored to your prompt: '{prompt}'"
        else:
            lcm_response = f"LCM model response placeholder for: {prompt}"
            lcm_time = 0.8
        
        llama_response, llama_time = llama.generate_response(prompt)
        
        # Prepare metrics
        lcm_metrics = {"processing_time": lcm_time}
        llama_metrics = {"processing_time": llama_time}
        
        # Compare responses
        comparison_metrics = comparison.compare_responses(
            prompt, lcm_response, llama_response, 
            lcm_metrics, llama_metrics, image_path
        )
        
        # Calculate total processing time
        processing_time = time.time() - start_time
        
        # Log comparison
        logger.info(f"Comparison completed for prompt: {prompt[:50]}...")
        
        return ComparisonResponse(
            prompt=prompt,
            lcm_response=lcm_response,
            llama_response=llama_response,
            comparison_metrics=comparison_metrics,
            session_id=session_id,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error in model comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare-with-image", response_model=ComparisonResponse)
async def compare_models_with_image(
    prompt: str = Form(...),
    session_id: Optional[str] = Form(None),
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks
):
    """
    Compare LCM and Llama models on a prompt with an image.
    
    Args:
        prompt: User prompt
        session_id: Session ID (optional)
        image: Uploaded image file
        background_tasks: Background tasks
        
    Returns:
        ComparisonResponse with both model responses and comparison metrics
    """
    try:
        start_time = time.time()
        
        # Generate session ID if not provided
        session_id = session_id or str(uuid.uuid4())
        
        # Get models
        lcm = get_lcm_model()
        llama = get_llama_model()
        comparison = get_comparison_module()
        
        # Save uploaded image to temporary file
        image_path = f"/tmp/{uuid.uuid4()}_{image.filename}"
        with open(image_path, "wb") as f:
            f.write(await image.read())
        
        # Generate responses from both models
        # For MVP, we'll use mock responses for multimodal input
        lcm_response = f"This is a simulated response from the LCM-7B model analyzing the image and responding to: '{prompt}'"
        lcm_time = 0.9
        
        llama_response = f"This is a simulated response from the Llama-7B model. Note that standard Llama models don't have multimodal capabilities, so this would require a specialized version or extension."
        llama_time = 1.2
        
        # Prepare metrics
        lcm_metrics = {"processing_time": lcm_time}
        llama_metrics = {"processing_time": llama_time}
        
        # Compare responses
        comparison_metrics = comparison.compare_responses(
            prompt, lcm_response, llama_response, 
            lcm_metrics, llama_metrics, image_path
        )
        
        # Calculate total processing time
        processing_time = time.time() - start_time
        
        # Log comparison
        logger.info(f"Multimodal comparison completed for prompt: {prompt[:50]}...")
        
        # Clean up temporary file in background
        background_tasks.add_task(os.remove, image_path)
        
        return ComparisonResponse(
            prompt=prompt,
            lcm_response=lcm_response,
            llama_response=llama_response,
            comparison_metrics=comparison_metrics,
            session_id=session_id,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error in multimodal model comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-cases", response_model=TestCaseListResponse)
async def get_test_cases():
    """
    Get available test cases for comparison.
    
    Returns:
        TestCaseListResponse with test case categories and details
    """
    try:
        # Get comparison module
        comparison = get_comparison_module()
        
        # Get test cases
        test_cases = comparison.get_all_test_cases()
        
        return TestCaseListResponse(
            categories=list(test_cases.keys()),
            test_cases=test_cases
        )
    except Exception as e:
        logger.error(f"Error getting test cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", response_model=ComparisonSummaryResponse)
async def get_comparison_summary():
    """
    Get summary of all comparisons.
    
    Returns:
        ComparisonSummaryResponse with comparison statistics
    """
    try:
        # Get comparison module
        comparison = get_comparison_module()
        
        # Get summary
        summary = comparison.get_comparison_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        return ComparisonSummaryResponse(**summary)
    except Exception as e:
        logger.error(f"Error getting comparison summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
