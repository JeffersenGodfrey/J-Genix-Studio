from typing import Dict, Any, Optional, Union
import requests
import json

def generate_hd_image(
    prompt: str,
    api_key: str,
    model_version: str = "2.2",
    num_results: int = 1,
    aspect_ratio: str = "1:1",
    sync: bool = True,
    seed: Optional[int] = None,
    negative_prompt: str = "",
    steps_num: Optional[int] = None,
    text_guidance_scale: Optional[float] = None,
    medium: Optional[str] = None,
    prompt_enhancement: bool = False,
    enhance_image: bool = False,
    content_moderation: bool = False,
    ip_signal: bool = False
) -> Dict[str, Any]:
    """Generate HD image from prompt using Bria's text-to-image API.
    
    Args:
        prompt: The prompt to generate images from
        api_key: API key for authentication
        model_version: Model version to use (default: "2.2")
        num_results: Number of images to generate (1-4)
        aspect_ratio: Image aspect ratio ("1:1", "2:3", "3:2", etc.)
        sync: Whether to wait for results or get URLs immediately
        seed: Optional seed for reproducible results
        negative_prompt: Elements to exclude from generation
        steps_num: Number of refinement iterations (20-50)
        text_guidance_scale: How closely to follow text (1-10)
        medium: Generation medium ("photography" or "art")
        prompt_enhancement: Whether to enhance the prompt
        enhance_image: Whether to enhance image quality
        content_moderation: Whether to enable content moderation
        ip_signal: Whether to flag potential IP content
    """
    
    if not prompt:
        raise ValueError("Prompt is required for image generation")
    
    # Build request data with only provided parameters
    data = {
        "prompt": prompt,
        "num_results": max(1, min(num_results, 4)),
        "sync": sync,
        "negative_prompt": negative_prompt
    }
    
    # Add optional parameters only if they have valid values
    if aspect_ratio:
        data["aspect_ratio"] = aspect_ratio
    if seed is not None:
        data["seed"] = seed
    if steps_num is not None:
        data["steps_num"] = max(20, min(steps_num, 50))
    if text_guidance_scale is not None:
        data["text_guidance_scale"] = max(1.0, min(text_guidance_scale, 10.0))
    if medium:
        data["medium"] = medium
    if prompt_enhancement:
        data["prompt_enhancement"] = prompt_enhancement
    if enhance_image:
        data["enhance_image"] = enhance_image
    if content_moderation:
        data["content_moderation"] = content_moderation
    if ip_signal:
        data["ip_signal"] = ip_signal
    
    url = f"https://engine.prod.bria-api.com/v1/text-to-image/hd/{model_version}"
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        return response.json()
        
    except Exception as e:
        raise Exception(f"HD image generation failed: {str(e)}") 