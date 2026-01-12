
"""
Utility functions for filtering and cleaning extracted data
"""

import re
from typing import List


def extract_species_from_compound_name(compound_name: str) -> str:
    """
    Extract species name from compound names like "tiger skin" -> "tiger"

    Args:
        compound_name: Compound name containing species and product

    Returns:
        Extracted species name or original if no extraction needed
    """
    compound_lower = compound_name.lower().strip()

    # Common product indicators to split on
    product_indicators = [
        'skin', 'skins', 'hide', 'hides', 'scale', 'scales', 'scaly',
        'horn', 'horns', 'tusk', 'tusks', 'tooth', 'teeth', 'fang', 'fangs',
        'bone', 'bones', 'meat', 'fur', 'pelt', 'pelts', 'leather',
        'ivory', 'claw', 'claws', 'tail', 'tails', 'feather', 'feathers',
        'egg', 'eggs', 'shell', 'shells', 'bile', 'gallbladder',
        'organ', 'organs', 'blood', 'fat', 'oil'
    ]

    # Split on product indicators and take the first part as species
    for indicator in product_indicators:
        if f' {indicator}' in compound_lower or f'{indicator} ' in compound_lower:
            # Split and take the species part (usually the first word)
            parts = compound_lower.split()
            if len(parts) >= 2:
                # Take the first part as the species name
                species_candidate = parts[0]
                # Validate it's a reasonable species name (not too short, not generic)
                if len(species_candidate) > 2 and species_candidate not in ['animal', 'wildlife', 'creature']:
                    return species_candidate.title()

    return compound_name  # Return original if no extraction possible


def filter_species_from_products(animals: List[str]) -> List[str]:
    """
    Filter out wildlife products from species list and extract species from compound names.
    Converts "tiger skin" -> "Tiger", "leopard skin" -> "Leopard", etc.

    Args:
        animals: List of extracted animal names/products

    Returns:
        List of actual species (filtered and extracted)
    """
    if not animals:
        return []

    # Common animal species (to preserve legitimate species)
    known_species = {
        'tiger', 'tigers', 'leopard', 'leopards', 'panther', 'panthers',
        'elephant', 'elephants', 'rhino', 'rhinos', 'rhinoceros',
        'pangolin', 'pangolins', 'turtle', 'turtles', 'tortoise', 'tortoises',
        'snake', 'snakes', 'lizard', 'lizards', 'frog', 'frogs',
        'bird', 'birds', 'parrot', 'parrots', 'eagle', 'eagles',
        'owl', 'owls', 'monkey', 'monkeys', 'ape', 'apes',
        'bear', 'bears', 'deer', 'wolf', 'wolves', 'lion', 'lions',
        'cheetah', 'cheetahs', 'jaguar', 'jaguars', 'crocodile', 'crocodiles',
        'alligator', 'alligators', 'shark', 'sharks', 'whale', 'whales',
        'dolphin', 'dolphins', 'seal', 'seals', 'otter', 'otters'
    }

    filtered_animals = []

    for animal in animals:
        animal_lower = animal.lower().strip()

        # Skip generic terms that aren't species
        if animal_lower in ['animal', 'animals', 'wildlife', 'creature', 'creatures']:
            continue

        # Try to extract species from compound names
        extracted_species = extract_species_from_compound_name(animal)

        # If extraction resulted in a different name, use the extracted species
        if extracted_species != animal:
            species_name = extracted_species.lower()
        else:
            species_name = animal_lower

        # Keep if it's a known species
        if species_name in known_species:
            # Normalize to title case and singular form
            normalized = extracted_species.title()
            # Convert plurals to singular for consistency
            if normalized.endswith('s') and normalized.lower()[:-1] in known_species:
                normalized = normalized[:-1]
            filtered_animals.append(normalized)

    return list(set(filtered_animals))  # Remove duplicates


def clean_extracted_animals(animals: List[str]) -> List[str]:
    """
    Clean and normalize extracted animal names

    Args:
        animals: Raw extracted animal names

    Returns:
        Cleaned and filtered animal species
    """
    if not animals:
        return []

    # First filter out products
    species_only = filter_species_from_products(animals)

    # Additional cleaning
    cleaned = []
    for animal in species_only:
        # Remove extra whitespace and normalize
        cleaned_animal = ' '.join(animal.split()).title()
        if cleaned_animal and len(cleaned_animal) > 1:  # Avoid single letters
            cleaned.append(cleaned_animal)

    return cleaned


def is_wildlife_product(text: str) -> bool:
    """
    Check if text describes a wildlife product rather than a species

    Args:
        text: Text to check

    Returns:
        True if it's a product, False if it's a species
    """
    text_lower = text.lower()

    # Product patterns
    product_patterns = [
        r'\b\w+\s+(skin|skins|hide|hides|scale|scales|horn|horns|tusk|tusks|tooth|teeth|bone|bones|meat|fur|leather|ivory|claw|claws|tail|tails|feather|feathers|egg|eggs|shell|shells)\b',
        r'\b(skin|scales|horn|ivory|leather|fur|bones?|tusks?|claws?|tails?|feathers?|eggs?|shells?)\b.*\b\w+\b'
    ]

    for pattern in product_patterns:
        if re.search(pattern, text_lower):
            return True

    return False
