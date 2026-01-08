"""
Google Generative AI (Gemini) connection and configuration
Updated to use the new google-genai package
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Configure Google AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Try to import the new package, fall back to old one if needed
try:
    from google import genai
    from google.genai import types
    USE_NEW_SDK = True
    print("✅ Using new google-genai package")
except ImportError:
    try:
        import google.generativeai as genai
        USE_NEW_SDK = False
        print("⚠️ Using deprecated google.generativeai package - please upgrade to google-genai")
    except ImportError:
        genai = None
        USE_NEW_SDK = False
        print("⚠️ Google AI package not installed")

if GOOGLE_API_KEY and genai:
    if USE_NEW_SDK:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Google Generative AI configured")
else:
    client = None
    if not GOOGLE_API_KEY:
        print("⚠️ Warning: GOOGLE_API_KEY not found in environment variables")

# Model configuration
MODEL_NAME = "gemini-1.5-flash"  # or "gemini-1.5-pro" for better quality


def get_model(model_name: str = MODEL_NAME):
    """
    Get configured Gemini model instance
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        Configured model instance
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured")
    
    if USE_NEW_SDK:
        return model_name  # With new SDK, we use model name directly
    else:
        model = genai.GenerativeModel(model_name)
        return model


async def generate_text(
    prompt: str,
    model_name: str = MODEL_NAME,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """
    Generate text using Gemini model
    
    Args:
        prompt: Input prompt
        model_name: Model to use
        temperature: Sampling temperature (0.0 to 1.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text
    """
    try:
        if USE_NEW_SDK and client:
            # New SDK approach
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text
        else:
            # Old SDK approach
            model = get_model(model_name)
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
    
    except Exception as e:
        print(f"❌ Error generating text: {e}")
        raise


async def generate_text_with_json(
    prompt: str,
    model_name: str = MODEL_NAME,
    temperature: float = 0.3
) -> str:
    """
    Generate text with JSON output format
    Useful for structured data extraction
    
    Args:
        prompt: Input prompt (should specify JSON format)
        model_name: Model to use
        temperature: Lower temperature for more consistent JSON
        
    Returns:
        Generated JSON string
    """
    try:
        if USE_NEW_SDK and client:
            # New SDK approach
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    response_mime_type="application/json"
                )
            )
            return response.text
        else:
            # Old SDK approach
            model = get_model(model_name)
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json"
            )
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
    
    except Exception as e:
        print(f"❌ Error generating JSON: {e}")
        raise


async def analyze_text_batch(
    texts: list[str],
    prompt_template: str,
    model_name: str = MODEL_NAME
) -> list[str]:
    """
    Analyze multiple texts using the same prompt template
    
    Args:
        texts: List of texts to analyze
        prompt_template: Template with {text} placeholder
        model_name: Model to use
        
    Returns:
        List of analysis results
    """
    results = []
    
    for text in texts:
        try:
            prompt = prompt_template.format(text=text)
            result = await generate_text(prompt, model_name)
            results.append(result)
        except Exception as e:
            print(f"⚠️ Error analyzing text: {e}")
            results.append(None)
    
    return results


def check_api_key() -> bool:
    """
    Check if Google API key is configured
    
    Returns:
        True if API key is configured, False otherwise
    """
    return GOOGLE_API_KEY is not None and GOOGLE_API_KEY != ""


# Prompt templates
ENTITY_EXTRACTION_PROMPT = """
You are an AI assistant specialized in wildlife smuggling analysis.

Extract the following information from the text below:
1. Animal species or wildlife products mentioned
2. Specific location details (city, state, country)
3. Key entities (people, organizations, vehicles)
4. Important keywords

Text: {text}

Return the information in this JSON format:
{{
    "animals": ["animal1", "animal2"],
    "location": "specific location",
    "entities": ["entity1", "entity2"],
    "keywords": ["keyword1", "keyword2"]
}}
"""

SUMMARY_PROMPT = """
You are an AI assistant specialized in wildlife smuggling analysis.

Write a brief 2-3 sentence summary of the following wildlife smuggling incident.
Focus on: what was seized, where, and the outcome.

Text: {text}

Summary:
"""

PATTERN_ANALYSIS_PROMPT = """
You are an AI assistant specialized in wildlife smuggling analysis.

Analyze the following incidents and identify patterns:
- Common smuggling routes
- Frequently smuggled animals/products
- Typical modus operandi
- Temporal patterns

Incidents:
{incidents}

Provide a detailed analysis:
"""