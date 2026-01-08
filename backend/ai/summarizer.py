"""
AI-powered text summarization for incident descriptions
Generates concise summaries of smuggling incidents
"""

from typing import List, Optional
from .llm import generate_text, SUMMARY_PROMPT, PATTERN_ANALYSIS_PROMPT, check_api_key


async def generate_summary(text: str, max_length: int = 150) -> str:
    """
    Generate a concise summary of incident description
    
    Args:
        text: Full incident description
        max_length: Maximum length of summary in characters
        
    Returns:
        Generated summary text
    """
    if not check_api_key():
        print("⚠️ Google API key not configured, using extractive summary")
        return extractive_summary(text, max_length)
    
    try:
        # Use AI to generate summary
        prompt = SUMMARY_PROMPT.format(text=text)
        summary = await generate_text(
            prompt,
            temperature=0.5,
            max_tokens=100
        )
        
        # Trim to max length if needed
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(' ', 1)[0] + "..."
        
        return summary.strip()
    
    except Exception as e:
        print(f"⚠️ AI summarization failed: {e}, using extractive summary")
        return extractive_summary(text, max_length)


def extractive_summary(text: str, max_length: int = 150) -> str:
    """
    Fallback extractive summarization
    Simply takes the first N characters/sentences
    
    Args:
        text: Full text
        max_length: Maximum length
        
    Returns:
        Extracted summary
    """
    if len(text) <= max_length:
        return text
    
    # Try to break at sentence boundary
    summary = text[:max_length]
    last_period = summary.rfind('.')
    
    if last_period > max_length * 0.7:  # If we can get at least 70% with full sentence
        summary = summary[:last_period + 1]
    else:
        # Break at word boundary
        summary = summary.rsplit(' ', 1)[0] + "..."
    
    return summary


async def generate_summaries_batch(texts: List[str]) -> List[str]:
    """
    Generate summaries for multiple texts
    
    Args:
        texts: List of incident descriptions
        
    Returns:
        List of summaries
    """
    summaries = []
    
    for text in texts:
        try:
            summary = await generate_summary(text)
            summaries.append(summary)
        except Exception as e:
            print(f"⚠️ Batch summary error: {e}")
            summaries.append(extractive_summary(text))
    
    return summaries


async def generate_incident_report(incidents: List[dict]) -> str:
    """
    Generate a comprehensive report from multiple incidents
    
    Args:
        incidents: List of incident dictionaries
        
    Returns:
        Generated report text
    """
    if not check_api_key():
        return generate_simple_report(incidents)
    
    try:
        # Prepare incident text
        incident_texts = []
        for idx, incident in enumerate(incidents, 1):
            text = f"{idx}. {incident.get('location', 'Unknown')} - {incident.get('animals', 'Unknown')}: {incident.get('description', '')}"
            incident_texts.append(text)
        
        incidents_str = "\n".join(incident_texts)
        
        # Generate analysis
        prompt = PATTERN_ANALYSIS_PROMPT.format(incidents=incidents_str)
        report = await generate_text(
            prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        return report
    
    except Exception as e:
        print(f"⚠️ Report generation failed: {e}")
        return generate_simple_report(incidents)


def generate_simple_report(incidents: List[dict]) -> str:
    """
    Generate a simple statistical report without AI
    
    Args:
        incidents: List of incident dictionaries
        
    Returns:
        Simple report text
    """
    from collections import Counter
    
    total = len(incidents)
    
    # Count by status
    statuses = [inc.get('status', 'Unknown') for inc in incidents]
    status_counts = Counter(statuses)
    
    # Count by animal
    animals = [inc.get('animals', 'Unknown') for inc in incidents]
    animal_counts = Counter(animals).most_common(5)
    
    # Count by location
    locations = [inc.get('location', 'Unknown') for inc in incidents]
    location_counts = Counter(locations).most_common(5)
    
    report = f"""
Wildlife Smuggling Incident Report
==================================

Total Incidents: {total}

Status Breakdown:
{chr(10).join(f"- {status}: {count}" for status, count in status_counts.items())}

Top 5 Most Smuggled Animals/Products:
{chr(10).join(f"{idx}. {animal}: {count} incidents" for idx, (animal, count) in enumerate(animal_counts, 1))}

Top 5 Locations:
{chr(10).join(f"{idx}. {location}: {count} incidents" for idx, (location, count) in enumerate(location_counts, 1))}
"""
    
    return report


async def summarize_with_keywords(text: str) -> dict:
    """
    Generate summary along with extracted keywords
    
    Args:
        text: Incident description
        
    Returns:
        Dictionary with summary and keywords
    """
    summary = await generate_summary(text)
    
    # Extract keywords (simple version)
    import re
    words = re.findall(r'\b\w{5,}\b', text.lower())
    common_words = {
        'the', 'and', 'for', 'from', 'with', 'this', 'that',
        'were', 'was', 'are', 'been', 'have', 'has', 'had',
        'their', 'there', 'where', 'when', 'which', 'while'
    }
    keywords = [w for w in words if w not in common_words]
    
    # Count and get top keywords
    from collections import Counter
    keyword_counts = Counter(keywords).most_common(10)
    
    return {
        "summary": summary,
        "keywords": [kw for kw, _ in keyword_counts]
    }


async def generate_executive_summary(incidents: List[dict], time_period: str = "recent") -> str:
    """
    Generate executive summary for dashboards and reports
    
    Args:
        incidents: List of incidents
        time_period: Description of time period (e.g., "last month")
        
    Returns:
        Executive summary text
    """
    total = len(incidents)
    
    if total == 0:
        return f"No wildlife smuggling incidents recorded for {time_period}."
    
    # Basic stats
    statuses = [inc.get('status', 'Unknown') for inc in incidents]
    prosecuted = statuses.count('Prosecuted')
    investigated = statuses.count('Investigated')
    
    # Most common animal
    from collections import Counter
    animals = [inc.get('animals', 'Unknown') for inc in incidents]
    most_common_animal = Counter(animals).most_common(1)[0][0] if animals else "various species"
    
    summary = f"""
Executive Summary - {time_period.title()}

• Total Incidents: {total}
• Cases Prosecuted: {prosecuted} ({round(prosecuted/total*100)}%)
• Under Investigation: {investigated}
• Most Targeted: {most_common_animal}

Key Concern: Wildlife smuggling continues to be a significant threat, with {most_common_animal} being the most frequently targeted. Enhanced monitoring and enforcement efforts are recommended.
"""
    
    return summary.strip()