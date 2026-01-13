"""
Data Enrichment Agent
Uses Google Gemini to extract structured information from incident descriptions
"""

import json
import re
from typing import Dict, List, Optional
from .llm import get_model, USE_NEW_SDK
from .filter_utils import clean_extracted_animals


class EnrichmentAgent:
    """AI-powered data enrichment using Google Gemini"""
    
    def __init__(self):
        self.model = get_model()
        
    def enrich_incident(self, incident: Dict) -> Dict:
        """
        Enrich a single incident with AI-extracted information
        
        Args:
            incident: Dictionary with at least 'description' field
            
        Returns:
            Original incident with additional AI-extracted fields
        """
        description = incident.get('description', '')
        location = incident.get('location', '')
        
        if not description:
            return incident
        
        try:
            # Create prompt for extraction
            prompt = self._create_extraction_prompt(description, location)
            
            # Get AI response
            response = self._call_model(prompt)
            
            # Parse response
            extracted_data = self._parse_response(response)
            
            # Merge with original incident
            enriched = {**incident}
            raw_animals = extracted_data.get('animal_species', [])
            enriched.update({
                'animals': extracted_data.get('animals', ''),
                'quantity': extracted_data.get('quantity'),
                'source': extracted_data.get('source', ''),
                'suspects': extracted_data.get('suspects'),
                'vehicle_info': extracted_data.get('vehicle_info'),
                'estimated_value': extracted_data.get('estimated_value'),
                'status': extracted_data.get('status', 'Reported'),
                'extracted_animals': clean_extracted_animals(raw_animals),
                'keywords': extracted_data.get('keywords', []),
                'ai_summary': extracted_data.get('summary', ''),
                'ai_enriched': True
            })
            
            return enriched
            
        except Exception as e:
            # If enrichment fails, return original with error flag
            incident['ai_enriched'] = False
            incident['enrichment_error'] = str(e)
            return incident
    
    def enrich_batch(self, incidents: List[Dict]) -> List[Dict]:
        """
        Enrich multiple incidents
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            List of enriched incidents
        """
        enriched_incidents = []
        
        for incident in incidents:
            enriched = self.enrich_incident(incident)
            enriched_incidents.append(enriched)
        
        return enriched_incidents
    
    def _create_extraction_prompt(self, description: str, location: str = '') -> str:
        """Create prompt for Gemini to extract structured data"""
        
        prompt = f"""You are a wildlife crime analyst. Extract structured information from this incident description.

DESCRIPTION: {description}
LOCATION: {location}

Extract the following information and return as JSON:
{{
  "animals": "Main animal/wildlife product type (e.g., 'Elephant tusks', 'Pangolin scales', 'Tiger skins')",
  "animal_species": (e.g., ['Elephant', 'Pangolin', 'Tiger']),
  "quantity": "Quantity with units (e.g., '150 kg', '3 tusks', '25 animals')",
  "source": "Reporting agency or information source (e.g., 'Wildlife Crime Control Bureau', 'Customs', 'Park Rangers')",
  "suspects": "Number of suspects or arrests (e.g., '3 arrested', '2 suspects identified')",
  "vehicle_info": "Vehicle information if mentioned (e.g., 'White truck', 'Cargo ship')",
  "estimated_value": "Monetary value if mentioned (with currency)",
  "status": "Case status - one of: 'Reported', 'Under Investigation', 'Arrest Made', 'Case Closed', 'Ongoing'",
  "keywords": ["important", "keywords", "from", "description"],
  "summary": "Brief 1-sentence summary of the incident"
}}

Rules:
- If information is not mentioned, use null for that field
- Be precise and extract only what is explicitly stated
- For status, infer from context (arrests = 'Arrest Made', ongoing investigation = 'Under Investigation', etc.)
- Animal species should be ONLY actual animal species names (scientific or common names), NOT products like skin, scales, horn, etc.
- Do not include wildlife products in the animal_species array - only species names
- Keep summaries under 100 characters

Return ONLY valid JSON, no additional text.
"""
        return prompt
    
    def _call_model(self, prompt: str) -> str:
        """Call Gemini model and get response"""
        try:
            if USE_NEW_SDK:
                # New SDK (google-genai)
                from google.genai import types
                
                response = self.model.generate_content(
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=1000,
                    )
                )
                return response.text
            else:
                # Old SDK (google.generativeai)
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.1,
                        'max_output_tokens': 1000,
                    }
                )
                return response.text
                
        except Exception as e:
            raise Exception(f"Model call failed: {str(e)}")
    
    def _parse_response(self, response: str) -> Dict:
        """Parse JSON response from model"""
        try:
            # Extract JSON from response (in case model adds extra text)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try parsing entire response
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return empty dict
            return {
                'animals': '',
                'quantity': None,
                'source': '',
                'suspects': None,
                'vehicle_info': None,
                'estimated_value': None,
                'status': 'Reported',
                'animal_species': [],
                'keywords': [],
                'summary': ''
            }


# Convenience functions
def enrich_single_incident(incident: Dict) -> Dict:
    """Enrich a single incident"""
    agent = EnrichmentAgent()
    return agent.enrich_incident(incident)


def enrich_multiple_incidents(incidents: List[Dict]) -> List[Dict]:
    """Enrich multiple incidents"""
    agent = EnrichmentAgent()
    return agent.enrich_batch(incidents)


def extract_animals_from_text(text: str) -> List[str]:
    """
    Quick extraction of animal names from text
    Used by existing extractor.py
    """
    agent = EnrichmentAgent()
    prompt = f"""Extract ONLY actual animal species names from this text as a JSON array.
Do NOT include wildlife products like skin, scales, horn, tusks, etc.

Text: {text}

Return format: ["species1", "species2", ...]

Return ONLY the JSON array, no additional text."""
    
    try:
        response = agent._call_model(prompt)
        # Extract JSON array
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            raw_animals = json.loads(match.group(0))
            # Clean the extracted animals
            return clean_extracted_animals(raw_animals)
        return []
    except:
        return []
