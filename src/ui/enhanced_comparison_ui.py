#!/usr/bin/env python3
"""
Enhanced UI Styling and User Experience for Meta LCM Chatbot Comparison Feature.
This module provides polished UI components and improved user experience.
"""

import os
import gradio as gr
import json
import time
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.figure import Figure
import pandas as pd

# Custom theme for the comparison UI
COMPARISON_THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="orange",
    neutral_hue="gray",
    radius_size=gr.themes.sizes.radius_sm,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_text_color="#333333",
    background_fill="#f8f9fa",
    block_background_fill="#ffffff",
    block_label_background_fill="#f0f2f5",
    block_title_text_color="#1976d2",
    button_primary_background_fill="#1976d2",
    button_primary_background_fill_hover="#1565c0",
    button_secondary_background_fill="#ff9800",
    button_secondary_background_fill_hover="#f57c00",
    border_color_primary="#1976d2",
    block_shadow="0px 4px 6px rgba(0, 0, 0, 0.1)",
    block_title_text_weight="600",
)

# Custom CSS for enhanced styling
CUSTOM_CSS = """
/* Global styles */
body {
    font-family: 'Inter', sans-serif;
    color: #333333;
}

/* Header styling */
#comparison-header {
    background: linear-gradient(90deg, #1976d2, #2196f3);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

#comparison-header h1 {
    color: white;
    text-align: center;
    margin: 0;
    font-weight: 700;
    font-size: 2.2rem;
}

#comparison-header p {
    color: rgba(255, 255, 255, 0.9);
    text-align: center;
    margin: 10px 0 0 0;
    font-size: 1.1rem;
}

/* Model comparison containers */
.model-container {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    transition: all 0.3s ease;
}

.model-container:hover {
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.lcm-container {
    border-left: 4px solid #1976d2;
}

.llama-container {
    border-left: 4px solid #ff9800;
}

/* Model labels */
.model-label {
    font-weight: 600;
    padding: 5px 10px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 10px;
}

.lcm-label {
    background-color: #e3f2fd;
    color: #1976d2;
}

.llama-label {
    background-color: #fff3e0;
    color: #ff9800;
}

/* Metrics styling */
.metrics-container {
    background-color: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
    margin-top: 20px;
}

.metrics-title {
    font-weight: 600;
    color: #555;
    margin-bottom: 10px;
    font-size: 1.1rem;
}

.metric-card {
    background: white;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    text-align: center;
}

.metric-label {
    text-align: center;
    color: #666;
    font-size: 0.9rem;
    margin-top: 5px;
}

/* Winner badges */
.winner-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-left: 8px;
}

.lcm-winner {
    background-color: #e3f2fd;
    color: #1976d2;
}

.llama-winner {
    background-color: #fff3e0;
    color: #ff9800;
}

/* Button styling */
.action-button {
    border-radius: 20px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
}

.primary-button {
    background-color: #1976d2 !important;
    color: white !important;
}

.primary-button:hover {
    background-color: #1565c0 !important;
    box-shadow: 0 4px 8px rgba(25, 118, 210, 0.3) !important;
}

.secondary-button {
    background-color: #ff9800 !important;
    color: white !important;
}

.secondary-button:hover {
    background-color: #f57c00 !important;
    box-shadow: 0 4px 8px rgba(255, 152, 0, 0.3) !important;
}

/* Tabs styling */
.tab-nav button {
    font-weight: 600 !important;
    padding: 10px 16px !important;
}

.tab-nav button.selected {
    color: #1976d2 !important;
    border-bottom-color: #1976d2 !important;
}

/* Visualization enhancements */
.chart-container {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    margin: 20px 0;
}

/* Tooltip styling */
.tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
}

.tooltip .tooltip-text {
    visibility: hidden;
    width: 200px;
    background-color: #555;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 10px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    margin-left: -100px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

/* Loading animation */
.loading-spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #1976d2;
    animation: spin 1s linear infinite;
    margin: 20px auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
    #comparison-header h1 {
        font-size: 1.8rem;
    }
    
    #comparison-header p {
        font-size: 1rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
    }
}

/* Accessibility improvements */
button:focus, input:focus, select:focus, textarea:focus {
    outline: 2px solid #1976d2;
    outline-offset: 2px;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .model-container {
        background-color: #2d2d2d;
        border-color: #444;
    }
    
    .lcm-container {
        border-left-color: #42a5f5;
    }
    
    .llama-container {
        border-left-color: #ffb74d;
    }
    
    .lcm-label {
        background-color: rgba(66, 165, 245, 0.2);
        color: #90caf9;
    }
    
    .llama-label {
        background-color: rgba(255, 183, 77, 0.2);
        color: #ffcc80;
    }
}
"""

class EnhancedComparisonUI:
    """
    Enhanced UI components for the model comparison feature.
    Provides polished visualizations and improved user experience.
    """
    
    @staticmethod
    def create_radar_chart(metrics: Dict[str, Any], figsize: Tuple[int, int] = (8, 8)) -> Figure:
        """
        Create an enhanced radar chart for model comparison metrics.
        
        Args:
            metrics: Dictionary of comparison metrics
            figsize: Figure size (width, height)
            
        Returns:
            Matplotlib figure
        """
        try:
            # Extract metrics for radar chart
            categories = []
            lcm_scores = []
            llama_scores = []
            
            # Speed (inverted - lower is better)
            if "speed" in metrics:
                categories.append("Speed")
                lcm_time = metrics["speed"].get("lcm_time", 0)
                llama_time = metrics["speed"].get("llama_time", 0)
                max_time = max(lcm_time, llama_time, 0.001)
                # Normalize and invert (higher is better)
                lcm_scores.append(1 - (lcm_time / max_time))
                llama_scores.append(1 - (llama_time / max_time))
            
            # Reasoning
            if "reasoning" in metrics:
                categories.append("Reasoning")
                lcm_score = metrics["reasoning"].get("lcm_normalized_score", 0)
                llama_score = metrics["reasoning"].get("llama_normalized_score", 0)
                lcm_scores.append(lcm_score)
                llama_scores.append(llama_score)
            
            # Creativity
            if "creativity" in metrics:
                categories.append("Creativity")
                lcm_score = metrics["creativity"].get("lcm_creativity_score", 0)
                llama_score = metrics["creativity"].get("llama_creativity_score", 0)
                max_score = max(lcm_score, llama_score, 0.001)
                lcm_scores.append(lcm_score / max_score)
                llama_scores.append(llama_score / max_score)
            
            # Factuality
            if "factuality" in metrics:
                categories.append("Factuality")
                lcm_score = metrics["factuality"].get("lcm_factuality_score", 0)
                llama_score = metrics["factuality"].get("llama_factuality_score", 0)
                lcm_scores.append(lcm_score)
                llama_scores.append(llama_score)
            
            # Hallucination risk (inverted - lower is better)
            if "hallucination_risk" in metrics:
                categories.append("Reliability")
                lcm_risk = metrics["hallucination_risk"].get("lcm_hallucination_risk", 0)
                llama_risk = metrics["hallucination_risk"].get("llama_hallucination_risk", 0)
                # Normalize and invert (higher is better)
                lcm_scores.append(1 - lcm_risk)
                llama_scores.append(1 - llama_risk)
            
            # Add concept awareness if available
            if "concept_awareness" in metrics:
                categories.append("Concept\nAwareness")
                lcm_score = metrics["concept_awareness"].get("lcm_concept_score", 0)
                llama_score = metrics["concept_awareness"].get("llama_concept_score", 0)
                lcm_scores.append(lcm_score)
                llama_scores.append(llama_score)
            
            # Add coherence if available
            if "coherence" in metrics:
                categories.append("Coherence")
                lcm_score = metrics["coherence"].get("lcm_coherence_score", 0)
                llama_score = metrics["coherence"].get("llama_coherence_score", 0)
                lcm_scores.append(lcm_score)
                llama_scores.append(llama_score)
            
            # Add multimodal if available
            if "multimodal" in metrics:
                categories.append("Image\nUnderstanding")
                lcm_score = metrics["multimodal"].get("lcm_image_understanding", 0)
                llama_score = metrics["multimodal"].get("llama_image_understanding", 0)
                lcm_scores.append(lcm_score)
                llama_scores.append(llama_score)
            
            # Create figure with improved styling
            fig = plt.figure(figsize=figsize, facecolor='white')
            ax = fig.add_subplot(111, polar=True)
            
            # Number of variables
            N = len(categories)
            if N < 3:
                # Not enough metrics for radar chart
                ax.text(0.5, 0.5, "Not enough metrics for radar chart", 
                       ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Angle of each axis
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Close the loop
            
            # Add the first point at the end to close the polygon
            lcm_scores += lcm_scores[:1]
            llama_scores += llama_scores[:1]
            
            # Draw the chart with enhanced styling
            ax.plot(angles, lcm_scores, 'o-', linewidth=2, label='LCM-7B', color='#1976d2')
            ax.fill(angles, lcm_scores, alpha=0.25, color='#1976d2')
            
            ax.plot(angles, llama_scores, 'o-', linewidth=2, label='Llama-7B', color='#ff9800')
            ax.fill(angles, llama_scores, alpha=0.25, color='#ff9800')
            
            # Fix axis to go in the right order and start at 12 o'clock
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            
            # Draw axis lines for each angle and label
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
            
            # Draw y-axis labels (0.2, 0.4, 0.6, 0.8, 1.0)
            ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
            ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10)
            ax.set_ylim(0, 1)
            
            # Add subtle grid lines with improved styling
            ax.grid(True, linestyle='--', alpha=0.7, color='#cccccc')
            
            # Add legend with enhanced styling
            legend = ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), fontsize=12)
            legend.get_frame().set_alpha(0.8)
            legend.get_frame().set_edgecolor('#cccccc')
            
            # Add subtle background color to make the chart pop
            ax.set_facecolor('#f8f9fa')
            
            # Add title with improved styling
            plt.title('Model Comparison Metrics', fontsize=16, fontweight='bold', pad=20)
            
            return fig
        except Exception as e:
            # Return a simple error plot
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, f"Error creating visualization: {str(e)}", ha='center', va='center')
            ax.axis('off')
            return fig
    
    @staticmethod
    def create_bar_comparison(metrics: Dict[str, Any], metric_type: str, figsize: Tuple[int, int] = (10, 6)) -> Figure:
        """
        Create an enhanced bar chart comparing a specific metric between models.
        
        Args:
            metrics: Dictionary of comparison metrics
            metric_type: Type of metric to compare
            figsize: Figure size (width, height)
            
        Returns:
            Matplotlib figure
        """
        try:
            # Create figure with improved styling
            fig, ax = plt.subplots(figsize=figsize, facecolor='white')
            
            # Extract metric data
            if metric_type not in metrics:
                ax.text(0.5, 0.5, f"Metric '{metric_type}' not found", ha='center', va='center')
                ax.axis('off')
                return fig
            
            metric_data = metrics[metric_type]
            
            # Determine which values to plot based on metric type
            if metric_type == "speed":
                lcm_value = metric_data.get("lcm_time", 0)
                llama_value = metric_data.get("llama_time", 0)
                title = "Response Time (lower is better)"
                ylabel = "Time (seconds)"
                invert = True  # Lower is better
            elif metric_type == "reasoning":
                lcm_value = metric_data.get("lcm_reasoning_score", 0)
                llama_value = metric_data.get("llama_reasoning_score", 0)
                title = "Reasoning Quality"
                ylabel = "Score"
                invert = False
            elif metric_type == "creativity":
                lcm_value = metric_data.get("lcm_creativity_score", 0)
                llama_value = metric_data.get("llama_creativity_score", 0)
                title = "Creativity Score"
                ylabel = "Score"
                invert = False
            elif metric_type == "factuality":
                lcm_value = metric_data.get("lcm_factuality_score", 0)
                llama_value = metric_data.get("llama_factuality_score", 0)
                title = "Factuality Score"
                ylabel = "Score"
                invert = False
            elif metric_type == "hallucination_risk":
                lcm_value = metric_data.get("lcm_hallucination_risk", 0)
                llama_value = metric_data.get("llama_hallucination_risk", 0)
                title = "Hallucination Risk (lower is better)"
                ylabel = "Risk Score"
                invert = True  # Lower is better
            else:
                # Generic handling for other metrics
       
(Content truncated due to size limit. Use line ranges to read in chunks)