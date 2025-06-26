from typing import Dict, Any, Optional
import requests
import json

def enhance_prompt(
    api_key: str,
    prompt: str,
    **kwargs
) -> str:
    """
    Enhance a prompt using Bria AI's prompt enhancement service.
    
    Args:
        api_key: Bria AI API key
        prompt: Original prompt to enhance
        **kwargs: Additional parameters for the API
    
    Returns:
        Enhanced prompt string
    """
    url = "https://engine.prod.bria-api.com/v1/prompt_enhancer"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    data = {
        'prompt': prompt,
        **kwargs
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        result = response.json()
        return result.get("prompt variations", prompt)  # Return original prompt if enhancement fails
    except Exception as e:
        print(f"Error enhancing prompt: {str(e)}")
        return prompt  # Return original prompt on error 