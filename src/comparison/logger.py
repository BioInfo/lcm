#!/usr/bin/env python3
"""
Comparison Data Logger for Meta LCM Chatbot.
This module handles logging and analytics for model comparison data.
"""

import os
import json
import time
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComparisonLogger:
    """
    Logger for model comparison data.
    Handles storage, retrieval, and analytics for comparison results.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the comparison logger.
        
        Args:
            base_path: Base path for data storage (optional)
        """
        self.base_path = base_path or os.getcwd()
        self.data_dir = os.path.join(self.base_path, "app", "data", "logs")
        self.db_path = os.path.join(self.data_dir, "comparison_data.db")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database for comparison data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create comparison table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                prompt TEXT,
                lcm_response TEXT,
                llama_response TEXT,
                category TEXT,
                is_test_case INTEGER,
                has_image INTEGER,
                image_path TEXT,
                timestamp TEXT
            )
            ''')
            
            # Create metrics table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comparison_id INTEGER,
                metric_type TEXT,
                lcm_value REAL,
                llama_value REAL,
                winner TEXT,
                difference REAL,
                FOREIGN KEY (comparison_id) REFERENCES comparisons (id)
            )
            ''')
            
            # Create raw metrics table (for storing full JSON)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_metrics (
                comparison_id INTEGER PRIMARY KEY,
                metrics_json TEXT,
                FOREIGN KEY (comparison_id) REFERENCES comparisons (id)
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def log_comparison(self, 
                      session_id: str,
                      prompt: str,
                      lcm_response: str,
                      llama_response: str,
                      metrics: Dict[str, Any],
                      category: str = "custom",
                      is_test_case: bool = False,
                      image_path: Optional[str] = None) -> int:
        """
        Log a model comparison.
        
        Args:
            session_id: Session identifier
            prompt: User prompt
            lcm_response: Response from LCM model
            llama_response: Response from Llama model
            metrics: Comparison metrics
            category: Test case category (default: "custom")
            is_test_case: Whether this is a pre-defined test case
            image_path: Path to image (for multimodal comparisons)
            
        Returns:
            Comparison ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert comparison
            timestamp = datetime.now().isoformat()
            cursor.execute('''
            INSERT INTO comparisons (
                session_id, prompt, lcm_response, llama_response, 
                category, is_test_case, has_image, image_path, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, prompt, lcm_response, llama_response,
                category, 1 if is_test_case else 0, 1 if image_path else 0, image_path, timestamp
            ))
            
            comparison_id = cursor.lastrowid
            
            # Insert metrics
            self._insert_metrics(cursor, comparison_id, metrics)
            
            # Insert raw metrics JSON
            cursor.execute('''
            INSERT INTO raw_metrics (comparison_id, metrics_json)
            VALUES (?, ?)
            ''', (comparison_id, json.dumps(metrics)))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Logged comparison {comparison_id} for session {session_id}")
            
            return comparison_id
        except Exception as e:
            logger.error(f"Error logging comparison: {e}")
            return -1
    
    def _insert_metrics(self, cursor, comparison_id: int, metrics: Dict[str, Any]):
        """
        Insert metrics into the database.
        
        Args:
            cursor: Database cursor
            comparison_id: Comparison ID
            metrics: Comparison metrics
        """
        # Process speed metrics
        if "speed" in metrics:
            speed = metrics["speed"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "speed", 
                speed.get("lcm_time", 0), 
                speed.get("llama_time", 0),
                speed.get("faster_model", "Tie"),
                speed.get("difference_seconds", 0)
            ))
        
        # Process reasoning metrics
        if "reasoning" in metrics:
            reasoning = metrics["reasoning"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "reasoning", 
                reasoning.get("lcm_normalized_score", 0), 
                reasoning.get("llama_normalized_score", 0),
                reasoning.get("better_reasoning", "Tie"),
                reasoning.get("difference", 0)
            ))
        
        # Process creativity metrics
        if "creativity" in metrics:
            creativity = metrics["creativity"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "creativity", 
                creativity.get("lcm_creativity_score", 0), 
                creativity.get("llama_creativity_score", 0),
                creativity.get("more_creative", "Tie"),
                creativity.get("difference", 0)
            ))
        
        # Process factuality metrics
        if "factuality" in metrics:
            factuality = metrics["factuality"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "factuality", 
                factuality.get("lcm_factuality_score", 0), 
                factuality.get("llama_factuality_score", 0),
                factuality.get("more_factual", "Tie"),
                factuality.get("difference", 0)
            ))
        
        # Process hallucination risk metrics
        if "hallucination_risk" in metrics:
            hallucination = metrics["hallucination_risk"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "hallucination_risk", 
                hallucination.get("lcm_hallucination_risk", 0), 
                hallucination.get("llama_hallucination_risk", 0),
                hallucination.get("lower_risk", "Tie"),
                hallucination.get("difference", 0)
            ))
        
        # Process concept awareness metrics
        if "concept_awareness" in metrics:
            concept = metrics["concept_awareness"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "concept_awareness", 
                concept.get("lcm_concept_score", 0), 
                concept.get("llama_concept_score", 0),
                concept.get("better_concept_awareness", "Tie"),
                concept.get("difference", 0)
            ))
        
        # Process coherence metrics
        if "coherence" in metrics:
            coherence = metrics["coherence"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "coherence", 
                coherence.get("lcm_coherence_score", 0), 
                coherence.get("llama_coherence_score", 0),
                coherence.get("more_coherent", "Tie"),
                coherence.get("difference", 0)
            ))
        
        # Process multimodal metrics
        if "multimodal" in metrics:
            multimodal = metrics["multimodal"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "multimodal", 
                multimodal.get("lcm_image_understanding", 0), 
                multimodal.get("llama_image_understanding", 0),
                multimodal.get("better_image_understanding", "Tie"),
                multimodal.get("difference", 0)
            ))
        
        # Process cross-lingual metrics
        if "cross_lingual" in metrics:
            cross_lingual = metrics["cross_lingual"]
            cursor.execute('''
            INSERT INTO metrics (comparison_id, metric_type, lcm_value, llama_value, winner, difference)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                comparison_id, "cross_lingual", 
                cross_lingual.get("lcm_cross_lingual_score", 0), 
                cross_lingual.get("llama_cross_lingual_score", 0),
                cross_lingual.get("better_cross_lingual", "Tie"),
                cross_lingual.get("difference", 0)
            ))
    
    def get_comparison(self, comparison_id: int) -> Dict[str, Any]:
        """
        Get a comparison by ID.
        
        Args:
            comparison_id: Comparison ID
            
        Returns:
            Comparison data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get comparison
            cursor.execute('''
            SELECT * FROM comparisons WHERE id = ?
            ''', (comparison_id,))
            
            comparison = dict(cursor.fetchone())
            
            # Get metrics
            cursor.execute('''
            SELECT * FROM metrics WHERE comparison_id = ?
            ''', (comparison_id,))
            
            metrics = [dict(row) for row in cursor.fetchall()]
            comparison["metrics"] = metrics
            
            # Get raw metrics
            cursor.execute('''
            SELECT metrics_json FROM raw_metrics WHERE comparison_id = ?
            ''', (comparison_id,))
            
            raw_metrics = cursor.fetchone()
            if raw_metrics:
                comparison["raw_metrics"] = json.loads(raw_metrics[0])
            
            conn.close()
            
            return comparison
        except Exception as e:
            logger.error(f"Error getting comparison {comparison_id}: {e}")
            return {}
    
    def get_session_comparisons(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all comparisons for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of comparison data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get comparisons
            cursor.execute('''
            SELECT id FROM comparisons WHERE session_id = ? ORDER BY timestamp DESC
            ''', (session_id,))
            
            comparison_ids = [row["id"] for row in cursor.fetchall()]
            conn.close()
            
            # Get each comparison
            comparisons = [self.get_comparison(cid) for cid in comparison_ids]
            
            return comparisons
        except Exception as e:
            logger.error(f"Error getting comparisons for session {session_id}: {e}")
            return []
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for all comparisons.
        
        Returns:
            Summary statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total comparisons
            cursor.execute('SELECT COUNT(*) FROM comparisons')
            total_comparisons = cursor.fetchone()[0]
            
            # Get win counts
            cursor.execute('''
            SELECT winner, COUNT(*) FROM metrics 
            GROUP BY winner
            ''')
            
            wins = {"LCM": 0, "Llama": 0, "Tie": 0}
            for row in cursor.fetchall():
                winner, count = row
                if winner in wins:
                    wins[winner] = count
            
            # Get category distribution
            cursor.execute('''
            SELECT category, COUNT(*) FROM comparisons 
            GROUP BY category
            ''')
            
            categories = {}
            for row in cursor.fetchall():
                category, count = row
                categories[category] = count
            
            # Get metric averages
            cursor.execute('''
            SELECT metric_type, 
                   AVG(lcm_value) as lcm_avg, 
                   AVG(llama_value) as llama_avg,
                   AVG(difference) as avg_diff
            FROM metrics 
            GROUP BY metric_type
            ''')
            
            metrics = {}
            for row in cursor.fetchall():
                metric_type, lcm_avg, llama_avg, avg_diff = row
                metrics[metric_type] = {
                    "lcm_avg": lcm_avg,
                    "llama_avg": llama_avg,
                    "avg_diff": avg_diff
                }
            
            # Get multimodal stats
            cursor.execute('''
            SELECT COUNT(*) FROM comparisons WHERE has_image = 1
            ''')
            multimodal_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Compile summary
            summary = {
                "total_comparisons": total_comparisons,
                "lcm_wins": wins["LCM"],
                "llama_wins": wins["Llama"],
                "tie": wins["Tie"],
   
(Content truncated due to size limit. Use line ranges to read in chunks)