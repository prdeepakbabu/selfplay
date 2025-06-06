#!/usr/bin/env python3
"""
Example script demonstrating the use of the SocialSim module.

This script shows how to:
1. Load personas from PersonaHub
2. Run a simple survey experiment
3. Run an A/B test experiment
4. Analyze and visualize the results
"""

import os
import sys
import logging
import time

# Add the parent directory to the path so we can import selfplay
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selfplay.socialsim import PersonaHubDB, ExperimentRunner

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_simple_survey():
    """Run a simple survey experiment."""
    logger.info("Running simple survey experiment...")
    
    # Load a small number of personas for the example with lazy loading
    persona_db = PersonaHubDB(use_elite=True, use_standard=False, max_personas=50)
    
    # Create experiment runner
    runner = ExperimentRunner(persona_db)
    
    # Define survey question and options
    question = "Do you support increasing the minimum wage to $15 per hour?"
    options = ["Strongly support", "Support", "Neutral", "Oppose", "Strongly oppose"]
    
    # Run the survey with a small number of personas
    results = runner.run_survey(
        question=question,
        options=options,
        n=10,  # Small number for the example
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
        results.export_csv("survey_results.csv")
        logger.info("Results exported to survey_results.csv")
        
        # Visualize results
        try:
            fig = results.visualize(chart_type="bar", filepath="survey_results.png")
            logger.info("Visualization saved to survey_results.png")
        except Exception as e:
            logger.error(f"Could not create visualization: {str(e)}")
    else:
        logger.error("Survey experiment failed")

def run_ab_test():
    """Run an A/B test experiment."""
    logger.info("Running A/B test experiment...")
    
    # Load a small number of personas for the example with lazy loading
    persona_db = PersonaHubDB(use_elite=True, use_standard=False, max_personas=50)
    
    # Define control and test questions
    control_question = "Would you support a carbon tax that increases energy costs by 10% but reduces pollution?"
    test_question = "Would you support a clean energy investment that increases energy costs by 10% but creates new jobs?"
    options = ["Strongly support", "Support", "Neutral", "Oppose", "Strongly oppose"]
    
    # Run the A/B test with a small number of personas
    results = ExperimentRunner.ab_test(
        persona_db=persona_db,
        control_question=control_question,
        test_question=test_question,
        options=options,
        n=20,  # Small number for the example
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
    else:
        logger.error("A/B test experiment failed")

def main():
    """Main function."""
    # Check if AWS credentials are available
    # AWS credentials can be in ~/.aws/credentials or environment variables
    # For this example, we'll check for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        logger.warning("AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY environment variables not found.")
        logger.warning("Make sure AWS credentials are available in ~/.aws/credentials or as environment variables.")
    
    # Run the examples
    run_simple_survey()
    time.sleep(1)  # Add a small delay between experiments
    run_ab_test()

if __name__ == "__main__":
    main()
