#!/usr/bin/env python3
"""
Script to inspect the structure of the PersonaHub dataset.

This script loads a small sample of the PersonaHub dataset and prints the structure
of the items to understand how to correctly extract persona descriptions.
"""

import logging
from datasets import load_dataset

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_dataset():
    """Inspect the structure of the PersonaHub dataset."""
    logger.info("Loading a small sample of the PersonaHub dataset...")
    
    # Load the dataset with streaming to avoid downloading the entire dataset
    dataset = load_dataset("proj-persona/PersonaHub", "elite_persona", streaming=True)
    
    # Take a small sample of items
    sample_size = 3
    sample_items = []
    
    logger.info(f"Taking a sample of {sample_size} items...")
    for i, item in enumerate(dataset["train"].take(sample_size)):
        sample_items.append(item)
        
    # Print the structure of the sample items
    logger.info("Sample item structure:")
    for i, item in enumerate(sample_items):
        logger.info(f"Item {i+1}:")
        for key, value in item.items():
            if isinstance(value, str):
                # Print a truncated version of string values
                logger.info(f"  {key}: {value[:100]}..." if len(value) > 100 else f"  {key}: {value}")
            else:
                logger.info(f"  {key}: {value}")
        logger.info("---")
    
    # Check if 'instruction' field exists and contains persona descriptions
    if all('instruction' in item for item in sample_items):
        logger.info("All sample items have 'instruction' field.")
        for i, item in enumerate(sample_items):
            instruction = item.get('instruction', '')
            logger.info(f"Item {i+1} instruction field (first 200 chars): {instruction[:200]}...")
    else:
        logger.info("Not all sample items have 'instruction' field.")
        
    # Check for other fields that might contain persona descriptions
    potential_description_fields = ['persona', 'description', 'profile', 'character', 'bio']
    for field in potential_description_fields:
        if any(field in item for item in sample_items):
            logger.info(f"Some items have '{field}' field.")
            for i, item in enumerate(sample_items):
                if field in item:
                    value = item[field]
                    logger.info(f"Item {i+1} {field} field (first 200 chars): {value[:200]}...")

def main():
    """Main function."""
    inspect_dataset()

if __name__ == "__main__":
    main()
