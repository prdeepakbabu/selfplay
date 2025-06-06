"""
Experiment runner for SocialSim.

This module defines the ExperimentRunner class, which manages the execution of
social science experiments, and the SurveyResponse class, which represents a
single response to a survey question.
"""

import time
import logging
import hashlib
import uuid
from typing import List, Dict, Any, Optional, Union

from .persona import Persona
from .results_collector import ResultsCollector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SurveyResponse:
    """
    A class representing a single response to a survey question.
    
    This class stores all relevant information about a survey response,
    including the question, the persona, and the response value.
    """
    
    def __init__(self):
        """Initialize a new SurveyResponse instance with default attribute values."""
        # Survey metadata
        self.survey_id = None
        self.survey_name = None
        self.survey_description = None
        self.timestamp = None
        self.experiment_type = None  # "standard", "ab_test", "multi_variant", etc.
        
        # Question data
        self.question_id = None
        self.question_text = None
        self.question_type = None  # "multiple_choice", "likert", "open_ended", etc.
        self.question_options = []  # List of possible options for multiple choice
        self.question_variant = None  # For A/B testing, which variant was shown
        
        # Persona data
        self.persona_id = None
        self.persona_attributes = {}  # All demographic and psychographic attributes
        
        # Response data
        self.response_value = None  # The actual response (option selected, text entered, etc.)
        self.response_time = None  # Simulated response time
        self.confidence_score = None  # How confident the model is in this response
        
        # Experimental grouping
        self.group = None  # "control", "treatment_a", "treatment_b", etc.
        self.condition = None  # Experimental condition if applicable
    
    def __str__(self):
        """Return a string representation of the survey response."""
        return f"Response from {self.persona_id}: {self.response_value}"

class ExperimentRunner:
    """
    A class for running social science experiments.
    
    This class manages the execution of experiments, including sampling personas,
    presenting questions, collecting responses, and analyzing results.
    """
    
    def __init__(self, persona_db):
        """
        Initialize the experiment runner.
        
        Args:
            persona_db: PersonaDB instance
        """
        self.persona_db = persona_db
        self.results_collector = None
    
    def run_survey(self, question, options, n=100, stratify_by=None, filter_by=None, 
                   provider="azure", model=None, question_type="multiple_choice"):
        """
        Run a survey experiment.
        
        Args:
            question (str): The question to ask
            options (list): List of response options
            n (int): Number of personas to sample
            stratify_by (str): Attribute to stratify by
            filter_by (dict): Dict of attributes to filter by
            provider (str): LLM provider to use
            model (str): Model to use
            question_type (str): Type of question ("multiple_choice", "likert", "open_ended", etc.)
            
        Returns:
            ResultsCollector: Results collector with the experiment results
        """
        # Sample personas
        logger.info(f"Sampling {n} personas...")
        personas = self.persona_db.sample(n=n, stratify_by=stratify_by, filter_by=filter_by)
        
        if len(personas) == 0:
            logger.error("No personas match the specified criteria")
            return None
        
        logger.info(f"Sampled {len(personas)} personas")
        
        # Set up experiment config
        experiment_config = {
            "type": "survey",
            "question": question,
            "options": options,
            "question_type": question_type,
            "n": len(personas),
            "stratify_by": stratify_by,
            "filter_by": filter_by,
            "provider": provider,
            "model": model
        }
        
        # Initialize results collector
        self.results_collector = ResultsCollector(experiment_config)
        
        # Generate a unique survey ID
        survey_id = str(uuid.uuid4())
        
        # Generate a question ID based on the question text
        question_id = hashlib.md5(question.encode()).hexdigest()
        
        # Run the experiment
        logger.info(f"Running survey experiment with {len(personas)} personas...")
        
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
                ])
                end_time = time.time()
                
                # Process response
                response = response.strip()
                
                # Extract the actual choice (Yes/No) from longer responses
                processed_response = response
                if question_type == "multiple_choice":
                    # Check if the response contains one of the options
                    for option in options:
                        if option in response:
                            processed_response = option
                            break
                
                # Create survey response
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
                
                # Add to results collector
                self.results_collector.add_response(survey_response)
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.1)
            
            # Finalize results collection
            self.results_collector.finalize()
            
            return self.results_collector
        
        except Exception as e:
            logger.error(f"Error running experiment: {str(e)}")
            return None
    
    @classmethod
    def ab_test(cls, persona_db, control_question, test_question, options, n=100, 
                stratify_by=None, filter_by=None, provider="azure", model=None, 
                question_type="multiple_choice"):
        """
        Run an A/B test experiment.
        
        Args:
            persona_db: PersonaDB instance
            control_question (str): Question for the control group
            test_question (str): Question for the test group
            options (list): List of response options
            n (int): Number of personas to sample (total)
            stratify_by (str): Attribute to stratify by
            filter_by (dict): Dict of attributes to filter by
            provider (str): LLM provider to use
            model (str): Model to use
            question_type (str): Type of question
            
        Returns:
            ResultsCollector: Results collector with the experiment results
        """
        # Create experiment runner
        runner = cls(persona_db)
        
        # Sample personas
        logger.info(f"Sampling {n} personas for A/B test...")
        personas = persona_db.sample(n=n, stratify_by=stratify_by, filter_by=filter_by)
        
        if len(personas) == 0:
            logger.error("No personas match the specified criteria")
            return None
        
        logger.info(f"Sampled {len(personas)} personas")
        
        # Split personas into control and test groups
        import random
        random.shuffle(personas)
        midpoint = len(personas) // 2
        control_personas = personas[:midpoint]
        test_personas = personas[midpoint:]
        
        logger.info(f"Control group: {len(control_personas)} personas")
        logger.info(f"Test group: {len(test_personas)} personas")
        
        # Set up experiment config
        experiment_config = {
            "type": "ab_test",
            "control_question": control_question,
            "test_question": test_question,
            "options": options,
            "question_type": question_type,
            "n_control": len(control_personas),
            "n_test": len(test_personas),
            "stratify_by": stratify_by,
            "filter_by": filter_by,
            "provider": provider,
            "model": model
        }
        
        # Initialize results collector
        runner.results_collector = ResultsCollector(experiment_config)
        
        # Generate a unique survey ID
        survey_id = str(uuid.uuid4())
        
        # Generate question IDs
        control_question_id = hashlib.md5(control_question.encode()).hexdigest()
        test_question_id = hashlib.md5(test_question.encode()).hexdigest()
        
        # Run the experiment
        logger.info("Running A/B test experiment...")
        
        try:
            from selfplay.provider_interface import get_provider
            
            llm_provider = get_provider(provider, model=model)
            
            # Process control group
            logger.info("Processing control group...")
            for i, persona in enumerate(control_personas):
                logger.info(f"Processing control persona {i+1}/{len(control_personas)}: {persona.id}")
                
                # Create prompt for the persona
                prompt = f"""
                You are the following person:
                {persona.description}
                
                Please answer the following question as this person would:
                
                Question: {control_question}
                
                Options:
                {', '.join(options)}
                
                Choose exactly one option from the list above. Respond with only the chosen option.
                """
                
                # Get response from LLM
                start_time = time.time()
                response = llm_provider.generate_response([
                    {"role": "system", "content": "You are roleplaying as a specific person. Answer the question as that person would."},
                    {"role": "user", "content": prompt}
                ])
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
                survey_response = SurveyResponse()
                survey_response.survey_id = survey_id
                survey_response.question_id = control_question_id
                survey_response.question_text = control_question
                survey_response.question_type = question_type
                survey_response.question_options = options
                survey_response.question_variant = "control"
                survey_response.persona_id = persona.id
                survey_response.persona_attributes = persona.to_dict()
                survey_response.response_value = processed_response
                survey_response.response_time = end_time - start_time
                survey_response.timestamp = time.time()
                survey_response.group = "control"
                
                # Add to results collector
                runner.results_collector.add_response(survey_response)
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.1)
            
            # Process test group
            logger.info("Processing test group...")
            for i, persona in enumerate(test_personas):
                logger.info(f"Processing test persona {i+1}/{len(test_personas)}: {persona.id}")
                
                # Create prompt for the persona
                prompt = f"""
                You are the following person:
                {persona.description}
                
                Please answer the following question as this person would:
                
                Question: {test_question}
                
                Options:
                {', '.join(options)}
                
                Choose exactly one option from the list above. Respond with only the chosen option.
                """
                
                # Get response from LLM
                start_time = time.time()
                response = llm_provider.generate_response([
                    {"role": "system", "content": "You are roleplaying as a specific person. Answer the question as that person would."},
                    {"role": "user", "content": prompt}
                ])
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
                survey_response = SurveyResponse()
                survey_response.survey_id = survey_id
                survey_response.question_id = test_question_id
                survey_response.question_text = test_question
                survey_response.question_type = question_type
                survey_response.question_options = options
                survey_response.question_variant = "test"
                survey_response.persona_id = persona.id
                survey_response.persona_attributes = persona.to_dict()
                survey_response.response_value = processed_response
                survey_response.response_time = end_time - start_time
                survey_response.timestamp = time.time()
                survey_response.group = "test"
                
                # Add to results collector
                runner.results_collector.add_response(survey_response)
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.1)
            
            # Finalize results collection
            runner.results_collector.finalize()
            
            return runner.results_collector
        
        except Exception as e:
            logger.error(f"Error running A/B test experiment: {str(e)}")
            return None
    
    @classmethod
    def multi_variant_test(cls, persona_db, base_question, variants, options, n=100, 
                          stratify_by=None, filter_by=None, provider="azure", model=None, 
                          question_type="multiple_choice"):
        """
        Run a multi-variant test experiment.
        
        Args:
            persona_db: PersonaDB instance
            base_question (str): Base question text
            variants (dict): Dict of variant names to variant-specific text
            options (list): List of response options
            n (int): Number of personas per variant
            stratify_by (str): Attribute to stratify by
            filter_by (dict): Dict of attributes to filter by
            provider (str): LLM provider to use
            model (str): Model to use
            question_type (str): Type of question
            
        Returns:
            ResultsCollector: Results collector with the experiment results
        """
        # Create experiment runner
        runner = cls(persona_db)
        
        # Calculate total number of personas needed
        total_personas = n * len(variants)
        
        # Sample personas
        logger.info(f"Sampling {total_personas} personas for multi-variant test...")
        personas = persona_db.sample(n=total_personas, stratify_by=stratify_by, filter_by=filter_by)
        
        if len(personas) == 0:
            logger.error("No personas match the specified criteria")
            return None
        
        logger.info(f"Sampled {len(personas)} personas")
        
        # Split personas into variant groups
        import random
        random.shuffle(personas)
        personas_per_variant = len(personas) // len(variants)
        variant_personas = {}
        
        for i, variant_name in enumerate(variants.keys()):
            start_idx = i * personas_per_variant
            end_idx = start_idx + personas_per_variant if i < len(variants) - 1 else len(personas)
            variant_personas[variant_name] = personas[start_idx:end_idx]
            logger.info(f"Variant '{variant_name}': {len(variant_personas[variant_name])} personas")
        
        # Set up experiment config
        experiment_config = {
            "type": "multi_variant_test",
            "base_question": base_question,
            "variants": variants,
            "options": options,
            "question_type": question_type,
            "personas_per_variant": personas_per_variant,
            "stratify_by": stratify_by,
            "filter_by": filter_by,
            "provider": provider,
            "model": model
        }
        
        # Initialize results collector
        runner.results_collector = ResultsCollector(experiment_config)
        
        # Generate a unique survey ID
        survey_id = str(uuid.uuid4())
        
        # Run the experiment
        logger.info("Running multi-variant test experiment...")
        
        try:
            from selfplay.provider_interface import get_provider
            
            llm_provider = get_provider(provider, model=model)
            
            # Process each variant
            for variant_name, variant_text in variants.items():
                logger.info(f"Processing variant '{variant_name}'...")
                
                # Construct full question
                full_question = f"{base_question} {variant_text}"
                
                # Generate question ID
                question_id = hashlib.md5(full_question.encode()).hexdigest()
                
                for i, persona in enumerate(variant_personas[variant_name]):
                    logger.info(f"Processing persona {i+1}/{len(variant_personas[variant_name])}: {persona.id}")
                    
                    # Create prompt for the persona
                    prompt = f"""
                    You are the following person:
                    {persona.description}
                    
                    Please answer the following question as this person would:
                    
                    Question: {full_question}
                    
                    Options:
                    {', '.join(options)}
                    
                    Choose exactly one option from the list above. Respond with only the chosen option.
                    """
                    
                    # Get response from LLM
                    start_time = time.time()
                    response = llm_provider.generate_response([
                        {"role": "system", "content": "You are roleplaying as a specific person. Answer the question as that person would."},
                        {"role": "user", "content": prompt}
                    ])
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
                    survey_response = SurveyResponse()
                    survey_response.survey_id = survey_id
                    survey_response.question_id = question_id
                    survey_response.question_text = full_question
                    survey_response.question_type = question_type
                    survey_response.question_options = options
                    survey_response.question_variant = variant_name
                    survey_response.persona_id = persona.id
                    survey_response.persona_attributes = persona.to_dict()
                    survey_response.response_value = processed_response
                    survey_response.response_time = end_time - start_time
                    survey_response.timestamp = time.time()
                    survey_response.group = variant_name
                    
                    # Add to results collector
                    runner.results_collector.add_response(survey_response)
                    
                    # Add a small delay to avoid rate limiting
                    time.sleep(0.1)
            
            # Finalize results collection
            runner.results_collector.finalize()
            
            return runner.results_collector
        
        except Exception as e:
            logger.error(f"Error running multi-variant test experiment: {str(e)}")
            return None
