#!/usr/bin/env python3
"""
Entry point script for LCM Comparison Framework.
"""

import os
import sys
import argparse
import uvicorn

def main():
    """Run the LCM Comparison Framework app."""
    parser = argparse.ArgumentParser(description="LCM Comparison Framework")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--ui", action="store_true", help="Run UI only")
    parser.add_argument("--api", action="store_true", help="Run API only")
    parser.add_argument("--comparison", action="store_true", help="Run in comparison mode")
    
    args = parser.parse_args()
    
    if args.ui:
        if args.comparison:
            print("Starting comparison UI...")
            from src.ui.head_to_head_ui import ComparisonUI
            ui = ComparisonUI()
            ui.launch(server_name=args.host, server_port=args.port)
        else:
            print("Starting chat UI...")
            from src.ui.chat_ui import ChatUI
            ui = ChatUI()
            ui.launch(server_name=args.host, server_port=args.port)
    elif args.api or not (args.ui or args.comparison):
        print(f"Starting API server on {args.host}:{args.port}...")
        uvicorn.run(
            "src.api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )

if __name__ == "__main__":
    main()