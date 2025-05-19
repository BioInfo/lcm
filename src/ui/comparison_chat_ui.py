#!/usr/bin/env python3
"""
Enhanced Chat UI with Model Comparison for Meta LCM Chatbot.
This module provides an improved chat interface with LCM vs Llama comparison features.
"""

import os
import time
import logging
import gradio as gr
import markdown
import requests
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
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

class ComparisonChatUI:
    """
    Enhanced Chat UI with Model Comparison using Gradio.
    Provides a polished interface for comparing LCM and Llama models.
    """
    
    def __init__(self, api_url: str = API_URL):
        """
        Initialize the enhanced chat UI with comparison features.
        
        Args:
            api_url: URL of the API endpoint
        """
        self.api_url = api_url
        self.comparison_api_url = f"{api_url}/comparison"
        self.session_id = None
        self.test_cases = {}
        self.comparison_results = []
        
        # Create Gradio interface
        self.interface = self._create_interface()
    
    def _create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface with comparison features.
        
        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(css=self._get_custom_css(), theme=gr.themes.Soft()) as interface:
            # Header
            with gr.Row():
                gr.Markdown("# Meta LCM Chatbot with Model Comparison", elem_id="title")
            
            with gr.Row():
                gr.Markdown("Compare concept-level reasoning (LCM-7B) vs token-level processing (Llama-7B)", elem_id="subtitle")
            
            # Tabs for different modes
            with gr.Tabs() as tabs:
                # Standard Chat Tab
                with gr.TabItem("Standard Chat", id="chat-tab"):
                    self._create_standard_chat_tab()
                
                # Model Comparison Tab
                with gr.TabItem("Model Comparison", id="comparison-tab"):
                    self._create_comparison_tab()
                
                # Comparison Analytics Tab
                with gr.TabItem("Comparison Analytics", id="analytics-tab"):
                    self._create_analytics_tab()
            
            # Footer
            with gr.Row():
                gr.Markdown("*Response times < 1s median / 2s p95. No PII stored. GPU-accelerated inference.*", elem_id="footer")
            
            # Hidden state for session ID
            session_id = gr.State("")
            
            # Initialize session on load
            interface.load(
                fn=self.initialize_session,
                inputs=[],
                outputs=[session_id]
            )
        
        return interface
    
    def _create_standard_chat_tab(self):
        """Create the standard chat tab."""
        with gr.Row():
            with gr.Column(scale=4):
                # Chat history (conversation stream)
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    elem_id="chatbot",
                    avatar_images=(None, "https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.png"),
                    bubble_full_width=False
                )
                
                # Input bar with send button
                with gr.Row():
                    with gr.Column(scale=8):
                        msg = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here...",
                            show_label=False,
                            elem_id="msg-box",
                            container=False
                        )
                    with gr.Column(scale=1, min_width=70):
                        submit_btn = gr.Button("Send", variant="primary", elem_id="send-btn")
                
                # Action buttons
                with gr.Row():
                    clear_btn = gr.Button("Clear History", variant="secondary", elem_id="clear-btn")
                    regenerate_btn = gr.Button("Regenerate Response", variant="secondary", elem_id="regenerate-btn")
            
            with gr.Column(scale=1):
                # Session info
                with gr.Accordion("Session Info", open=False):
                    session_info = gr.JSON(
                        label="Session Details",
                        elem_id="session-info"
                    )
                
                # Performance metrics
                with gr.Accordion("Performance Metrics", open=False):
                    metrics = gr.JSON(
                        label="Response Metrics",
                        elem_id="metrics"
                    )
                
                # System status
                with gr.Accordion("System Status", open=False):
                    system_status = gr.JSON(
                        label="System Status",
                        elem_id="system-status"
                    )
                    refresh_status_btn = gr.Button("Refresh Status", size="sm")
        
        # Hidden state for last message
        last_message = gr.State("")
        
        # Event handlers
        submit_btn.click(
            fn=self.handle_message,
            inputs=[msg, chatbot, gr.State("")],
            outputs=[msg, chatbot, gr.State(""), metrics]
        )
        
        msg.submit(
            fn=self.handle_message,
            inputs=[msg, chatbot, gr.State("")],
            outputs=[msg, chatbot, gr.State(""), metrics]
        )
        
        clear_btn.click(
            fn=self.handle_clear,
            inputs=[gr.State("")],
            outputs=[chatbot, gr.State(""), metrics, system_status]
        )
        
        regenerate_btn.click(
            fn=self.handle_regenerate,
            inputs=[last_message, chatbot, gr.State("")],
            outputs=[chatbot, gr.State(""), metrics]
        )
        
        refresh_status_btn.click(
            fn=self.get_system_status,
            inputs=[],
            outputs=[system_status]
        )
    
    def _create_comparison_tab(self):
        """Create the model comparison tab."""
        with gr.Row():
            with gr.Column(scale=1):
                # Comparison options
                with gr.Accordion("Comparison Options", open=True):
                    use_test_case = gr.Checkbox(
                        label="Use Pre-defined Test Case",
                        value=False,
                        elem_id="use-test-case"
                    )
                    
                    test_category = gr.Dropdown(
                        label="Test Case Category",
                        choices=["general", "reasoning", "creativity", "cross_lingual", "multimodal"],
                        value="general",
                        interactive=True,
                        elem_id="test-category"
                    )
                    
                    prompt_input = gr.Textbox(
                        label="Custom Prompt",
                        placeholder="Enter your prompt for comparison...",
                        lines=3,
                        elem_id="prompt-input"
                    )
                    
                    with gr.Row():
                        image_input = gr.Image(
                            label="Image Input (Optional)",
                            type="filepath",
                            elem_id="image-input"
                        )
                    
                    compare_btn = gr.Button(
                        "Compare Models",
                        variant="primary",
                        elem_id="compare-btn"
                    )
            
            with gr.Column(scale=2):
                # Comparison results
                with gr.Accordion("Prompt", open=True):
                    prompt_display = gr.Textbox(
                        label="Prompt",
                        lines=2,
                        elem_id="prompt-display",
                        interactive=False
                    )
                
                with gr.Row():
                    with gr.Column():
                        lcm_response = gr.Textbox(
                            label="LCM-7B Response (Concept-Level)",
                            lines=8,
                            elem_id="lcm-response",
                            interactive=False
                        )
                    
                    with gr.Column():
                        llama_response = gr.Textbox(
                            label="Llama-7B Response (Token-Level)",
                            lines=8,
                            elem_id="llama-response",
                            interactive=False
                        )
                
                with gr.Accordion("Comparison Metrics", open=True):
                    metrics_display = gr.JSON(
                        label="Detailed Metrics",
                        elem_id="metrics-display"
                    )
                
                with gr.Accordion("Visualization", open=True):
                    metrics_plot = gr.Plot(
                        label="Metrics Comparison",
                        elem_id="metrics-plot"
                    )
        
        # Event handlers
        compare_btn.click(
            fn=self.handle_comparison,
            inputs=[prompt_input, use_test_case, test_category, image_input],
            outputs=[prompt_display, lcm_response, llama_response, metrics_display, metrics_plot]
        )
        
        use_test_case.change(
            fn=self.toggle_test_case,
            inputs=[use_test_case],
            outputs=[prompt_input, test_category]
        )
    
    def _create_analytics_tab(self):
        """Create the comparison analytics tab."""
        with gr.Row():
            with gr.Column():
                refresh_analytics_btn = gr.Button(
                    "Refresh Analytics",
                    variant="primary",
                    elem_id="refresh-analytics-btn"
                )
                
                with gr.Accordion("Overall Performance", open=True):
                    summary_stats = gr.JSON(
                        label="Summary Statistics",
                        elem_id="summary-stats"
                    )
                    
                    summary_plot = gr.Plot(
                        label="Win Rate Comparison",
                        elem_id="summary-plot"
                    )
                
                with gr.Accordion("Detailed Metrics", open=True):
                    with gr.Row():
                        with gr.Column():
                            speed_plot = gr.Plot(
                                label="Speed Comparison",
                                elem_id="speed-plot"
                            )
                        
                        with gr.Column():
                            reasoning_plot = gr.Plot(
                                label="Reasoning Comparison",
                                elem_id="reasoning-plot"
                            )
                    
                    with gr.Row():
                        with gr.Column():
                            creativity_plot = gr.Plot(
                                label="Creativity Comparison",
                                elem_id="creativity-plot"
                            )
                        
                        with gr.Column():
                            factuality_plot = gr.Plot(
                                label="Factuality Comparison",
                                elem_id="factuality-plot"
                            )
                
                with gr.Accordion("Previous Comparisons", open=False):
                    comparison_history = gr.Dataframe(
                        headers=["Prompt", "LCM Win", "Llama Win", "Details"],
                        elem_id="comparison-history"
                    )
        
        # Event handlers
        refresh_analytics_btn.click(
            fn=self.refresh_analytics,
            inputs=[],
            outputs=[summary_stats, summary_plot, speed_plot, reasoning_plot, creativity_plot, factuality_plot, comparison_history]
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
        #chatbot {
            height: 500px;
            overflow-y: auto;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        #msg-box {
            border-radius: 20px;
            padding: 10px 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        #send-btn, #compare-btn, #refresh-analytics-btn {
            border-radius: 20px;
            min-height: 40px;
        }
        #clear-btn, #regenerate-btn {
            border-radius: 8px;
            margin-top: 10px;
        }
        #footer {
            text-align: center;
            color: #777;
            font-size: 0.8em;
            margin-top: 20px;
        }
        .message {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 10px;
        }
        .user-message {
            background-color: #e3f2fd;
            text-align: right;
        }
        .bot-message {
            background-color: #f5f5f5;
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
            color: #c62828;
        }
        code {
            background-color: #f8f8f8;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        """
    
    def initialize_session(self) -> str:
        """
        Initialize a new session.
        
        Returns:
            Session ID
        """
        try:
            # Create a new session via API
            response = requests.post(f"{self.api_url}/chat", json={"message": ""})
            data = response.json()
            
            session_id = data.get("session_id", "")
            self.session_id = session_id
            
            # Load test cases
            self._load_test_cases()
            
            logger.info(f"Initialized session: {session_id}")
            
            return session_id
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            r
(Content truncated due to size limit. Use line ranges to read in chunks)