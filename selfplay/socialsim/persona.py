"""
Persona class for SocialSim.

This module defines the Persona class, which represents an individual persona with
demographic and psychographic attributes.
"""

class Persona:
    """
    A class representing an individual persona with demographic and psychographic attributes.
    
    Attributes:
        id (str): Unique identifier for the persona
        source (str): Source of the persona (e.g., "personahub_elite")
        description (str): Natural language description of the persona
        
        # Demographic attributes
        age (int or str): Age or age range
        gender (str): Gender identity (e.g., "male", "female", "non_binary")
        education (str): Highest level of education
        income (str): Income level or range
        location (str): Geographic location
        occupation (str): Current or most recent job
        family_status (str): Family status (e.g., "single", "married", "divorced")
        
        # Psychographic attributes
        personality_traits (dict): Personality traits (e.g., Big Five traits)
        values (dict): Core values and beliefs
        interests (list): Areas of interest and hobbies
        political_leaning (str): Political orientation
        social_issues (dict): Positions on various social issues
        
        # Response tendencies
        response_style (str): Characteristic response style
        bias_patterns (dict): Known response biases
    """
    
    def __init__(self):
        """Initialize a new Persona instance with default attribute values."""
        # Basic identification
        self.id = None
        self.source = None
        self.description = None
        
        # Demographic attributes
        self.age = None
        self.gender = None
        self.education = None
        self.income = None
        self.location = None
        self.occupation = None
        self.family_status = None
        
        # Psychographic attributes
        self.personality_traits = {}
        self.values = {}
        self.interests = []
        self.political_leaning = None
        self.social_issues = {}
        
        # Response tendencies
        self.response_style = None
        self.bias_patterns = {}
    
    def __str__(self):
        """Return a string representation of the persona."""
        if self.description:
            return f"Persona {self.id}: {self.description[:50]}..."
        else:
            return f"Persona {self.id}: {self.gender}, {self.age}, {self.occupation}"
    
    def to_dict(self):
        """Convert the persona to a dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data):
        """Create a persona from a dictionary."""
        persona = cls()
        for key, value in data.items():
            setattr(persona, key, value)
        return persona
    
    def has_attribute(self, attribute, value=None):
        """
        Check if the persona has a specific attribute, optionally with a specific value.
        
        Args:
            attribute (str): The attribute to check
            value: The value to check for (optional)
            
        Returns:
            bool: True if the persona has the attribute (with the specified value if provided)
        """
        if not hasattr(self, attribute) or getattr(self, attribute) is None:
            return False
        
        if value is not None:
            attr_value = getattr(self, attribute)
            
            # Handle different types of attributes
            if isinstance(attr_value, dict) and isinstance(value, dict):
                # Check if all key-value pairs in value are in attr_value
                return all(k in attr_value and attr_value[k] == v for k, v in value.items())
            elif isinstance(attr_value, list) and not isinstance(value, list):
                # Check if value is in the list
                return value in attr_value
            else:
                # Direct comparison
                return attr_value == value
        
        return True
