#!/usr/bin/env python3
"""
Flu Shot A/B Test Script (Standard Personas Version)

This script runs an A/B test to compare the effectiveness of two messages:
1. Control: "Get your flu shot now! Will you get a flu shot?"
2. Social Proof: "78% of your neighborhood is protected through flushot. Get yours now to protect yourself from flu! Will you get a flu shot?"

The test measures the percentage of people who respond "Yes" vs "No" to each message.
"""

import os
import logging
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from selfplay.socialsim import PersonaHubDB, ExperimentRunner, ResultsCollector

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_flushot_ab_test():
    """Run the flu shot A/B test experiment."""
    logger.info("Running flu shot A/B test experiment with standard personas...")
    
    # Load personas with lazy loading to optimize performance
    # Use standard personas instead of elite personas
    logger.info("Loading standard personas...")
    persona_db = PersonaHubDB(use_elite=False, use_standard=True, max_personas=100)
    
    # Define control and test questions
    control_question = "Get your flu shot now! Will you get a flu shot?"
    test_question = "78% of your neighborhood is protected through flushot. Get yours now to protect yourself from flu! Will you get a flu shot?"
    options = ["Yes", "No"]
    
    # Set number of personas for the test
    num_personas = 50  # Each persona will answer both questions
    
    logger.info(f"Running A/B test with {num_personas} total personas...")
    
    # Instead of using the built-in A/B test method, we'll run two separate surveys
    # with the same personas to implement a within-subjects design
    
    # First, run the control question survey
    logger.info(f"Running control question survey with {num_personas} personas...")
    control_results = run_survey_with_delay(
        persona_db=persona_db,
        question=control_question,
        options=options,
        n=num_personas,
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        question_type="multiple_choice",
        temperature=0.2,  # Reduced temperature as requested
        group_name="control"
    )
    
    # Add a delay between surveys to avoid rate limiting
    logger.info("Waiting 30 seconds before running the test question survey...")
    time.sleep(30)
    
    # Then, run the test question survey with the same personas
    logger.info(f"Running test question survey with the same {num_personas} personas...")
    test_results = run_survey_with_delay(
        persona_db=persona_db,
        question=test_question,
        options=options,
        n=num_personas,
        provider="aws",
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        question_type="multiple_choice",
        temperature=0.2,  # Reduced temperature as requested
        group_name="test",
        use_personas=control_results.get_personas()  # Use the same personas as the control group
    )
    
    # Combine the results
    results = combine_results(control_results, test_results)
    
    if results:
        # Print summary statistics
        logger.info("A/B test results:")
        stats = results.summary_statistics()
        
        # Calculate response rates by group
        control_responses = [r for r in results.responses if r.group == "control"]
        test_responses = [r for r in results.responses if r.group == "test"]
        
        control_yes = sum(1 for r in control_responses if r.response_value == "Yes")
        control_total = len(control_responses)
        control_yes_rate = control_yes / control_total * 100 if control_total > 0 else 0
        
        test_yes = sum(1 for r in test_responses if r.response_value == "Yes")
        test_total = len(test_responses)
        test_yes_rate = test_yes / test_total * 100 if test_total > 0 else 0
        
        # Print results
        print("\nControl Group (Standard Message):")
        print(f"  Yes: {control_yes}/{control_total} ({control_yes_rate:.1f}%)")
        print(f"  No: {control_total - control_yes}/{control_total} ({100 - control_yes_rate:.1f}%)")
        
        print("\nTest Group (Social Proof Message):")
        print(f"  Yes: {test_yes}/{test_total} ({test_yes_rate:.1f}%)")
        print(f"  No: {test_total - test_yes}/{test_total} ({100 - test_yes_rate:.1f}%)")
        
        # Calculate lift
        if control_yes_rate > 0:
            lift = (test_yes_rate - control_yes_rate) / control_yes_rate * 100
            print(f"\nLift from social proof: {lift:.1f}%")
        
        # Perform within-subjects analysis using the new method in ResultsCollector
        within_subjects_analysis = results.perform_within_subjects_analysis(
            group_column='group',
            persona_column='persona_id'
        )
        
        if within_subjects_analysis and 'significance_test' in within_subjects_analysis:
            significance_test = within_subjects_analysis['significance_test']
            if significance_test:
                print("\nMcNemar's Test Contingency Table:")
                contingency = significance_test['contingency_table']
                print(f"  Yes to both messages: {contingency['both_yes']}")
                print(f"  Yes to control, No to test: {contingency['group1_yes_group2_no']}")
                print(f"  No to control, Yes to test: {contingency['group1_no_group2_yes']}")
                print(f"  No to both messages: {contingency['both_no']}")
                
                test_name = significance_test['test']
                p_value = significance_test['p_value']
                
                if test_name == 'mcnemar_exact':
                    print(f"\nMcNemar's exact binomial test p-value: {p_value:.4f}")
                else:
                    test_stat = significance_test['test_statistic']
                    print(f"\nMcNemar's chi-square test statistic: {test_stat:.4f}")
                    print(f"McNemar's chi-square test p-value: {p_value:.4f}")
                
                # Interpret the result
                alpha = 0.05
                if p_value < alpha:
                    print(f"The difference is statistically significant (p < {alpha}).")
                else:
                    print(f"The difference is not statistically significant (p >= {alpha}).")
                
                # Print response changes
                changes = within_subjects_analysis['response_changes']
                print(f"\nResponse Changes:")
                print(f"  Total paired responses: {changes['total_paired_responses']}")
                print(f"  Changed responses: {changes['changed_responses']} ({changes['change_percentage']:.1f}%)")
        
        # Export results
        results.export_csv("standard_ab_test_results.csv")
        logger.info("Results exported to standard_ab_test_results.csv")
        
        # Create visualization
        create_visualization(control_yes_rate, test_yes_rate)
        
        # Return the results for further analysis if needed
        return results
    else:
        logger.error("A/B test experiment failed")
        return None

def create_visualization(control_yes_rate, test_yes_rate):
    """Create a bar chart visualization of the A/B test results."""
    try:
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        groups = ['Standard Message', 'Social Proof Message (78%)']
        yes_rates = [control_yes_rate, test_yes_rate]
        
        bars = plt.bar(groups, yes_rates, color=['#1f77b4', '#ff7f0e'])
        
        # Add labels and title
        plt.xlabel('Message Type')
        plt.ylabel('Percentage Responding "Yes"')
        plt.title('Effect of Social Proof on Flu Shot Acceptance (Standard Personas)')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Add grid lines for readability
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Set y-axis to start at 0 and end at 100
        plt.ylim(0, 100)
        
        # Save the figure
        plt.savefig('standard_flushot_ab_test_results.png')
        logger.info("Visualization saved to standard_flushot_ab_test_results.png")
        
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")

def run_survey_with_delay(persona_db, question, options, n, provider, model, 
                         question_type, temperature, group_name, use_personas=None):
    """
    Run a survey with a delay between API calls to avoid throttling.
    
    Args:
        persona_db: PersonaHubDB instance
        question: Question to ask
        options: Response options
        n: Number of personas to sample
        provider: LLM provider
        model: Model to use
        question_type: Type of question
        temperature: Temperature for LLM generation
        group_name: Group name for the responses
        use_personas: Optional list of personas to use (instead of sampling)
        
    Returns:
        ResultsCollector: Results collector with the survey results
    """
    # Create experiment runner
    runner = ExperimentRunner(persona_db)
    
    # Sample personas if not provided
    if use_personas is None:
        logger.info(f"Sampling {n} personas...")
        personas = persona_db.sample(n=n)
    else:
        logger.info(f"Using {len(use_personas)} provided personas...")
        personas = use_personas
    
    if len(personas) == 0:
        logger.error("No personas available")
        return None
    
    # Set up experiment config
    experiment_config = {
        "type": "survey",
        "question": question,
        "options": options,
        "question_type": question_type,
        "n": len(personas),
        "provider": provider,
        "model": model,
        "temperature": temperature
    }
    
    # Initialize results collector
    results_collector = ResultsCollector(experiment_config)
    
    # Generate a unique survey ID
    import uuid
    import hashlib
    survey_id = str(uuid.uuid4())
    question_id = hashlib.md5(question.encode()).hexdigest()
    
    # Run the survey
    logger.info(f"Running survey with {len(personas)} personas...")
    
    try:
        from selfplay.provider_interface import get_provider
        
        llm_provider = get_provider(provider, model=model)
        
        for i, persona in enumerate(personas):
            logger.info(f"Processing persona {i+1}/{len(personas)}: {persona.id}")
            
            # Create prompt for the persona
            prompt = f"""
            You are the following person:
            {persona.description}
            
            Please answer the following question as this person would:
            
            Question: {question}
            
            Options:
            {', '.join(options)}
            
            Choose exactly one option from the list above. Respond with only the chosen option.
            """
            
            # Get response from LLM
            start_time = time.time()
            response = llm_provider.generate_response([
                {"role": "system", "content": "You are roleplaying as a specific person. Answer the question as that person would."},
                {"role": "user", "content": prompt}
            ], temperature=temperature)  # Use the specified temperature
            end_time = time.time()
            
            # Process response
            response = response.strip()
            
            # Extract the actual choice from longer responses
            processed_response = response
            if question_type == "multiple_choice":
                # Check if the response contains one of the options
                for option in options:
                    if option in response:
                        processed_response = option
                        break
            
            # Create survey response
            from selfplay.socialsim.experiment_runner import SurveyResponse
            survey_response = SurveyResponse()
            survey_response.survey_id = survey_id
            survey_response.question_id = question_id
            survey_response.question_text = question
            survey_response.question_type = question_type
            survey_response.question_options = options
            survey_response.persona_id = persona.id
            survey_response.persona_attributes = persona.to_dict()
            survey_response.response_value = processed_response
            survey_response.response_time = end_time - start_time
            survey_response.timestamp = time.time()
            survey_response.group = group_name
            
            # Add to results collector
            results_collector.add_response(survey_response)
            
            # Add a delay between API calls to avoid throttling
            logger.info(f"Waiting 10 seconds before next API call...")
            time.sleep(10)
        
        # Finalize results collection
        results_collector.finalize()
        
        # Store the personas used for this survey in the results collector
        setattr(results_collector, 'personas', personas)
        
        return results_collector
    
    except Exception as e:
        logger.error(f"Error running survey: {str(e)}")
        return None

# Add a method to ResultsCollector to get personas
def get_personas(self):
    """Get the personas used in this survey."""
    return getattr(self, 'personas', [])

# Monkey patch the ResultsCollector class to add the get_personas method
ResultsCollector.get_personas = get_personas

def combine_results(control_results, test_results):
    """
    Combine results from control and test surveys.
    
    Args:
        control_results: Results collector for control group
        test_results: Results collector for test group
        
    Returns:
        ResultsCollector: Combined results collector
    """
    if control_results is None or test_results is None:
        logger.error("Cannot combine results: one or both result sets are None")
        return None
    
    # Extract question information from the first response in each result set
    control_question = ""
    test_question = ""
    options = []
    question_type = "multiple_choice"
    
    if control_results.responses:
        control_question = control_results.responses[0].question_text
        options = control_results.responses[0].question_options
        question_type = control_results.responses[0].question_type
    
    if test_results.responses:
        test_question = test_results.responses[0].question_text
    
    # Create a new results collector with combined config
    combined_config = {
        "type": "ab_test",
        "control_question": control_question,
        "test_question": test_question,
        "options": options,
        "question_type": question_type,
    }
    
    combined_results = ResultsCollector(combined_config)
    
    # Add all responses from both collectors
    for response in control_results.responses:
        combined_results.add_response(response)
    
    for response in test_results.responses:
        combined_results.add_response(response)
    
    # Finalize the combined results
    combined_results.finalize()
    
    return combined_results

def main():
    """Main function."""
    # Check if AWS credentials are available
    if not os.path.exists(os.path.expanduser("~/.aws/credentials")):
        logger.warning("AWS credentials file not found at ~/.aws/credentials")
        logger.warning("Make sure AWS credentials are properly configured")
    
    # Run the A/B test
    results = run_flushot_ab_test()
    
    if results:
        logger.info("A/B test completed successfully!")
        
        # Additional analysis could be added here
        df = results.get_dataframe()
        
        # Check if there are any demographic patterns
        if 'persona_gender' in df.columns:
            logger.info("Gender distribution of respondents:")
            for group in ['control', 'test']:
                group_df = df[df['group'] == group]
                for gender in group_df['persona_gender'].unique():
                    if pd.notna(gender):
                        gender_df = group_df[group_df['persona_gender'] == gender]
                        yes_count = len(gender_df[gender_df['response_value'] == 'Yes'])
                        yes_percentage = yes_count / len(gender_df) * 100 if len(gender_df) > 0 else 0
                        print(f"  {group.title()} group - {gender}: {yes_percentage:.1f}% responded Yes ({yes_count}/{len(gender_df)})")

if __name__ == "__main__":
    # Import matplotlib here to avoid import error if not creating visualizations
    import matplotlib.pyplot as plt
    main()
