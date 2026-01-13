"""
Tag assignment logic for wildlife incidents
Automatically assigns predefined tags based on incident description and content
"""

import re
from typing import List, Dict, Any

# Predefined tags for wildlife incidents
PREDEFINED_TAGS = [
    "Animal Hunting", "Animal Killing", "Poaching", "Animal Smuggling",
    "Illegal Wildlife Trade", "Animal Capture", "Animal Injury/Cruelty",
    "Seizure of Animal Products", "Illegal Weapon Usage", "Forest Law Violation",
    "Arrest/Legal Action", "Rescue and Rehabilitation"
]

# Keywords and patterns for each tag
TAG_KEYWORDS = {
    "Animal Hunting": [
        "hunt", "hunting", "hunter", "hunted", "game", "trophy", "safari",
        "stalk", "track", "pursue", "chase"
    ],
    "Animal Killing": [
        "kill", "killed", "killing", "slaughter", "slaughtered", "murder",
        "death", "dead", "fatal", "lethal", "execute", "executed"
    ],
    "Poaching": [
        "poach", "poacher", "poaching", "illegal hunt", "wildlife crime",
        "endangered species", "protected animal", "banned hunt"
    ],
    "Animal Smuggling": [
        "smuggle", "smuggling", "smuggler", "contraband", "illegal transport",
        "border crossing", "hidden cargo", "traffick", "trafficking"
    ],
    "Illegal Wildlife Trade": [
        "trade", "trading", "market", "black market", "illegal sale",
        "wildlife commerce", "animal trafficking", "commercial poaching"
    ],
    "Animal Capture": [
        "capture", "captured", "trap", "trapped", "net", "cage", "caught",
        "seize", "seized", "arrest animal", "animal detention"
    ],
    "Animal Injury/Cruelty": [
        "injure", "injured", "injury", "cruelty", "abuse", "torture",
        "mutilate", "mutilated", "wound", "wounded", "suffer", "suffering"
    ],
    "Seizure of Animal Products": [
        "seize", "seized", "confiscate", "confiscated", "ivory", "tusk",
        "skin", "hide", "fur", "scale", "horn", "bone", "meat", "product"
    ],
    "Illegal Weapon Usage": [
        "weapon", "gun", "rifle", "firearm", "poison", "trap", "snare",
        "explosive", "bomb", "illegal weapon", "prohibited weapon"
    ],
    "Forest Law Violation": [
        "forest", "protected area", "national park", "sanctuary", "reserve",
        "conservation area", "wildlife reserve", "violation", "trespass"
    ],
    "Arrest/Legal Action": [
        "arrest", "arrested", "detain", "detained", "charge", "charged",
        "prosecute", "prosecuted", "court", "legal", "law enforcement"
    ],
    "Rescue and Rehabilitation": [
        "rescue", "rescued", "rehabilitate", "rehabilitation", "save",
        "saved", "release", "released", "recovery", "treatment", "care"
    ]
}

def assign_tags_to_incident(incident: Dict[str, Any]) -> List[str]:
    """
    Analyze incident data and assign appropriate tags

    Args:
        incident: Dictionary containing incident data

    Returns:
        List of assigned tags
    """
    assigned_tags = []
    text_to_analyze = ""

    # Combine relevant text fields for analysis
    if incident.get("description"):
        text_to_analyze += str(incident["description"]) + " "
    if incident.get("animals"):
        text_to_analyze += str(incident["animals"]) + " "
    if incident.get("location"):
        text_to_analyze += str(incident["location"]) + " "
    if incident.get("notes"):
        text_to_analyze += str(incident["notes"]) + " "
    if incident.get("source"):
        text_to_analyze += str(incident["source"]) + " "

    # Convert to lowercase for matching
    text_lower = text_to_analyze.lower()

    # Check each tag's keywords
    for tag, keywords in TAG_KEYWORDS.items():
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                if tag not in assigned_tags:
                    assigned_tags.append(tag)
                break  # Found a match for this tag, move to next tag

    # Special logic for certain combinations
    if "poaching" in text_lower or ("hunting" in text_lower and "illegal" in text_lower):
        if "Poaching" not in assigned_tags:
            assigned_tags.append("Poaching")

    if "smuggling" in text_lower or "trafficking" in text_lower:
        if "Animal Smuggling" not in assigned_tags:
            assigned_tags.append("Animal Smuggling")
        if "Illegal Wildlife Trade" not in assigned_tags:
            assigned_tags.append("Illegal Wildlife Trade")

    # If no tags were assigned but it's clearly a wildlife incident, assign general tags
    if not assigned_tags and any(word in text_lower for word in ["wildlife", "animal", "species", "conservation"]):
        # Try to infer from context
        if any(word in text_lower for word in ["kill", "dead", "death"]):
            assigned_tags.append("Animal Killing")
        elif any(word in text_lower for word in ["arrest", "seize"]):
            assigned_tags.append("Arrest/Legal Action")
        elif any(word in text_lower for word in ["rescue", "save"]):
            assigned_tags.append("Rescue and Rehabilitation")

    return assigned_tags

def assign_tags_to_multiple_incidents(incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assign tags to multiple incidents

    Args:
        incidents: List of incident dictionaries

    Returns:
        List of incidents with tags assigned
    """
    tagged_incidents = []

    for incident in incidents:
        # Create a copy to avoid modifying the original
        tagged_incident = incident.copy()

        # Assign tags
        assigned_tags = assign_tags_to_incident(incident)

        # Only add tags if any were assigned
        if assigned_tags:
            tagged_incident["tags"] = assigned_tags

        tagged_incidents.append(tagged_incident)

    return tagged_incidents

# For testing purposes
if __name__ == "__main__":
    # Test the tag assignment
    test_incident = {
        "description": "Poachers killed a tiger in the forest using illegal weapons",
        "animals": "Tiger",
        "location": "National Park"
    }

    tags = assign_tags_to_incident(test_incident)
    print(f"Assigned tags: {tags}")
