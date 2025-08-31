"""
Model utilities for dynamically fetching available models from AI providers
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def get_openai_models() -> Dict[str, str]:
    """Fetch available OpenAI models dynamically"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found, returning empty model list")
            return {}
        
        client = OpenAI(api_key=api_key)
        models_response = client.models.list()
        
        # Filter and format models for chat completion
        chat_models = {}
        for model in models_response.data:
            model_id = model.id
            # Only include GPT models that are suitable for chat completion
            if any(prefix in model_id.lower() for prefix in ['gpt-4', 'gpt-3.5', 'o1']):
                # Format model display name
                display_name = model_id
                if 'gpt-4o' in model_id:
                    if 'mini' in model_id:
                        display_name = "GPT-4o Mini (Recommended)"
                    else:
                        display_name = "GPT-4o"
                elif 'gpt-4' in model_id:
                    display_name = f"GPT-{model_id.replace('gpt-', '').upper()}"
                elif 'gpt-3.5' in model_id:
                    display_name = f"GPT-{model_id.replace('gpt-', '').replace('-', ' ').title()}"
                elif 'o1' in model_id:
                    if 'pro' in model_id:
                        display_name = "O1-Pro"
                    elif 'mini' in model_id:
                        display_name = "O1-Mini" 
                    else:
                        display_name = "O1"
                
                chat_models[model_id] = display_name
        
        # Sort models by preference (recommended first)
        preferred_order = ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-4', 'o1-pro', 'o1-mini', 'gpt-3.5-turbo']
        sorted_models = {}
        
        # Add preferred models first
        for preferred in preferred_order:
            for model_id in chat_models:
                if preferred in model_id:
                    sorted_models[model_id] = chat_models[model_id]
                    break
        
        # Add remaining models
        for model_id, display_name in chat_models.items():
            if model_id not in sorted_models:
                sorted_models[model_id] = display_name
        
        return sorted_models
        
    except Exception as e:
        logger.error(f"Error fetching OpenAI models: {str(e)}")
        # Return fallback models
        return {
            "gpt-4o-mini": "GPT-4o Mini (Recommended)",
            "gpt-4o": "GPT-4o",
            "gpt-4": "GPT-4",
            "gpt-3.5-turbo": "GPT-3.5 Turbo"
        }


def get_gemini_models() -> Dict[str, str]:
    """Fetch available Gemini models dynamically"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found, returning empty model list")
            return {}
        
        genai.configure(api_key=api_key)
        
        # List available models
        models = genai.list_models()
        
        # Filter models for text generation
        text_models = {}
        for model in models:
            model_name = model.name.replace('models/', '')
            # Only include Gemini models suitable for text generation
            if 'gemini' in model_name.lower() and 'generatecontent' in str(model.supported_generation_methods):
                # Format display name
                display_name = model_name
                if 'gemini-2.5-pro' in model_name:
                    display_name = "Gemini 2.5 Pro (Recommended)"
                elif 'gemini-2.5-flash' in model_name:
                    display_name = "Gemini 2.5 Flash"
                elif 'gemini-2.0' in model_name:
                    if 'flash' in model_name:
                        display_name = "Gemini 2.0 Flash"
                    elif 'pro' in model_name:
                        display_name = "Gemini 2.0 Pro"
                elif 'gemini-1.5' in model_name:
                    if 'pro' in model_name:
                        display_name = "Gemini 1.5 Pro"
                    elif 'flash' in model_name:
                        display_name = "Gemini 1.5 Flash"
                
                text_models[model_name] = display_name
        
        # Sort models by preference (recommended first)
        preferred_order = ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash-exp', 'gemini-2.0-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']
        sorted_models = {}
        
        # Add preferred models first
        for preferred in preferred_order:
            for model_id in text_models:
                if preferred in model_id:
                    sorted_models[model_id] = text_models[model_id]
                    break
        
        # Add remaining models
        for model_id, display_name in text_models.items():
            if model_id not in sorted_models:
                sorted_models[model_id] = display_name
        
        return sorted_models
        
    except Exception as e:
        logger.error(f"Error fetching Gemini models: {str(e)}")
        # Return fallback models
        return {
            "gemini-2.5-pro": "Gemini 2.5 Pro (Recommended)",
            "gemini-2.0-flash-exp": "Gemini 2.0 Flash Experimental",
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "gemini-1.5-flash": "Gemini 1.5 Flash"
        }


def get_available_models() -> Dict[str, Dict[str, str]]:
    """Get all available models for both providers"""
    return {
        "openai": get_openai_models(),
        "gemini": get_gemini_models()
    }


def get_default_model(provider: str) -> Optional[str]:
    """Get the default model for a provider"""
    models = get_available_models()
    provider_models = models.get(provider, {})
    
    if not provider_models:
        return None
    
    # Return the first model (should be the recommended one)
    return list(provider_models.keys())[0]