"""
AI-powered entity extraction for incident descriptions
Extracts animals, locations, and keywords from text using Google Generative AI
"""

from typing import List, Optional, Dict, Any
from .llm import generate_text_with_json, ENTITY_EXTRACTION_PROMPT, check_api_key


async def extract_entities_from_text(text: str) -> Dict[str, Any]:
    """
    Extract entities from incident description text
    
    Args:
        text: Incident description text
        
    Returns:
        Dictionary containing extracted entities:
        - animals: List of animal species/products
        - location: Extracted location string
        - entities: List of other entities (people, organizations)
        - keywords: List of important keywords
    """
    if not check_api_key():
        print("⚠️ Google API key not configured, using fallback extraction")
        return fallback_entity_extraction(text)
    
    try:
        # Use AI to extract entities
        prompt = ENTITY_EXTRACTION_PROMPT.format(text=text)
        json_response = await generate_text_with_json(
            prompt,
            temperature=0.3
        )
        
        # Parse JSON response
        import json
        entities = json.loads(json_response)
        
        # Ensure expected structure
        return {
            "animals": entities.get("animals", []),
            "location": entities.get("location", ""),
            "entities": entities.get("entities", []),
            "keywords": entities.get("keywords", [])
        }
    
    except Exception as e:
        print(f"⚠️ AI entity extraction failed: {e}, using fallback")
        return fallback_entity_extraction(text)


def fallback_entity_extraction(text: str) -> Dict[str, Any]:
    """
    Fallback entity extraction without AI
    Basic keyword matching and heuristics
    
    Args:
        text: Incident description text
        
    Returns:
        Dictionary with extracted entities
    """
    text_lower = text.lower()
    
    # Common animal keywords
    animal_keywords = [
        'tiger', 'elephant', 'rhino', 'pangolin', 'turtle', 'tortoise',
        'ivory', 'skin', 'scales', 'horn', 'bone', 'meat', 'leather',
        'snake', 'lizard', 'frog', 'bird', 'parrot', 'eagle', 'owl',
        'monkey', 'ape', 'bear', 'deer', 'wolf', 'lion', 'cheetah'
    ]
    
    # Common location indicators
    location_indicators = [
        'port', 'airport', 'border', 'forest', 'national park',
        'zoo', 'market', 'village', 'city', 'state', 'province',
        'country', 'india', 'china', 'thailand', 'vietnam', 'malaysia',
        'indonesia', 'africa', 'asia', 'america', 'europe'
    ]
    
    # Extract animals
    animals = []
    for keyword in animal_keywords:
        if keyword in text_lower:
            animals.append(keyword.title())
    
    # Extract location (simple heuristic - look for capitalized words after certain prepositions)
    location = ""
    import re
    location_patterns = [
        r'\b(?:in|at|from|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:port|airport|border)'
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, text)
        if matches:
            location = matches[0]
            break
    
    # Extract keywords (nouns and important terms)
    words = re.findall(r'\b\w{4,}\b', text_lower)
    common_words = {
        'this', 'that', 'with', 'from', 'were', 'have', 'been',
        'their', 'there', 'where', 'when', 'which', 'while',
        'officials', 'customs', 'police', 'authorities', 'seized'
    }
    keywords = [w.title() for w in words if w not in common_words][:10]
    
    return {
        "animals": list(set(animals)),  # Remove duplicates
        "location": location,
        "entities": [],  # Not extracting entities in fallback
        "keywords": keywords
    }


async def extract_animals_only(text: str) -> List[str]:
    """
    Extract only animal species/products from text
    
    Args:
        text: Incident description text
        
    Returns:
        List of extracted animals
    """
    entities = await extract_entities_from_text(text)
    return entities.get("animals", [])


async def extract_location_only(text: str) -> Optional[str]:
    """
    Extract only location from text
    
    Args:
        text: Incident description text
        
    Returns:
        Extracted location string or None
    """
    entities = await extract_entities_from_text(text)
    location = entities.get("location", "")
    return location if location else None


async def extract_keywords_only(text: str) -> List[str]:
    """
    Extract only keywords from text
    
    Args:
        text: Incident description text
        
    Returns:
        List of extracted keywords
    """
    entities = await extract_entities_from_text(text)
    return entities.get("keywords", [])


async def extract_entities_batch(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Extract entities from multiple texts
    
    Args:
        texts: List of incident description texts
        
    Returns:
        List of entity dictionaries
    """
    results = []
    
    for text in texts:
        try:
            entities = await extract_entities_from_text(text)
            results.append(entities)
        except Exception as e:
            print(f"⚠️ Batch entity extraction error: {e}")
            results.append(fallback_entity_extraction(text))
    
    return results


def validate_extracted_entities(entities: Dict[str, Any]) -> bool:
    """
    Validate extracted entities structure
    
    Args:
        entities: Extracted entities dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ['animals', 'location', 'entities', 'keywords']
    
    if not isinstance(entities, dict):
        return False
    
    for key in required_keys:
        if key not in entities:
            return False
        
        if key in ['animals', 'entities', 'keywords']:
            if not isinstance(entities[key], list):
                return False
        elif key == 'location':
            if not isinstance(entities[key], str):
                return False
    
    return True
