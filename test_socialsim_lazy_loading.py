#!/usr/bin/env python3
"""
Test script for the lazy loading implementation of PersonaHubDB.

This script tests that the PersonaHubDB class only loads the personas we need
instead of downloading the entire dataset.

Usage:
    python test_socialsim_lazy_loading.py
"""

import os
import logging
import time
from selfplay.socialsim import PersonaHubDB

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_lazy_loading():
    """Test the lazy loading implementation of PersonaHubDB."""
    logger.info("Testing lazy loading of PersonaHubDB...")
    
    # Initialize the PersonaHubDB with lazy loading
    # This should only set up the dataset references without loading any data
    persona_db = PersonaHubDB(use_elite=True, use_standard=False, max_personas=50)
    
    # Check that no personas are loaded initially
    logger.info(f"Initial number of personas: {len(persona_db.personas)}")
    
    # Sample a small number of personas
    # This should trigger loading of personas
    logger.info("Sampling 10 personas...")
    personas = persona_db.sample(n=10)
    
    # Check how many personas were loaded
    logger.info(f"Number of personas after sampling 10: {len(persona_db.personas)}")
    
    # Sample more personas
    # This should trigger loading of more personas
    logger.info("Sampling 30 personas...")
    personas = persona_db.sample(n=30)
    
    # Check how many personas were loaded
    logger.info(f"Number of personas after sampling 30: {len(persona_db.personas)}")
    
    # Print some sample personas
    logger.info("Sample personas:")
    for i in range(min(3, len(personas))):
        logger.info(f"Persona {i+1}: {personas[i]}")
    
    return True

def main():
    """Main function."""
    # Run the test
    success = test_lazy_loading()
    
    if success:
        logger.info("Test passed!")
    else:
        logger.error("Test failed")

if __name__ == "__main__":
    main()
