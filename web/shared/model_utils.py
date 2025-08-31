"""
Model utilities for dynamically fetching available models from AI providers
"""

from src.logger import logger
from typing import Dict, Optional

def get_openai_models() -> Dict[str, str]:
    """Return curated OpenAI models suitable for factsheet generation"""
    models = {
        'gpt-5': 'gpt-5-2025-08-07', 
        'gpt-5-nano': 'gpt-5-nano-2025-08-07',
        'gpt-5-mini': 'gpt-5-mini-2025-08-07',
        'gpt-4o-mini': 'gpt-4o-mini-2024-07-18',
        'gpt-4o': 'gpt-4o-2024-11-20',
        'gpt-4-turbo': 'gpt-4-turbo-2024-04-09',
    }
    
    logger.info(f"Using {len(models)} curated models: {list(models.keys())}")
    return models

def get_default_model() -> Optional[str]:
    """Get the default OpenAI model"""
    models = get_openai_models()
    
    if not models:
        return None
    
    return list(models.keys())[0]