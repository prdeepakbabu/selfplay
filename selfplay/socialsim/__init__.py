"""
SocialSim: Social Science Experiment Simulation Extension for SelfPlay

This module extends SelfPlay with capabilities for conducting simulations of social science experiments.
It enables researchers, marketers, policy makers, and educators to simulate surveys with large numbers
of AI personas, conduct A/B testing, and analyze results with statistical metrics.
"""

from .persona import Persona
from .persona_db import PersonaHubDB
from .experiment_runner import ExperimentRunner, SurveyResponse
from .results_collector import ResultsCollector

__all__ = [
    'Persona',
    'PersonaHubDB',
    'ExperimentRunner',
    'SurveyResponse',
    'ResultsCollector',
]
