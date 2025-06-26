from typing import Dict, Any, Optional
import requests
import base64

def generative_fill(
    api_key: str,
    image_data: bytes,
    mask_data: bytes,
    prompt: str,
    negative_prompt: Optional[str] = None,
    num_results: int = 4,
    sync: bool = False,
    seed: Optional[int] = None,
    content_moderation: bool = False,
    mask_type: str = "manual"
) -> Dict[str, Any]:
    """
    Generate content in a masked area of an image using a text prompt.
    
    Args:
        api_key: Bria AI API key
        image_data: Image data in bytes
        mask_data: Mask image data in bytes
        prompt: Description of what to generate in the masked area
        negative_prompt: Description of what to avoid (optional)
        num_results: Number of variations to generate (1-4)
        sync: Whether to wait for results
        seed: Optional seed for reproducible results
        content_moderation: Whether to enable content moderation
        mask_type: Type of mask ('manual' or 'automatic')
    """
    url = "https://engine.prod.bria-api.com/v1/gen_fill"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Convert image and mask to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    mask_base64 = base64.b64encode(mask_data).decode('utf-8')
    
    # Prepare request data
    data = {
        'file': image_base64,
        'mask_file': mask_base64,
        'mask_type': mask_type,
        'prompt': prompt,
        'num_results': num_results,
        'sync': sync,
        'content_moderation': content_moderation
    }
    
    # Add optional parameters
    if negative_prompt:
        data['negative_prompt'] = negative_prompt
    if seed is not None:
        data['seed'] = seed
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        return response.json()
    except Exception as e:
        raise Exception(f"Generative fill failed: {str(e)}") 