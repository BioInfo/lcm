#!/usr/bin/env python3
"""
Cross-lingual and Multimodal Test Cases for Meta LCM Chatbot.
This module provides pre-defined test cases for comparing LCM and Llama models.
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# Define test case categories
TEST_CATEGORIES = [
    "general",
    "reasoning",
    "creativity",
    "cross_lingual",
    "multimodal"
]

# Define test cases
TEST_CASES = {
    "general": [
        {
            "prompt": "Explain the concept of quantum entanglement in simple terms.",
            "category": "explanation",
            "description": "Tests ability to explain complex scientific concepts clearly"
        },
        {
            "prompt": "What are the main differences between renewable and non-renewable energy sources?",
            "category": "comparison",
            "description": "Tests ability to compare and contrast related concepts"
        },
        {
            "prompt": "Summarize the key principles of machine learning.",
            "category": "summary",
            "description": "Tests ability to summarize a technical field concisely"
        }
    ],
    "reasoning": [
        {
            "prompt": "If a train travels at 60 mph for 3 hours, then at 80 mph for 2 hours, what is the average speed?",
            "category": "math",
            "description": "Tests mathematical reasoning and step-by-step problem solving"
        },
        {
            "prompt": "A bat and ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
            "category": "logic",
            "description": "Tests logical reasoning and avoiding common cognitive biases"
        },
        {
            "prompt": "If all roses are flowers and some flowers fade quickly, can we conclude that some roses fade quickly?",
            "category": "syllogism",
            "description": "Tests syllogistic reasoning and logical deduction"
        }
    ],
    "creativity": [
        {
            "prompt": "Write a short poem about artificial intelligence.",
            "category": "creative_writing",
            "description": "Tests creative expression and metaphorical thinking"
        },
        {
            "prompt": "Invent a new sport that combines elements of basketball and chess.",
            "category": "invention",
            "description": "Tests creative combination of disparate concepts"
        },
        {
            "prompt": "Describe a world where humans can photosynthesize like plants.",
            "category": "imagination",
            "description": "Tests speculative thinking and world-building"
        }
    ],
    "cross_lingual": [
        {
            "prompt": "Translate 'The quick brown fox jumps over the lazy dog' to French, Spanish, and German.",
            "category": "translation",
            "description": "Tests basic translation capabilities across multiple languages"
        },
        {
            "prompt": "Explain the concept of 'hygge' from Danish culture and similar concepts in other cultures.",
            "category": "cultural_concepts",
            "description": "Tests understanding of culture-specific concepts"
        },
        {
            "prompt": "Compare how the greeting 'How are you?' differs in meaning and usage across English, Japanese, and Spanish cultures.",
            "category": "pragmatics",
            "description": "Tests understanding of pragmatic differences across languages"
        },
        {
            "prompt": "Respond to this question in both English and Spanish: What are the benefits of being bilingual?",
            "category": "bilingual_response",
            "description": "Tests ability to generate content in multiple languages"
        },
        {
            "prompt": "Translate this idiom to equivalent expressions in other languages: 'It's raining cats and dogs.'",
            "category": "idiom_translation",
            "description": "Tests understanding and translation of non-literal expressions"
        }
    ],
    "multimodal": [
        {
            "prompt": "Describe what you see in this image.",
            "category": "image_description",
            "description": "Tests basic image understanding and description",
            "requires_image": True,
            "image_path": "app/data/images/city_street.jpg"
        },
        {
            "prompt": "What emotions does this image convey?",
            "category": "image_emotion",
            "description": "Tests emotional and aesthetic interpretation of images",
            "requires_image": True,
            "image_path": "app/data/images/sunset_beach.jpg"
        },
        {
            "prompt": "Identify the objects in this image and explain how they relate to each other.",
            "category": "image_relationship",
            "description": "Tests spatial reasoning and object relationship understanding",
            "requires_image": True,
            "image_path": "app/data/images/office_desk.jpg"
        },
        {
            "prompt": "What story might this image be telling?",
            "category": "image_narrative",
            "description": "Tests narrative construction from visual information",
            "requires_image": True,
            "image_path": "app/data/images/park_scene.jpg"
        },
        {
            "prompt": "Based on this image, what might have happened just before this moment, and what might happen next?",
            "category": "image_temporal",
            "description": "Tests temporal reasoning from static visual information",
            "requires_image": True,
            "image_path": "app/data/images/cafe_interaction.jpg"
        }
    ]
}

class TestCaseManager:
    """
    Manages test cases for model comparison.
    Provides access to pre-defined test cases and handles image paths.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the test case manager.
        
        Args:
            base_path: Base path for image files (optional)
        """
        self.base_path = base_path or str(Path(__file__).parent.parent.parent)
        self.test_cases = TEST_CASES
        self.categories = TEST_CATEGORIES
        
        # Ensure image directory exists
        self._ensure_image_directory()
        
        # Create sample images if they don't exist
        self._create_sample_images()
    
    def _ensure_image_directory(self):
        """Ensure the image directory exists."""
        image_dir = os.path.join(self.base_path, "app", "data", "images")
        os.makedirs(image_dir, exist_ok=True)
    
    def _create_sample_images(self):
        """Create sample images for testing if they don't exist."""
        # In a real implementation, these would be actual images
        # For the MVP, we'll create placeholder text files
        image_files = [
            "city_street.jpg",
            "sunset_beach.jpg",
            "office_desk.jpg",
            "park_scene.jpg",
            "cafe_interaction.jpg"
        ]
        
        for image_file in image_files:
            image_path = os.path.join(self.base_path, "app", "data", "images", image_file)
            if not os.path.exists(image_path):
                with open(image_path, "w") as f:
                    f.write(f"Placeholder for {image_file}\n")
                    f.write("In a real implementation, this would be an actual image file.")
    
    def get_test_case(self, category: str = None, index: int = None) -> Dict[str, Any]:
        """
        Get a test case.
        
        Args:
            category: Test case category (optional)
            index: Test case index within category (optional)
            
        Returns:
            Test case dictionary
        """
        import random
        
        if category and category in self.test_cases:
            cases = self.test_cases[category]
            if index is not None and 0 <= index < len(cases):
                case = cases[index]
            else:
                case = random.choice(cases)
        else:
            # Random category and case
            category = random.choice(self.categories)
            case = random.choice(self.test_cases[category])
        
        # Update image path if needed
        if case.get("requires_image", False) and "image_path" in case:
            case["image_path"] = os.path.join(self.base_path, case["image_path"])
        
        return case
    
    def get_all_test_cases(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all test cases.
        
        Returns:
            Dictionary of all test cases by category
        """
        # Make a deep copy to avoid modifying the original
        import copy
        result = copy.deepcopy(self.test_cases)
        
        # Update image paths
        for category, cases in result.items():
            for case in cases:
                if case.get("requires_image", False) and "image_path" in case:
                    case["image_path"] = os.path.join(self.base_path, case["image_path"])
        
        return result
    
    def get_categories(self) -> List[str]:
        """
        Get all test case categories.
        
        Returns:
            List of category names
        """
        return self.categories

# Simple test function
def test_manager():
    """Test the test case manager."""
    manager = TestCaseManager()
    
    # Get a random test case
    test_case = manager.get_test_case()
    print(f"Random test case: {json.dumps(test_case, indent=2)}")
    
    # Get a specific category
    test_case = manager.get_test_case("cross_lingual")
    print(f"Cross-lingual test case: {json.dumps(test_case, indent=2)}")
    
    # Get all test cases
    all_cases = manager.get_all_test_cases()
    print(f"Total categories: {len(all_cases)}")
    print(f"Total test cases: {sum(len(cases) for cases in all_cases.values())}")
    
    return all_cases

if __name__ == "__main__":
    # Run test if executed directly
    test_manager()
