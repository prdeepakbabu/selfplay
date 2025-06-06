#!/usr/bin/env python3
"""
A/B test script for the SocialSim module with AWS Bedrock and Claude 3.7.

This script tests the A/B testing functionality of the SocialSim module:
1. Creating sample personas
2. Running an A/B test with AWS Bedrock and Claude 3.7
3. Analyzing and comparing the results

Usage:
    python test_socialsim_ab_test.py
"""

import os
import logging
import time
import random
from selfplay.socialsim import Persona, ExperimentRunner

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_personas(num_personas=10):
    """Create a small sample of personas manually to avoid downloading the full dataset."""
    logger.info(f"Creating {num_personas} sample personas...")
    
    personas = []
    
    # Sample persona descriptions
    descriptions = [
        "I am a 35-year-old software engineer working at a tech startup in San Francisco. I have a passion for hiking and photography.",
        "I'm a 42-year-old high school teacher from Chicago. I teach history and coach the debate team.",
        "I'm a 28-year-old nurse working in a busy hospital in New York. I enjoy reading and yoga in my free time.",
        "I am a 50-year-old small business owner running a family restaurant in Austin. I love cooking and spending time with my grandchildren.",
        "I'm a 22-year-old college student studying environmental science. I'm passionate about climate activism and sustainable living.",
        "I am a 38-year-old marketing executive at a large corporation. I travel frequently for work and enjoy trying new cuisines.",
        "I'm a 31-year-old freelance graphic designer working from home. I have two cats and enjoy video games in my spare time.",
        "I am a 45-year-old construction worker with 20 years of experience. I enjoy fishing and watching football on weekends.",
        "I'm a 29-year-old veterinarian who recently opened my own practice. I volunteer at animal shelters and love hiking with my dog.",
        "I am a 60-year-old retired librarian. I now spend my time gardening and participating in a local book club.",
        "I'm a 33-year-old single parent working as an accountant. I balance work with raising my two children.",
        "I am a 26-year-old professional musician playing in an orchestra. I also teach piano lessons on the side.",
        "I'm a 41-year-old police officer who has served the community for 15 years. I enjoy woodworking as a hobby.",
        "I am a 37-year-old chef at a fine dining restaurant. I'm constantly experimenting with new recipes and techniques.",
        "I'm a 52-year-old farmer who manages a family farm that's been passed down for generations. I'm interested in sustainable farming practices."
    ]
    
    # Create personas
    for i in range(num_personas):
        persona = Persona()
        persona.id = f"sample_{i}"
        persona.source = "sample"
        persona.description = descriptions[i % len(descriptions)]
        
        # Add some demographic attributes
        persona.age = random.randint(18, 80)
        persona.gender = random.choice(["male", "female", "non_binary"])
        persona.education = random.choice(["high_school", "bachelors", "masters", "doctorate"])
        persona.occupation = random.choice(["engineer", "teacher", "doctor", "artist", "student"])
        
        personas.append(persona)
    
    logger.info(f"Created {len(personas)} sample personas")
    return personas

class SamplePersonaDB:
    """A simple class to mimic PersonaHubDB with a small sample of personas."""
    
    def __init__(self, num_personas=10):
        """Initialize with a number of sample personas."""
        self.personas = create_sample_personas(num_personas)
    
    def sample(self, n=5, stratify_by=None, filter_by=None):
        """Sample n personas."""
        return random.sample(self.personas, min(n, len(self.personas)))

def test_ab_test():
    """Test running an A/B test experiment with AWS Bedrock and Claude 3.7."""
    logger.info("Testing A/B test experiment with AWS Bedrock and Claude 3.7...")
    
    # Create sample personas
    persona_db = SamplePersonaDB(num_personas=10)
    
    # Define control and test questions
    control_question = "Would you support a carbon tax that increases energy costs by 10% but reduces pollution?"
    test_question = "Would you support a clean energy investment that increases energy costs by 10% but creates new jobs?"
    options = ["Strongly support", "Support", "Neutral", "Oppose", "Strongly oppose"]
    
    # Run the A/B test
    results = ExperimentRunner.ab_test(
        persona_db=persona_db,
        control_question=control_question,
        test_question=test_question,
        options=options,
        n=6,  # Small number for the test (3 per group)
        provider="aws",  # Using AWS Bedrock
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude 3.7 Sonnet model
        question_type="multiple_choice"
    )
    
    if results:
        # Compare groups
        logger.info("A/B test results:")
        comparison = results.compare_groups()
        
        if comparison:
            print("\nControl group distribution:")
            for option, percentage in comparison['group_distributions']['control']['response_percentages'].items():
                print(f"  {option}: {percentage:.1f}%")
            
            print("\nTest group distribution:")
            for option, percentage in comparison['group_distributions']['test']['response_percentages'].items():
                print(f"  {option}: {percentage:.1f}%")
            
            if comparison['significance_test']:
                print(f"\nSignificance test: p-value = {comparison['significance_test']['p_value']:.4f}")
                print(f"Significant at 0.05 level: {comparison['significance_test']['significant_at_0.05']}")
        
        # Export results
        results.export_csv("ab_test_results.csv")
        logger.info("Results exported to ab_test_results.csv")
        
        return True
    else:
        logger.error("A/B test experiment failed")
        return False

def main():
    """Main function."""
    # Check if AWS credentials are available
    # AWS credentials should be in ~/.aws/credentials
    if not os.path.exists(os.path.expanduser("~/.aws/credentials")):
        logger.warning("AWS credentials file not found at ~/.aws/credentials")
        logger.warning("Make sure AWS credentials are properly configured")
    
    # Run the test
    ab_test_success = test_ab_test()
    
    if ab_test_success:
        logger.info("Test passed!")
    else:
        logger.error("Test failed")

if __name__ == "__main__":
    main()
