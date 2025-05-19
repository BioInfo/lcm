#!/usr/bin/env python3
"""
User-driven Head-to-Head Comparison UI for Meta LCM Chatbot.
This module provides an interactive interface for comparing LCM and Llama models.
"""

import os
import time
import logging
import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import seaborn as sns
from PIL import Image
import io
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoint
API_URL = os.environ.get("API_URL", "http://localhost:8000/api")
COMPARISON_API_URL = f"{API_URL}/comparison"

class HeadToHeadUI:
    """
    Interactive Head-to-Head Comparison UI using Gradio.
    Provides a visually engaging interface for comparing LCM and Llama models.
    """
    
    def __init__(self, api_url: str = API_URL):
        """
        Initialize the head-to-head comparison UI.
        
        Args:
            api_url: URL of the API endpoint
        """
        self.api_url = api_url
        self.comparison_api_url = f"{api_url}/comparison"
        self.session_id = None
        self.test_cases = {}
        self.comparison_results = []
        self.categories = []
        
        # Create Gradio interface
        self.interface = self._create_interface()
    
    def _create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface with interactive comparison features.
        
        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(css=self._get_custom_css(), theme=gr.themes.Soft()) as interface:
            # Header
            with gr.Row():
                gr.Markdown("# LCM vs Llama: Head-to-Head Comparison", elem_id="title")
            
            with gr.Row():
                gr.Markdown("Compare concept-level reasoning (LCM-7B) vs token-level processing (Llama-7B)", elem_id="subtitle")
            
            # Main content
            with gr.Tabs() as tabs:
                # Interactive Comparison Tab
                with gr.TabItem("Interactive Comparison", id="interactive-tab"):
                    self._create_interactive_tab()
                
                # Pre-defined Test Cases Tab
                with gr.TabItem("Pre-defined Test Cases", id="test-cases-tab"):
                    self._create_test_cases_tab()
                
                # Results Dashboard Tab
                with gr.TabItem("Results Dashboard", id="dashboard-tab"):
                    self._create_dashboard_tab()
            
            # Footer
            with gr.Row():
                gr.Markdown("*Comparing LCM-7B (concept-level reasoning) vs Llama-7B (token-level processing)*", elem_id="footer")
            
            # Initialize on load
            interface.load(
                fn=self._initialize,
                inputs=[],
                outputs=[
                    self.test_category_dropdown,
                    self.test_case_dropdown,
                    self.dashboard_summary,
                    self.win_rate_chart,
                    self.metric_comparison_chart
                ]
            )
        
        return interface
    
    def _create_interactive_tab(self):
        """Create the interactive comparison tab."""
        with gr.Row():
            # Input column
            with gr.Column(scale=1):
                # Prompt input
                prompt_input = gr.Textbox(
                    label="Enter your prompt for comparison",
                    placeholder="Type a prompt to compare both models...",
                    lines=3,
                    elem_id="prompt-input"
                )
                
                # Image input (optional)
                with gr.Row():
                    image_input = gr.Image(
                        label="Add image (optional)",
                        type="filepath",
                        elem_id="image-input"
                    )
                
                # Compare button
                compare_btn = gr.Button(
                    "Compare Models",
                    variant="primary",
                    elem_id="compare-btn"
                )
                
                # Advanced options
                with gr.Accordion("Advanced Options", open=False):
                    with gr.Row():
                        with gr.Column(scale=1):
                            temperature_slider = gr.Slider(
                                label="Temperature",
                                minimum=0.1,
                                maximum=1.0,
                                value=0.7,
                                step=0.1,
                                elem_id="temperature-slider"
                            )
                        
                        with gr.Column(scale=1):
                            max_length_slider = gr.Slider(
                                label="Max Response Length",
                                minimum=50,
                                maximum=500,
                                value=200,
                                step=50,
                                elem_id="max-length-slider"
                            )
            
            # Results column
            with gr.Column(scale=2):
                # Comparison results
                with gr.Row():
                    with gr.Column():
                        lcm_response = gr.Textbox(
                            label="LCM-7B Response (Concept-Level)",
                            lines=8,
                            elem_id="lcm-response"
                        )
                    
                    with gr.Column():
                        llama_response = gr.Textbox(
                            label="Llama-7B Response (Token-Level)",
                            lines=8,
                            elem_id="llama-response"
                        )
                
                # Performance metrics
                with gr.Row():
                    with gr.Column():
                        speed_metrics = gr.JSON(
                            label="Speed Comparison",
                            elem_id="speed-metrics"
                        )
                    
                    with gr.Column():
                        reasoning_metrics = gr.JSON(
                            label="Reasoning Comparison",
                            elem_id="reasoning-metrics"
                        )
                
                # Visualization
                metrics_chart = gr.Plot(
                    label="Metrics Comparison",
                    elem_id="metrics-chart"
                )
                
                # Detailed metrics accordion
                with gr.Accordion("All Comparison Metrics", open=False):
                    all_metrics = gr.JSON(
                        label="Detailed Metrics",
                        elem_id="all-metrics"
                    )
        
        # Event handlers
        compare_btn.click(
            fn=self._handle_comparison,
            inputs=[prompt_input, image_input, temperature_slider, max_length_slider],
            outputs=[
                lcm_response,
                llama_response,
                speed_metrics,
                reasoning_metrics,
                metrics_chart,
                all_metrics
            ]
        )
    
    def _create_test_cases_tab(self):
        """Create the pre-defined test cases tab."""
        with gr.Row():
            # Test case selection column
            with gr.Column(scale=1):
                # Category dropdown
                self.test_category_dropdown = gr.Dropdown(
                    label="Test Case Category",
                    choices=[],
                    elem_id="test-category-dropdown"
                )
                
                # Test case dropdown
                self.test_case_dropdown = gr.Dropdown(
                    label="Select Test Case",
                    choices=[],
                    elem_id="test-case-dropdown"
                )
                
                # Test case description
                test_case_description = gr.Textbox(
                    label="Test Case Description",
                    elem_id="test-case-description",
                    interactive=False
                )
                
                # Run test case button
                run_test_case_btn = gr.Button(
                    "Run Test Case",
                    variant="primary",
                    elem_id="run-test-case-btn"
                )
                
                # Batch run button
                with gr.Accordion("Batch Testing", open=False):
                    batch_category = gr.Dropdown(
                        label="Category for Batch Testing",
                        choices=[],
                        elem_id="batch-category"
                    )
                    
                    batch_run_btn = gr.Button(
                        "Run All Tests in Category",
                        variant="secondary",
                        elem_id="batch-run-btn"
                    )
                    
                    batch_progress = gr.Textbox(
                        label="Batch Progress",
                        elem_id="batch-progress",
                        interactive=False
                    )
            
            # Results column
            with gr.Column(scale=2):
                # Test case prompt
                test_prompt = gr.Textbox(
                    label="Test Prompt",
                    elem_id="test-prompt",
                    interactive=False
                )
                
                # Test case image (if applicable)
                test_image = gr.Image(
                    label="Test Image (if applicable)",
                    elem_id="test-image",
                    type="filepath",
                    visible=False
                )
                
                # Comparison results
                with gr.Row():
                    with gr.Column():
                        test_lcm_response = gr.Textbox(
                            label="LCM-7B Response",
                            lines=8,
                            elem_id="test-lcm-response"
                        )
                    
                    with gr.Column():
                        test_llama_response = gr.Textbox(
                            label="Llama-7B Response",
                            lines=8,
                            elem_id="test-llama-response"
                        )
                
                # Visualization
                test_metrics_chart = gr.Plot(
                    label="Test Case Metrics",
                    elem_id="test-metrics-chart"
                )
                
                # Detailed metrics accordion
                with gr.Accordion("Test Case Metrics", open=False):
                    test_all_metrics = gr.JSON(
                        label="Detailed Metrics",
                        elem_id="test-all-metrics"
                    )
        
        # Event handlers
        self.test_category_dropdown.change(
            fn=self._update_test_cases,
            inputs=[self.test_category_dropdown],
            outputs=[self.test_case_dropdown]
        )
        
        self.test_case_dropdown.change(
            fn=self._update_test_description,
            inputs=[self.test_category_dropdown, self.test_case_dropdown],
            outputs=[test_case_description]
        )
        
        run_test_case_btn.click(
            fn=self._run_test_case,
            inputs=[self.test_category_dropdown, self.test_case_dropdown],
            outputs=[
                test_prompt,
                test_image,
                test_lcm_response,
                test_llama_response,
                test_metrics_chart,
                test_all_metrics
            ]
        )
        
        batch_run_btn.click(
            fn=self._run_batch_tests,
            inputs=[batch_category],
            outputs=[batch_progress, self.dashboard_summary, self.win_rate_chart, self.metric_comparison_chart]
        )
    
    def _create_dashboard_tab(self):
        """Create the results dashboard tab."""
        with gr.Row():
            # Summary column
            with gr.Column(scale=1):
                # Summary statistics
                self.dashboard_summary = gr.JSON(
                    label="Summary Statistics",
                    elem_id="dashboard-summary"
                )
                
                # Win rate chart
                self.win_rate_chart = gr.Plot(
                    label="Win Rate Comparison",
                    elem_id="win-rate-chart"
                )
                
                # Refresh button
                refresh_btn = gr.Button(
                    "Refresh Dashboard",
                    variant="primary",
                    elem_id="refresh-btn"
                )
            
            # Detailed metrics column
            with gr.Column(scale=2):
                # Metric comparison chart
                self.metric_comparison_chart = gr.Plot(
                    label="Metric Comparison",
                    elem_id="metric-comparison-chart"
                )
                
                # Comparison history
                with gr.Accordion("Comparison History", open=True):
                    comparison_history = gr.Dataframe(
                        headers=["Prompt", "Category", "LCM Wins", "Llama Wins", "Timestamp"],
                        elem_id="comparison-history"
                    )
                
                # Export results button
                export_btn = gr.Button(
                    "Export Results",
                    variant="secondary",
                    elem_id="export-btn"
                )
                
                export_path = gr.Textbox(
                    label="Export Path",
                    elem_id="export-path",
                    interactive=False
                )
        
        # Event handlers
        refresh_btn.click(
            fn=self._refresh_dashboard,
            inputs=[],
            outputs=[self.dashboard_summary, self.win_rate_chart, self.metric_comparison_chart, comparison_history]
        )
        
        export_btn.click(
            fn=self._export_results,
            inputs=[],
            outputs=[export_path]
        )
    
    def _get_custom_css(self) -> str:
        """
        Get custom CSS for the interface with enhanced styling.
        
        Returns:
            CSS string
        """
        return """
        #title {
            text-align: center;
            color: #1565c0;
            margin-bottom: 0;
        }
        #subtitle {
            text-align: center;
            color: #555;
            margin-top: 0;
            margin-bottom: 20px;
        }
        #compare-btn, #run-test-case-btn, #refresh-btn {
            border-radius: 20px;
            min-height: 40px;
            background-color: #1976d2;
        }
        #batch-run-btn, #export-btn {
            border-radius: 20px;
            min-height: 40px;
            background-color: #5c6bc0;
        }
        #footer {
            text-align: center;
            color: #777;
            font-size: 0.8em;
            margin-top: 20px;
        }
        .lcm-highlight {
            background-color: #e3f2fd;
            padding: 2px 4px;
            border-radius: 3px;
        }
        .llama-highlight {
            background-color: #fff3e0;
            padding: 2px 4px;
            border-radius: 3px;
        }
        .comparison-win {
            font-weight: bold;
            color: #2e7d32;
        }
        .comparison-loss {
    
(Content truncated due to size limit. Use line ranges to read in chunks)