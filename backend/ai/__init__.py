"""
AI module for Wildlife Smuggling Tracker
Provides entity extraction and text summarization using Google Generative AI
"""

from .llm import get_model, generate_text, check_api_key
from .extractor import extract_entities_from_text, extract_animals_only, extract_location_only
from .summarizer import generate_summary, generate_incident_report

__all__ = [
    'get_model',
    'generate_text',
    'check_api_key',
    'extract_entities_from_text',
    'extract_animals_only',
    'extract_location_only',
    'generate_summary',
    'generate_incident_report'
]