#!/usr/bin/env python3
"""
Flu Shot Multivariate Messaging Experiment (Medium Version)

This script runs a multivariate experiment to compare the effectiveness of 7 different
message variants for encouraging flu shot uptake with 10 personas (instead of the full 50).
"""

import os
import logging
import time
import random
import uuid
import hashlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from selfplay.socialsim import PersonaHubDB, ExperimentRunner, ResultsCollector

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define message variants
MESSAGE_VARIANTS = [
    {
        "id": 1,
        "name": "Control (Direct)",
        "principle": "Direct Request",
        "text": "Get your flu shot now! Will you get a flu shot?"
    },
    {
        "id": 2,
        "name": "Social Proof",
        "principle": "Social Proof",
        "text": "78% of people in your community have already gotten their flu shot this season. Will you get a flu shot?"
    },
    {
        "id": 3,
        "name": "Authority",
        "principle": "Authority",
        "text": "Medical experts at the CDC and WHO strongly recommend getting a flu shot this season. Will you get a flu shot?"
    },
    {
        "id": 4,
        "name": "Scarcity/Urgency",
        "principle": "Scarcity",
        "text": "Flu vaccine supplies are limited this year and appointments are filling up quickly. Will you get a flu shot?"
    },
    {
        "id": 5,
        "name": "Personal Benefit",
        "principle": "Self-Interest",
        "text": "Getting a flu shot reduces your personal risk of illness by up to 60% and can prevent severe symptoms even if you do catch the flu. Will you get a flu shot?"
    },
    {
        "id": 6,
        "name": "Fear Appeal",
        "principle": "Fear",
        "text": "Without a flu shot, you're at higher risk of hospitalization or even death from influenza, which kills thousands each year. Will you get a flu shot?"
    },
    {
        "id": 7,
        "name": "Reciprocity/Community Benefit",
        "principle": "Altruism",
        "text": "By getting a flu shot, you help protect vulnerable people in your community who cannot get vaccinated, such as infants and those with compromised immune systems. Will you get a flu shot?"
    }
]

def run_multivariate_experiment(num_personas=10, use_standard_personas=True):
    """
    Run the multivariate flu shot messaging experiment.
    
    Args:
        num_personas (int): Number of personas to sample
        use_standard_personas (bool): Whether to use standard personas instead of elite personas
        
    Returns:
        pd.DataFrame: DataFrame containing all responses
    """
    logger.info(f"Running multivariate flu shot messaging experiment with {num_personas} personas...")
    
    # Create a unique session ID
    session_id = str(uuid.uuid4())
    
    # Load personas with lazy loading to optimize performance
    logger.info("Loading personas...")
    persona_db = PersonaHubDB(
        use_elite=not use_standard_personas, 
        use_standard=use_standard_personas, 
        max_personas=num_personas * 2  # Load extra for filtering
    )
    
    # Sample personas
    logger.info(f"Sampling {num_personas} personas...")
    personas = persona_db.sample(n=num_personas)
    
    if len(personas) < num_personas:
        logger.warning(f"Could only sample {len(personas)} personas, fewer than requested {num_personas}")
    
    # Create experiment runner
    runner = ExperimentRunner(persona_db)
    
    # Common response options
    options = ["Yes", "No"]
    
    # Initialize a list to store all responses
    all_responses = []
    
    # For each persona, randomize the order of message variants
    for i, persona in enumerate(personas):
        logger.info(f"Processing persona {i+1}/{len(personas)}: {persona.id}")
        
        # Randomize message order for this persona
        message_order = random.sample(MESSAGE_VARIANTS, len(MESSAGE_VARIANTS))
        
        # Process each message variant for this persona
        for order_idx, message in enumerate(message_order):
            logger.info(f"  Testing message variant {message['id']}: {message['name']}")
            
            # Create a unique survey ID for this message variant
            survey_id = f"{session_id}_{message['id']}"
            question_id = hashlib.md5(message['text'].encode()).hexdigest()
            
            # Create prompt for the persona
            prompt = f"""
            You are the following person:
            {persona.description}
            
            Please answer the following question as this person would:
            
            Question: {message['text']}
            
            Options:
            {', '.join(options)}
            
            Choose exactly one option from the list above. Respond with only the chosen option.
            """
            
            # Get response from LLM
            try:
                from selfplay.provider_interface import get_provider
                
                # Use AWS Bedrock with Claude 3.7 Sonnet
                provider = "aws"
                model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
                temperature = 0.2  # Low temperature for consistent responses
                
                llm_provider = get_provider(provider, model=model)
                
                start_time = time.time()
                response = llm_provider.generate_response([
                    {"role": "system", "content": "You are roleplaying as a specific person. Answer the question as that person would."},
                    {"role": "user", "content": prompt}
                ], temperature=temperature)
                end_time = time.time()
                
                # Process response
                raw_response = response.strip()
                
                # Extract the actual choice from longer responses
                processed_response = raw_response
                for option in options:
                    if option in raw_response:
                        processed_response = option
                        break
                
                # Create response record
                response_record = {
                    'session_id': session_id,
                    'timestamp': time.time(),
                    'persona_id': persona.id,
                    'persona_description': persona.description,
                    'message_id': message['id'],
                    'message_name': message['name'],
                    'message_principle': message['principle'],
                    'message_text': message['text'],
                    'message_order': order_idx + 1,
                    'response_value': processed_response,
                    'response_time': end_time - start_time,
                    'raw_response': raw_response
                }
                
                # Add all available persona attributes
                persona_dict = persona.to_dict()
                for key, value in persona_dict.items():
                    if key != 'description' and not isinstance(value, (dict, list)):
                        response_record[f'persona_{key}'] = value
                
                # Add to responses list
                all_responses.append(response_record)
                
                logger.info(f"    Response: {processed_response}")
                
                # Add a delay between API calls to avoid throttling
                logger.info(f"    Waiting 10 seconds before next API call...")
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error processing message variant {message['id']} for persona {persona.id}: {str(e)}")
        
        # Add a longer delay between personas
        if i < len(personas) - 1:
            logger.info(f"Waiting 30 seconds before processing next persona...")
            time.sleep(30)
    
    # Convert responses to DataFrame
    df = pd.DataFrame(all_responses)
    
    # Export to CSV
    csv_filename = f"flushot_multivariate_medium_results_{session_id[:8]}.csv"
    df.to_csv(csv_filename, index=False)
    logger.info(f"Exported {len(df)} responses to {csv_filename}")
    
    return df

def analyze_results(df):
    """
    Analyze the results of the multivariate experiment.
    
    Args:
        df (pd.DataFrame): DataFrame containing all responses
        
    Returns:
        dict: Dictionary containing analysis results
    """
    logger.info("Analyzing results...")
    
    # Calculate response rates by message variant
    response_rates = {}
    for message in MESSAGE_VARIANTS:
        message_df = df[df['message_id'] == message['id']]
        yes_count = len(message_df[message_df['response_value'] == 'Yes'])
        total_count = len(message_df)
        yes_rate = yes_count / total_count * 100 if total_count > 0 else 0
        
        response_rates[message['id']] = {
            'name': message['name'],
            'principle': message['principle'],
            'yes_count': yes_count,
            'total_count': total_count,
            'yes_rate': yes_rate
        }
    
    # Print response rates
    print("\nResponse Rates by Message Variant:")
    for message_id, stats in sorted(response_rates.items()):
        print(f"  {stats['name']} ({stats['principle']}): {stats['yes_count']}/{stats['total_count']} ({stats['yes_rate']:.1f}%)")
    
    # Perform Cochran's Q test for overall differences
    try:
        # Reshape data for Cochran's Q test
        pivot = df.pivot_table(
            index='persona_id',
            columns='message_id',
            values='response_value',
            aggfunc='first'
        )
        
        # Convert to binary (1 for "Yes", 0 for "No")
        # Use DataFrame.map instead of the deprecated DataFrame.applymap
        binary_pivot = pivot.copy()
        for col in binary_pivot.columns:
            binary_pivot[col] = binary_pivot[col].map(lambda x: 1 if x == 'Yes' else 0)
        
        # Implement our own Cochran's Q test since it might not be available in all scipy versions
        # Based on the formula: Q = (k-1) * (k * sum(Tj^2) - T.^2) / (k * R - sum(Ri^2))
        # where k is number of treatments, Tj is column sums, T. is grand sum, Ri is row sums
        
        # Check if we have complete data for all personas
        complete_data = binary_pivot.dropna()
        if len(complete_data) < len(binary_pivot):
            logger.warning(f"Dropping {len(binary_pivot) - len(complete_data)} personas with incomplete data for Cochran's Q test")
        
        if len(complete_data) >= 3:  # Need at least 3 personas for the test
            try:
                # Try to import cochrans_q if available
                try:
                    from scipy.stats import cochrans_q
                    q_stat, p_value = cochrans_q(complete_data.values)
                except ImportError:
                    # Implement our own Cochran's Q test
                    data = complete_data.values
                    k = data.shape[1]  # Number of treatments
                    n = data.shape[0]  # Number of subjects
                    
                    # Calculate column sums (Tj)
                    col_sums = data.sum(axis=0)
                    
                    # Calculate row sums (Ri)
                    row_sums = data.sum(axis=1)
                    
                    # Calculate grand sum (T.)
                    grand_sum = data.sum()
                    
                    # Calculate Q statistic
                    q_stat = (k - 1) * (k * np.sum(col_sums**2) - grand_sum**2) / (k * grand_sum - np.sum(row_sums**2))
                    
                    # Calculate p-value (Q follows chi-square with k-1 degrees of freedom)
                    from scipy import stats as scipy_stats
                    p_value = scipy_stats.chi2.sf(q_stat, k - 1)
                
                print(f"\nCochran's Q Test:")
                print(f"  Q statistic: {q_stat:.4f}")
                print(f"  p-value: {p_value:.4f}")
                print(f"  Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
            except Exception as e:
                logger.error(f"Error performing Cochran's Q test: {str(e)}")
            
            # If significant, perform post-hoc pairwise McNemar's tests
            if p_value < 0.05:
                print("\nPost-hoc Pairwise McNemar's Tests:")
                
                # Number of pairwise comparisons
                num_comparisons = len(MESSAGE_VARIANTS) * (len(MESSAGE_VARIANTS) - 1) // 2
                
                # Bonferroni-corrected alpha
                alpha_corrected = 0.05 / num_comparisons
                print(f"  Bonferroni-corrected α: {alpha_corrected:.5f}")
                
                # Perform pairwise tests
                significant_pairs = []
                
                for i in range(len(MESSAGE_VARIANTS)):
                    for j in range(i+1, len(MESSAGE_VARIANTS)):
                        message1_id = MESSAGE_VARIANTS[i]['id']
                        message2_id = MESSAGE_VARIANTS[j]['id']
                        
                        # Extract binary responses for the two messages
                        responses1 = binary_pivot[message1_id]
                        responses2 = binary_pivot[message2_id]
                        
                        # Count the different response patterns
                        both_yes = sum((responses1 == 1) & (responses2 == 1))
                        message1_yes_message2_no = sum((responses1 == 1) & (responses2 == 0))
                        message1_no_message2_yes = sum((responses1 == 0) & (responses2 == 1))
                        both_no = sum((responses1 == 0) & (responses2 == 0))
                        
                        # Only perform test if there are discordant pairs
                        if message1_yes_message2_no + message1_no_message2_yes > 0:
                            # Use exact binomial test for small samples
                            if message1_yes_message2_no + message1_no_message2_yes < 25:
                                try:
                                    # Try the newer scipy.stats.binomtest first (scipy >= 1.7.0)
                                    try:
                                        from scipy.stats import binomtest
                                        result = binomtest(message1_yes_message2_no, message1_yes_message2_no + message1_no_message2_yes, p=0.5)
                                        p_value = result.pvalue
                                        test_name = "exact binomial test"
                                    except ImportError:
                                        # Fall back to the older binom_test for older scipy versions
                                        p_value = stats.binom_test(message1_yes_message2_no, message1_yes_message2_no + message1_no_message2_yes, p=0.5)
                                        test_name = "exact binomial test"
                                except Exception as e:
                                    logger.warning(f"Could not perform exact binomial test: {str(e)}")
                                    # Fall back to chi-square approximation
                                    test_stat = (message1_yes_message2_no - message1_no_message2_yes)**2 / (message1_yes_message2_no + message1_no_message2_yes)
                                    p_value = stats.chi2.sf(test_stat, 1)
                                    test_name = "chi-square approximation"
                            else:
                                # Use chi-square approximation for larger samples
                                test_stat = (message1_yes_message2_no - message1_no_message2_yes)**2 / (message1_yes_message2_no + message1_no_message2_yes)
                                p_value = stats.chi2.sf(test_stat, 1)
                                test_name = "chi-square approximation"
                            
                            # Check if significant after Bonferroni correction
                            is_significant = p_value < alpha_corrected
                            
                            if is_significant:
                                significant_pairs.append((message1_id, message2_id))
                            
                            message1_name = next(m['name'] for m in MESSAGE_VARIANTS if m['id'] == message1_id)
                            message2_name = next(m['name'] for m in MESSAGE_VARIANTS if m['id'] == message2_id)
                            
                            print(f"  {message1_name} vs {message2_name}:")
                            print(f"    Both Yes: {both_yes}, {message1_name} Yes/{message2_name} No: {message1_yes_message2_no}, {message1_name} No/{message2_name} Yes: {message1_no_message2_yes}, Both No: {both_no}")
                            print(f"    p-value ({test_name}): {p_value:.4f}")
                            print(f"    Significant after Bonferroni correction: {'Yes' if is_significant else 'No'}")
                
                if not significant_pairs:
                    print("  No significant pairwise differences after Bonferroni correction")
        else:
            logger.warning("Not enough complete data for Cochran's Q test")
    except Exception as e:
        logger.error(f"Error performing Cochran's Q test: {str(e)}")
    
    # Analyze response patterns by persona attributes
    try:
        # Check if we have gender data
        if 'persona_gender' in df.columns:
            print("\nResponse Rates by Gender:")
            
            # Get unique genders
            genders = df['persona_gender'].dropna().unique()
            
            for gender in genders:
                print(f"\n  Gender: {gender}")
                
                for message in MESSAGE_VARIANTS:
                    gender_message_df = df[(df['persona_gender'] == gender) & (df['message_id'] == message['id'])]
                    yes_count = len(gender_message_df[gender_message_df['response_value'] == 'Yes'])
                    total_count = len(gender_message_df)
                    yes_rate = yes_count / total_count * 100 if total_count > 0 else 0
                    
                    print(f"    {message['name']}: {yes_count}/{total_count} ({yes_rate:.1f}%)")
    except Exception as e:
        logger.warning(f"Error analyzing response patterns by gender: {str(e)}")
    
    # Return response rates
    return response_rates

def create_visualization(response_rates, filename="flushot_multivariate_medium_results.png"):
    """
    Create a bar chart visualization of the response rates.
    
    Args:
        response_rates (dict): Dictionary containing response rates by message variant
        filename (str): Filename to save the visualization
    """
    try:
        plt.figure(figsize=(12, 8))
        
        # Extract data for plotting
        message_ids = []
        message_names = []
        yes_rates = []
        
        for message_id, stats in sorted(response_rates.items()):
            message_ids.append(message_id)
            message_names.append(f"{message_id}. {stats['name']}")
            yes_rates.append(stats['yes_rate'])
        
        # Create bar chart
        bars = plt.bar(message_names, yes_rates, color=plt.cm.tab10(range(len(message_ids))))
        
        # Add labels and title
        plt.xlabel('Message Variant')
        plt.ylabel('Percentage Responding "Yes"')
        plt.title('Effect of Different Message Framings on Flu Shot Acceptance')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Add grid lines for readability
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Set y-axis to start at 0 and end at 100
        plt.ylim(0, 100)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the figure
        plt.savefig(filename)
        logger.info(f"Visualization saved to {filename}")
        
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")

def main():
    """Main function."""
    # Check if AWS credentials are available
    if not os.path.exists(os.path.expanduser("~/.aws/credentials")):
        logger.warning("AWS credentials file not found at ~/.aws/credentials")
        logger.warning("Make sure AWS credentials are properly configured")
    
    # Run the multivariate experiment
    df = run_multivariate_experiment(num_personas=10, use_standard_personas=True)
    
    if len(df) > 0:
        logger.info("Multivariate experiment completed successfully!")
        
        # Analyze results
        response_rates = analyze_results(df)
        
        # Create visualization
        create_visualization(response_rates)
    else:
        logger.error("Multivariate experiment failed")

if __name__ == "__main__":
    main()
