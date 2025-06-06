#!/usr/bin/env python3
"""
Test script for the SocialSim module.

This script tests the basic functionality of the SocialSim module:
1. Loading personas from PersonaHub
2. Running a simple survey experiment with a mock provider
3. Analyzing the results

Usage:
    python test_socialsim.py
"""

import os
import logging
import time
import random
from unittest.mock import MagicMock
from selfplay.socialsim import PersonaHubDB, ExperimentRunner, Persona

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a mock provider for testing (simulating AWS with Claude 3.7)
class MockProvider:
    def __init__(self):
        self.provider_name = "AWS Bedrock"
        self.model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    
    def generate_response(self, messages, **kwargs):
        """Generate a mock response."""
        # Extract the question and options from the messages
        prompt = messages[-1]["content"]
        options = []
        if "Options:" in prompt:
            options_text = prompt.split("Options:")[1].strip()
            options = [opt.strip() for opt in options_text.split(',')]
        
        # Return a random option if available, otherwise a generic response
        if options:
            return random.choice(options)
        else:
            return "This is a mock response."

# Create a mock PersonaHubDB for testing
class MockPersonaHubDB:
    def __init__(self, num_personas=10):
        """Initialize with a number of mock personas."""
        self.personas = []
        for i in range(num_personas):
            persona = Persona()
            persona.id = f"mock_{i}"
            persona.source = "mock"
            persona.description = f"This is a mock persona {i}."
            persona.age = random.randint(18, 80)
            persona.gender = random.choice(["male", "female", "non_binary"])
            persona.education = random.choice(["high_school", "bachelors", "masters", "doctorate"])
            persona.occupation = random.choice(["engineer", "teacher", "doctor", "artist", "student"])
            self.personas.append(persona)
    
    def sample(self, n=5, stratify_by=None, filter_by=None):
        """Sample n personas."""
        return random.sample(self.personas, min(n, len(self.personas)))

def test_persona_loading():
    """Test loading personas from the mock PersonaHubDB."""
    logger.info("Testing persona loading...")
    
    # Create a mock PersonaHubDB
    persona_db = MockPersonaHubDB(num_personas=10)
    
    # Check if personas were loaded
    if len(persona_db.personas) > 0:
        logger.info(f"Successfully loaded {len(persona_db.personas)} mock personas")
        
        # Print some sample personas
        for i in range(min(3, len(persona_db.personas))):
            logger.info(f"Persona {i+1}: {persona_db.personas[i]}")
        
        return True, persona_db
    else:
        logger.error("Failed to create mock personas")
        return False, None

def test_simple_survey(persona_db):
    """Test running a simple survey experiment with mock provider."""
    logger.info("Testing simple survey experiment...")
    
    # Create experiment runner
    runner = ExperimentRunner(persona_db)
    
    # Monkey patch the provider_interface.get_provider function
    import selfplay.provider_interface
    original_get_provider = selfplay.provider_interface.get_provider
    selfplay.provider_interface.get_provider = lambda provider, **kwargs: MockProvider()
    
    # Define survey question and options
    question = "Do you prefer cats or dogs as pets?"
    options = ["Cats", "Dogs", "Both equally", "Neither"]
    
    # Run the survey with a small number of personas
    results = runner.run_survey(
        question=question,
        options=options,
        n=5,  # Small number for the test
        provider="aws",  # Using AWS Bedrock (mocked)
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude 3.7 Sonnet model
        question_type="multiple_choice"
    )
    
    # Restore the original get_provider function
    selfplay.provider_interface.get_provider = original_get_provider
    
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
        
        return True
    else:
        logger.error("Survey experiment failed")
        return False

def main():
    """Main function."""
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
