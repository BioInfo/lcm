#!/usr/bin/env python3
"""
Enhanced Chat UI for Meta LCM Chatbot.
This module provides an improved chat interface with better UX and Clear History functionality.
"""

import os
import time
import logging
import gradio as gr
import markdown
import requests
import json
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoint
API_URL = os.environ.get("API_URL", "http://localhost:8000/api")

class ChatUI:
    """
    Enhanced Chat UI using Gradio.
    Provides a polished two-pane layout with Markdown rendering and Clear History functionality.
    """
    
    def __init__(self, api_url: str = API_URL):
        """
        Initialize the chat UI.
        
        Args:
            api_url: URL of the API endpoint
        """
        self.api_url = api_url
        self.session_id = None
        
        # Create Gradio interface
        self.interface = self._create_interface()
    
    def _create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface with enhanced UX.
        
        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(css=self._get_custom_css(), theme=gr.themes.Soft()) as interface:
            with gr.Row():
                gr.Markdown("# Meta LCM Chatbot", elem_id="title")
            
            with gr.Row():
                gr.Markdown("A lightweight, concept-aware chatbot using Meta's Large Concept Model (LCM-7B)", elem_id="subtitle")
            
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
            
            # Footer
            with gr.Row():
                gr.Markdown("*Response times < 1s median / 2s p95. No PII stored. GPU-accelerated inference.*", elem_id="footer")
            
            # Hidden state for session ID and last message
            session_id = gr.State("")
            last_message = gr.State("")
            
            # Event handlers
            submit_btn.click(
                fn=self.handle_message,
                inputs=[msg, chatbot, session_id],
                outputs=[msg, chatbot, session_id, metrics]
            )
            
            msg.submit(
                fn=self.handle_message,
                inputs=[msg, chatbot, session_id],
                outputs=[msg, chatbot, session_id, metrics]
            )
            
            clear_btn.click(
                fn=self.handle_clear,
                inputs=[session_id],
                outputs=[chatbot, session_id, metrics, system_status]
            )
            
            regenerate_btn.click(
                fn=self.handle_regenerate,
                inputs=[last_message, chatbot, session_id],
                outputs=[chatbot, session_id, metrics]
            )
            
            refresh_status_btn.click(
                fn=self.get_system_status,
                inputs=[],
                outputs=[system_status]
            )
            
            # Initialize session on load
            interface.load(
                fn=self.initialize_session,
                inputs=[],
                outputs=[session_id, session_info, system_status]
            )
        
        return interface
    
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
        #send-btn {
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
    
    def initialize_session(self) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Initialize a new session with enhanced error handling.
        
        Returns:
            Tuple of (session_id, session_info, system_status)
        """
        try:
            # Create a new session via API
            response = requests.post(f"{self.api_url}/chat", json={"message": ""})
            data = response.json()
            
            session_id = data.get("session_id", "")
            
            # Get session info
            session_info = {
                "session_id": session_id,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active",
                "max_concepts": 128
            }
            
            # Get system status
            system_status = self.get_system_status()
            
            logger.info(f"Initialized session: {session_id}")
            
            return session_id, session_info, system_status
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return "", {"error": str(e)}, {"status": "error", "message": str(e)}
    
    def handle_message(self, message: str, history: List[List[str]], session_id: str) -> Tuple[str, List[List[str]], str, Dict[str, Any]]:
        """
        Handle a user message with improved error handling and UX.
        
        Args:
            message: User message
            history: Chat history
            session_id: Session ID
            
        Returns:
            Tuple of (cleared_message, updated_history, session_id, metrics)
        """
        if not message or not message.strip():
            return "", history, session_id, {}
        
        try:
            # Add user message to history
            history.append([message, None])
            
            # Send message to API
            response = requests.post(
                f"{self.api_url}/chat",
                json={"message": message, "session_id": session_id}
            )
            data = response.json()
            
            # Get response and metrics
            bot_response = data.get("response", "")
            session_id = data.get("session_id", session_id)
            metrics = data.get("metrics", {})
            
            # Update history with bot response
            history[-1][1] = bot_response
            
            logger.info(f"Processed message for session {session_id}")
            
            return "", history, session_id, metrics
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_message = f"⚠️ Error: {str(e)}. Please try again or refresh the page."
            history[-1][1] = error_message
            return "", history, session_id, {"error": str(e)}
    
    def handle_clear(self, session_id: str) -> Tuple[List[List[str]], str, Dict[str, Any], Dict[str, Any]]:
        """
        Handle clearing the chat history with improved feedback.
        
        Args:
            session_id: Session ID
            
        Returns:
            Tuple of (cleared_history, new_session_id, cleared_metrics, system_status)
        """
        try:
            if session_id:
                # Clear session via API
                requests.post(f"{self.api_url}/clear-history?session_id={session_id}")
            
            # Initialize a new session
            new_session_id, _, system_status = self.initialize_session()
            
            logger.info(f"Cleared history for session {session_id}, new session: {new_session_id}")
            
            return [], new_session_id, {}, system_status
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return [], session_id, {"error": str(e)}, {"status": "error", "message": str(e)}
    
    def handle_regenerate(self, last_message: str, history: List[List[str]], session_id: str) -> Tuple[List[List[str]], str, Dict[str, Any]]:
        """
        Handle regenerating the last response.
        
        Args:
            last_message: Last user message
            history: Chat history
            session_id: Session ID
            
        Returns:
            Tuple of (updated_history, session_id, metrics)
        """
        if not history:
            return history, session_id, {}
        
        try:
            # Get the last user message
            last_user_message = history[-1][0] if history else ""
            
            if not last_user_message:
                return history, session_id, {}
            
            # Update the last bot response to indicate regeneration
            history[-1][1] = "Regenerating response..."
            
            # Send message to API
            response = requests.post(
                f"{self.api_url}/chat",
                json={"message": last_user_message, "session_id": session_id}
            )
            data = response.json()
            
            # Get response and metrics
            bot_response = data.get("response", "")
            session_id = data.get("session_id", session_id)
            metrics = data.get("metrics", {})
            
            # Update history with new bot response
            history[-1][1] = bot_response
            
            logger.info(f"Regenerated response for session {session_id}")
            
            return history, session_id, metrics
        except Exception as e:
            logger.error(f"Error regenerating response: {e}")
            error_message = f"⚠️ Error regenerating response: {str(e)}. Please try again."
            history[-1][1] = error_message
            return history, session_id, {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status from health endpoint.
        
        Returns:
            Dict of system status
        """
        try:
            response = requests.get(f"{self.api_url.replace('/api', '')}/health")
            return response.json()
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"status": "error", "message": str(e)}
    
    def launch(self, **kwargs):
        """
        Launch the Gradio interface.
        
        Args:
            **kwargs: Additional arguments for gr.launch()
        """
        self.interface.launch(**kwargs)

# Run the application
if __name__ == "__main__":
    ui = ChatUI()
    ui.launch(share=True)
