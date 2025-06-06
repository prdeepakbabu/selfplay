#!/usr/bin/env python3
"""
Flu Shot Survey Script

This script runs a survey to test the effectiveness of the social proof message:
"4 of your neighbors have got a flushot. get yours now!"

The survey samples personas from the PersonaHub dataset and measures the percentage 
of people who respond "Yes" vs "No" to getting a flu shot after hearing this message.
"""

import os
import logging
import time
from selfplay.socialsim import PersonaHubDB, ExperimentRunner

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_flushot_survey():
    """Run the flu shot survey experiment."""
    logger.info("Running flu shot survey experiment...")
    
    # Load personas with lazy loading to optimize performance
    logger.info("Loading personas...")
    persona_db = PersonaHubDB(use_elite=True, use_standard=False, max_personas=100)
    
    # Create experiment runner
    runner = ExperimentRunner(persona_db)
    
    # Define survey question and options
    question = "4 of your neighbors have got a flushot. get yours now! Will you get a flu shot?"
    options = ["Yes", "No"]
    
    # Set a smaller number of personas for the test to avoid rate limiting
    num_personas = 10  # Reduced from 50 to avoid throttling
    
    logger.info(f"Running survey with {num_personas} personas...")
    # Run the survey with a smaller number of personas
    results = runner.run_survey(
        question=question,
        options=options,
        n=num_personas,  # Reduced number of personas
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
        results.export_csv("flushot_survey_results.csv")
        logger.info("Results exported to flushot_survey_results.csv")
        
        # Return the results for further analysis if needed
        return results
    else:
        logger.error("Survey experiment failed")
        return None

def main():
    """Main function."""
    # Check if AWS credentials are available
    if not os.path.exists(os.path.expanduser("~/.aws/credentials")):
        logger.warning("AWS credentials file not found at ~/.aws/credentials")
        logger.warning("Make sure AWS credentials are properly configured")
    
    # Run the survey
    results = run_flushot_survey()
    
    if results:
        logger.info("Survey completed successfully!")
        
        # Additional analysis could be added here
        
        # Print a summary of the results
        df = results.get_dataframe()
        
        # Check if there are any demographic patterns
        if 'persona_age' in df.columns:
            logger.info("Age distribution of respondents:")
            age_groups = {
                '18-30': (18, 30),
                '31-45': (31, 45),
                '46-60': (46, 60),
                '61+': (61, 200)
            }
            
            for group_name, (min_age, max_age) in age_groups.items():
                group_df = df[(df['persona_age'] >= min_age) & (df['persona_age'] <= max_age)]
                if len(group_df) > 0:
                    yes_count = len(group_df[group_df['response_value'] == 'Yes'])
                    yes_percentage = yes_count / len(group_df) * 100
                    print(f"  Age {group_name}: {yes_percentage:.1f}% responded Yes ({yes_count}/{len(group_df)})")
        
        if 'persona_gender' in df.columns:
            logger.info("Gender distribution of respondents:")
            for gender in df['persona_gender'].unique():
                if pd.notna(gender):
                    gender_df = df[df['persona_gender'] == gender]
                    yes_count = len(gender_df[gender_df['response_value'] == 'Yes'])
                    yes_percentage = yes_count / len(gender_df) * 100
                    print(f"  {gender}: {yes_percentage:.1f}% responded Yes ({yes_count}/{len(gender_df)})")

if __name__ == "__main__":
    # Import pandas here to avoid import error if not analyzing demographic patterns
    import pandas as pd
    main()
