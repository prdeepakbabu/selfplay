"""
PersonaDB implementation for SocialSim.

This module defines the PersonaHubDB class, which manages a database of personas
from the PersonaHub dataset on Hugging Face.
"""

import random
import re
import json
import time
import logging
from typing import List, Dict, Any, Optional, Union
import pandas as pd

from .persona import Persona

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonaHubDB:
    """
    A class for managing a database of personas from the PersonaHub dataset.
    
    This class handles loading, processing, and sampling personas from the
    PersonaHub dataset on Hugging Face.
    """
    
    def __init__(self, use_elite=True, use_standard=True, cache_dir=None, max_personas=1000):
        """
        Initialize the PersonaHub database with lazy loading.
        
        Args:
            use_elite (bool): Whether to include elite_persona dataset
            use_standard (bool): Whether to include standard persona dataset
            cache_dir (str): Directory to cache the dataset
            max_personas (int): Maximum number of personas to load
        """
        self.personas = []
        self.max_personas = max_personas
        self.datasets = []
        
        try:
            from datasets import load_dataset
            
            # Set up dataset references but don't load data yet
            if use_elite:
                logger.info("Setting up elite_persona dataset reference...")
                self.datasets.append(("elite", load_dataset("proj-persona/PersonaHub", "elite_persona", 
                                                          streaming=True, cache_dir=cache_dir)))
                
            if use_standard:
                logger.info("Setting up persona dataset reference...")
                self.datasets.append(("standard", load_dataset("proj-persona/PersonaHub", "persona", 
                                                             streaming=True, cache_dir=cache_dir)))
                
            logger.info(f"Set up {len(self.datasets)} dataset references for lazy loading")
        except ImportError:
            logger.error("Failed to import 'datasets'. Please install it with 'pip install datasets'.")
            raise
        except Exception as e:
            logger.error(f"Error setting up PersonaHub dataset: {str(e)}")
            raise
    
    def _load_personas(self, n=100):
        """
        Load n personas from the dataset if not already loaded.
        
        Args:
            n (int): Number of personas to load
        """
        if len(self.personas) >= n:
            return
        
        # Calculate how many more personas we need
        needed = min(n - len(self.personas), self.max_personas - len(self.personas))
        if needed <= 0:
            return
        
        logger.info(f"Loading {needed} additional personas...")
        
        # Distribute needed personas across available datasets
        per_dataset = needed // len(self.datasets) + 1
        
        for source_type, dataset in self.datasets:
            count = 0
            # Use take() to get only the number of examples we need
            for i, item in enumerate(dataset["train"].take(per_dataset)):
                if len(self.personas) >= self.max_personas:
                    break
                    
                persona = self._convert_to_persona(item, source_type, len(self.personas))
                if persona:  # Only add if conversion was successful
                    self.personas.append(persona)
                    count += 1
                    
                if count >= per_dataset:
                    break
                    
        logger.info(f"Loaded {len(self.personas)} personas in total")
    
    def _process_dataset(self, dataset, source_type, max_items=None):
        """
        Process the dataset into our persona format.
        
        Args:
            dataset: Hugging Face dataset
            source_type (str): Type of dataset ("elite" or "standard")
            max_items (int): Maximum number of items to process
        """
        for i, item in enumerate(dataset["train"]):
            if max_items is not None and i >= max_items:
                break
                
            persona = self._convert_to_persona(item, source_type, i)
            if persona:  # Only add if conversion was successful
                self.personas.append(persona)
    
    def _convert_to_persona(self, item, source_type, index):
        """
        Convert a dataset item to our Persona format.
        
        Args:
            item: Dataset item
            source_type (str): Type of dataset ("elite" or "standard")
            index (int): Index of the item in the dataset
            
        Returns:
            Persona: Converted persona
        """
        try:
            persona = Persona()
            
            # Basic identification
            persona.id = f"{source_type}_{index}"
            persona.source = f"personahub_{source_type}"
            
            # Extract the persona description from the 'persona' field
            persona.description = item.get("persona", "")
            
            # Extract basic attributes using simple pattern matching
            self._extract_basic_attributes(persona)
            
            return persona
        except Exception as e:
            logger.error(f"Error processing persona: {str(e)}")
            return None
    
    def _extract_basic_attributes(self, persona):
        """
        Extract basic attributes from the persona description using pattern matching.
        
        Args:
            persona (Persona): Persona to extract attributes for
        """
        desc = persona.description.lower()
        
        # Age extraction
        age_match = re.search(r'(\d+)[- ]year[s]?[- ]old', desc)
        if age_match:
            persona.age = int(age_match.group(1))
        
        # Gender extraction
        if "female" in desc or "woman" in desc or "girl" in desc:
            persona.gender = "female"
        elif "male" in desc or "man" in desc or "boy" in desc:
            persona.gender = "male"
        elif "non-binary" in desc or "nonbinary" in desc or "non binary" in desc:
            persona.gender = "non_binary"
        
        # Education extraction
        education_keywords = {
            "high school": "high_school",
            "bachelor": "bachelors",
            "college": "some_college",
            "university": "bachelors",
            "master": "masters",
            "phd": "doctorate",
            "doctorate": "doctorate"
        }
        
        for keyword, edu_level in education_keywords.items():
            if keyword in desc:
                persona.education = edu_level
                break
        
        # Occupation extraction
        occupation_patterns = [
            r'(?:I am|I\'m) (?:a|an) ([a-zA-Z]+(?:\s[a-zA-Z]+)?) (?:at|for|in|who)',
            r'(?:work|working) as (?:a|an) ([a-zA-Z]+(?:\s[a-zA-Z]+)?)',
            r'(?:I am|I\'m) (?:a|an) ([a-zA-Z]+(?:\s[a-zA-Z]+)?)$'
        ]
        
        for pattern in occupation_patterns:
            match = re.search(pattern, desc)
            if match:
                persona.occupation = match.group(1)
                break
    
    def enhance_with_llm(self, provider="azure", model=None, batch_size=10):
        """
        Enhance personas with attributes extracted using an LLM.
        
        Args:
            provider (str): LLM provider to use
            model (str): Model to use
            batch_size (int): Number of personas to process in each batch
        """
        try:
            from selfplay.provider_interface import get_provider
            
            llm_provider = get_provider(provider, model=model)
            
            for i in range(0, len(self.personas), batch_size):
                batch = self.personas[i:i+batch_size]
                logger.info(f"Enhancing personas {i} to {i+len(batch)-1}...")
                
                for persona in batch:
                    prompt = f"""
                    Based on the following persona description, extract key demographic and psychographic attributes.
                    
                    Persona description: "{persona.description}"
                    
                    Please extract the following attributes in JSON format:
                    - age: numeric age or age range
                    - gender: "male", "female", "non_binary", or "unknown"
                    - education: highest level of education
                    - occupation: current or most recent job
                    - income_level: "low", "middle", "upper_middle", "high", or "unknown"
                    - location: geographic location (city, state, country)
                    - personality_traits: key personality characteristics
                    - interests: main hobbies and interests
                    - political_leaning: "liberal", "moderate", "conservative", or "unknown"
                    - values: core values and beliefs
                    
                    Format as valid JSON.
                    """
                    
                    # Get response from LLM
                    response = llm_provider.generate_response([
                        {"role": "system", "content": "You are a helpful assistant that extracts structured information from text."},
                        {"role": "user", "content": prompt}
                    ])
                    
                    # Parse response and update persona
                    try:
                        # Find JSON in the response
                        json_match = re.search(r'\{.*\}', response, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                            attributes = json.loads(json_str)
                            
                            # Update persona attributes
                            for key, value in attributes.items():
                                if hasattr(persona, key):
                                    setattr(persona, key, value)
                        else:
                            logger.warning(f"No JSON found in LLM response for persona {persona.id}")
                    except Exception as e:
                        logger.error(f"Error parsing LLM response for persona {persona.id}: {str(e)}")
                    
                # Add a small delay to avoid rate limiting
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error enhancing personas with LLM: {str(e)}")
    
    def sample(self, n=100, stratify_by=None, filter_by=None):
        """
        Sample n personas from the database, loading more if needed.
        
        Args:
            n (int): Number of personas to sample
            stratify_by (str): Attribute to stratify by (e.g., "gender", "age")
            filter_by (dict): Dict of attributes to filter by (e.g., {"gender": "female"})
            
        Returns:
            List[Persona]: List of sampled personas
        """
        # Make sure we have enough personas loaded
        self._load_personas(n * 2)  # Load twice as many to allow for filtering
        
        available_personas = self.personas
        
        # Apply filters if specified
        if filter_by:
            filtered_personas = []
            for p in available_personas:
                matches = True
                for attr, value in filter_by.items():
                    if not p.has_attribute(attr, value):
                        matches = False
                        break
                if matches:
                    filtered_personas.append(p)
            available_personas = filtered_personas
        
        # If we don't have enough personas after filtering, warn the user
        if len(available_personas) < n:
            logger.warning(f"Requested {n} personas but only {len(available_personas)} match the criteria")
            n = len(available_personas)
        
        if n == 0:
            logger.warning("No personas match the specified criteria")
            return []
        
        # Simple random sampling if no stratification
        if not stratify_by or not all(hasattr(p, stratify_by) for p in available_personas):
            return random.sample(available_personas, n)
        
        # Stratified sampling
        strata = {}
        for p in available_personas:
            stratum = getattr(p, stratify_by)
            if stratum not in strata:
                strata[stratum] = []
            strata[stratum].append(p)
        
        # Calculate how many to sample from each stratum
        total = len(available_personas)
        sampled = []
        
        for stratum, personas in strata.items():
            # Proportional allocation
            stratum_n = round(n * len(personas) / total)
            if stratum_n > 0:
                sampled.extend(random.sample(personas, min(stratum_n, len(personas))))
        
        # Adjust if we didn't get exactly n
        if len(sampled) < n:
            remaining = [p for p in available_personas if p not in sampled]
            sampled.extend(random.sample(remaining, min(n - len(sampled), len(remaining))))
        elif len(sampled) > n:
            sampled = random.sample(sampled, n)
            
        return sampled
    
    def get_persona_by_id(self, persona_id):
        """
        Get a specific persona by ID.
        
        Args:
            persona_id (str): ID of the persona to get
            
        Returns:
            Persona: The persona with the specified ID, or None if not found
        """
        for persona in self.personas:
            if persona.id == persona_id:
                return persona
        return None
    
    def to_dataframe(self):
        """
        Convert personas to a pandas DataFrame.
        
        Returns:
            pd.DataFrame: DataFrame containing all personas
        """
        data = []
        for p in self.personas:
            data.append(p.to_dict())
        return pd.DataFrame(data)
    
    def save(self, filepath):
        """
        Save the persona database to a file.
        
        Args:
            filepath (str): Path to save the database to
        """
        with open(filepath, 'w') as f:
            json.dump([p.to_dict() for p in self.personas], f)
        logger.info(f"Saved {len(self.personas)} personas to {filepath}")
    
    def load(self, filepath):
        """
        Load the persona database from a file.
        
        Args:
            filepath (str): Path to load the database from
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        self.personas = []
        for item in data:
            p = Persona.from_dict(item)
            self.personas.append(p)
        
        logger.info(f"Loaded {len(self.personas)} personas from {filepath}")
