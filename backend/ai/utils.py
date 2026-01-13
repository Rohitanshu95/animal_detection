"""
Utility functions for AI and data processing
"""

def normalize_animal_name(name: str) -> str:
    """
    Normalize animal name to a standard format to improve filter grouping.
    
    Args:
        name: The raw animal name string
        
    Returns:
        Normalized animal name
    """
    if not name:
        return name
        
    name_lower = name.lower().strip()
    
    # Mapping for normalization
    # keys should be lower case
    mapping = {
        "turtle": "Turtles",
        "turtles": "Turtles",
        "sea turtle": "Turtles",
        "sea turtles": "Turtles",
        "tortoise": "Turtles",
        "tortoises": "Turtles",
        "indian flapshell turtle": "Turtles",
        "softshell turtle": "Turtles",
        
        "elephant": "Elephants",
        "elephants": "Elephants",
        "asian elephant": "Elephants",
        "tusker": "Elephants",
        
        "leopard": "Leopards",
        "leopards": "Leopards",
        "leopard skin": "Leopard Skin",
        
        "pangolin": "Pangolins",
        "pangolins": "Pangolins",
        "pangolin scale": "Pangolin Scales",
        "pangolin scales": "Pangolin Scales",
        "scales": "Pangolin Scales",
        
        "tiger": "Tigers",
        "tigers": "Tigers",
        "royal bengal tiger": "Tigers",
        
        "ivory": "Ivory",
        "tusk": "Ivory",
        "tusks": "Ivory",
        
        "deer": "Deer",
        "spotted deer": "Deer",
        "barking deer": "Deer",
        
        "snake": "Snakes",
        "cobra": "Snakes",
        "python": "Snakes",
        
        "myna": "Birds",
        "parrot": "Birds",
        "parakeet": "Birds"
    }
    
    # Check exact match
    if name_lower in mapping:
        return mapping[name_lower]
        
    # Check partial match for some broad categories (be careful here)
    if "turtle" in name_lower or "tortoise" in name_lower:
        return "Turtles"
    if "elephant" in name_lower and "skin" not in name_lower and "ivory" not in name_lower and "tusk" not in name_lower:
        return "Elephants"
    if "pangolin" in name_lower and "scale" not in name_lower and "skin" not in name_lower:
        return "Pangolins"
    if "leopard" in name_lower and "skin" not in name_lower:
        return "Leopards"
    if "tiger" in name_lower and "skin" not in name_lower:
        return "Tigers"
    
    # Default: Title Case
    return name.title()


# List of 30 Districts of Odisha
ODISHA_DISTRICTS = [
    "Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", 
    "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", 
    "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", 
    "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", 
    "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", 
    "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"
]

def normalize_location_name(name: str) -> str:
    """
    Normalize location name to one of the 30 Odisha districts if similar.
    
    Args:
        name: The raw location name string
        
    Returns:
        Normalized location name (District) or original
    """
    if not name:
        return name
        
    name_lower = name.lower().strip()
    
    # Custom Mappings for variations
    mapping = {
        "baleswar": "Balasore",
        "keonjhar": "Kendujhar",
        "sonepur": "Subarnapur",
        "subarnapur": "Subarnapur", # Ensure target is standard
        "bhubaneswar": "Khordha",   # Capital city in Khordha district
        "baripada": "Mayurbhanj",   # HQ of Mayurbhanj
        "rourkela": "Sundargarh",   # City in Sundargarh
        "berhampur": "Ganjam",      # City in Ganjam
        "brahmapur": "Ganjam",
        "similipal": "Mayurbhanj", # National park mostly in Mayurbhanj
        "bhitarkanika": "Kendrapara",
        "chilika": "Khordha",       # Spans multiple, defaulting to Khordha/Puri/Ganjam - let's pick Khordha for simplicity or leave generic
        "satkosia": "Angul",
        "nabrangpur": "Nabarangpur", # Common spelling variation
        "raigada": "Rayagada",       # Common spelling variation
        "hirakud": "Sambalpur",      # Major dam in Sambalpur
        "bhitarkanika": "Kendrapara",
        "dhenkjanal": "Dhenkanal",   # Typo observed
    }
    
    # Check exact/mapped match
    if name_lower in mapping:
        return mapping[name_lower]
        
    # Check against standard districts
    for district in ODISHA_DISTRICTS:
        if district.lower() == name_lower:
            return district
            
    # Fuzzy/Substring match
    # If the input string CONTAINS the district name (e.g. "Angul District")
    for district in ODISHA_DISTRICTS:
        if district.lower() in name_lower:
            return district
            
    # Reverse check: if mappable city is in string (e.g. "Near Rourkela")
    for key, value in mapping.items():
        if key in name_lower:
            return value

    return name.title()
