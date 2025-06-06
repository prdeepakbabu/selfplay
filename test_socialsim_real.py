#!/usr/bin/env python3
"""
Real test script for the SocialSim module.

This script tests the SocialSim module with real data and API calls:
1. Loading personas from PersonaHub (limited sample)
2. Running a simple survey experiment with AWS Bedrock and Claude 3.7
3. Analyzing the results

Usage:
    python test_socialsim_real.py
"""

import os
import logging
import time
from selfplay.socialsim import PersonaHubDB, ExperimentRunner

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_persona_loading():
    """Test loading personas from PersonaHub."""
    logger.info("Testing persona loading from PersonaHub...")
    
    # Load a small number of personas from the elite dataset only
    persona_db = PersonaHubDB(use_elite=True, use_standard=False)
    
    # Check if personas were loaded
    if len(persona_db.personas) > 0:
        logger.info(f"Successfully loaded {len(persona_db.personas)} personas")
        
        # Print some sample personas
        for i in range(min(3, len(persona_db.personas))):
            logger.info(f"Persona {i+1}: {persona_db.personas[i]}")
        
        return True, persona_db
    else:
        logger.error("Failed to load personas")
        return False, None

def test_simple_survey(persona_db):
    """Test running a simple survey experiment with AWS Bedrock and Claude 3.7."""
    logger.info("Testing simple survey experiment with AWS Bedrock and Claude 3.7...")
    
    # Create experiment runner
    runner = ExperimentRunner(persona_db)
    
    # Define survey question and options
    question = "Do you prefer cats or dogs as pets?"
    options = ["Cats", "Dogs", "Both equally", "Neither"]
    
    # Run the survey with a small number of personas
    results = runner.run_survey(
        question=question,
        options=options,
        n=5,  # Small number for the test
        provider="aws",  # Using AWS Bedrock
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude 3.7 Sonnet model
        question_type="multiple_choice"
    )
    
    if results:
        # Print summary statistics
        logger.info("Survey results:")
        stats = results.summary_statistics()
        print("\nResponse counts:")
        for option, count in stats['response_counts'].items():
            print(f"  {option}: {count}")
        
        print("\nResponse percentages:")
        for option, percentage in stats['response_percentages'].items():
            print(f"  {option}: {percentage:.1f}%")
        
        # Export results
        results.export_csv("real_survey_results.csv")
        logger.info("Results exported to real_survey_results.csv")
        
        return True
    else:
        logger.error("Survey experiment failed")
        return False

def main():
    """Main function."""
    # Check if AWS credentials are available
    # AWS credentials should be in ~/.aws/credentials
    if not os.path.exists(os.path.expanduser("~/.aws/credentials")):
        logger.warning("AWS credentials file not found at ~/.aws/credentials")
        logger.warning("Make sure AWS credentials are properly configured")
    
    # Run the tests
    persona_loading_success, persona_db = test_persona_loading()
    
    if persona_loading_success:
        time.sleep(1)  # Add a small delay between tests
        survey_success = test_simple_survey(persona_db)
        
        if persona_loading_success and survey_success:
            logger.info("All tests passed!")
        else:
            logger.error("Some tests failed")
    else:
        logger.error("Persona loading failed, skipping survey test")

if __name__ == "__main__":
    main()
