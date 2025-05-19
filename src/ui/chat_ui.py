#!/usr/bin/env python3
"""
Gradio UI for Meta LCM Chatbot.
This module provides the chat interface using Gradio.
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
API_URL = os.environ.get("API_URL", "http://localhost:8000")

class ChatUI:
    """
    Chat UI using Gradio.
    Provides a two-pane layout with Markdown rendering.
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
        Create the Gradio interface.
        
        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(css=self._get_custom_css()) as interface:
            gr.Markdown("# Meta LCM Chatbot")
            gr.Markdown("A lightweight, concept-aware chatbot using Meta's Large Concept Model")
            
            with gr.Row():
                with gr.Column(scale=4):
                    # Chat history (conversation stream)
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=500,
                        elem_id="chatbot"
                    )
                    
                    # Input bar
                    with gr.Row():
                        msg = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here...",
                            show_label=False,
                            elem_id="msg-box"
                        )
                        submit_btn = gr.Button("Send", variant="primary")
                    
                    # Clear button
                    clear_btn = gr.Button("Clear History")
                    
                with gr.Column(scale=1):
                    # Session info
                    session_info = gr.JSON(
                        label="Session Info",
                        elem_id="session-info"
                    )
                    
                    # Performance metrics
                    metrics = gr.JSON(
                        label="Performance Metrics",
                        elem_id="metrics"
                    )
            
            # Hidden state for session ID
            session_id = gr.State("")
            
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
                outputs=[chatbot, session_id, metrics]
            )
            
            # Initialize session on load
            interface.load(
                fn=self.initialize_session,
                inputs=[],
                outputs=[session_id, session_info]
            )
        
        return interface
    
    def _get_custom_css(self) -> str:
        """
        Get custom CSS for the interface.
        
        Returns:
            CSS string
        """
        return """
        #chatbot {
            height: 500px;
            overflow-y: auto;
        }
        #msg-box {
            height: 60px;
        }
        .message {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #e6f7ff;
            text-align: right;
        }
        .bot-message {
            background-color: #f0f0f0;
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
        """
    
    def initialize_session(self) -> Tuple[str, Dict[str, Any]]:
        """
        Initialize a new session.
        
        Returns:
            Tuple of (session_id, session_info)
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
                "status": "active"
            }
            
            logger.info(f"Initialized session: {session_id}")
            
            return session_id, session_info
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return "", {"error": str(e)}
    
    def handle_message(self, message: str, history: List[List[str]], session_id: str) -> Tuple[str, List[List[str]], str, Dict[str, Any]]:
        """
        Handle a user message.
        
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
            history[-1][1] = f"Error: {str(e)}"
            return "", history, session_id, {"error": str(e)}
    
    def handle_clear(self, session_id: str) -> Tuple[List[List[str]], str, Dict[str, Any]]:
        """
        Handle clearing the chat history.
        
        Args:
            session_id: Session ID
            
        Returns:
            Tuple of (cleared_history, new_session_id, cleared_metrics)
        """
        try:
            if session_id:
                # Clear session via API
                requests.post(f"{self.api_url}/clear-history?session_id={session_id}")
            
            # Initialize a new session
            new_session_id, _ = self.initialize_session()
            
            logger.info(f"Cleared history for session {session_id}, new session: {new_session_id}")
            
            return [], new_session_id, {}
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return [], session_id, {"error": str(e)}
    
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
