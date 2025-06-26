from typing import Dict, Any, Optional, List
import requests
import base64

def lifestyle_shot_by_text(
    api_key: str,
    image_data: bytes,
    scene_description: str,
    placement_type: str = "original",
    num_results: int = 4,
    sync: bool = False,
    fast: bool = True,
    optimize_description: bool = True,
    original_quality: bool = False,
    exclude_elements: Optional[str] = None,
    shot_size: List[int] = [1000, 1000],
    manual_placement_selection: List[str] = ["upper_left"],
    padding_values: List[int] = [0, 0, 0, 0],
    foreground_image_size: Optional[List[int]] = None,
    foreground_image_location: Optional[List[int]] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False,
    sku: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a lifestyle shot using text description.
    
    Args:
        api_key: Bria AI API key
        image_data: Image data in bytes
        scene_description: Text description of the new scene
        placement_type: How to position the product ("original", "automatic", "manual_placement", "manual_padding", "custom_coordinates")
        num_results: Number of results to generate
        sync: Whether to wait for results
        fast: Whether to use fast mode
        optimize_description: Whether to optimize the scene description
        original_quality: Whether to maintain original image quality
        exclude_elements: Elements to exclude from generation
        shot_size: Size of the output image [width, height]
        manual_placement_selection: List of placement positions
        padding_values: Padding values [left, right, top, bottom]
        foreground_image_size: Size of foreground image [width, height]
        foreground_image_location: Position of foreground image [x, y]
        force_rmbg: Whether to force background removal
        content_moderation: Whether to enable content moderation
        sku: Optional SKU identifier
    """
    url = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_text"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Convert image to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Prepare request data
    data = {
        'file': image_base64,
        'scene_description': scene_description,
        'placement_type': placement_type,
        'num_results': num_results,
        'sync': sync,
        'fast': fast,
        'optimize_description': optimize_description,
        'original_quality': original_quality,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation
    }
    
    # Add optional parameters
    if exclude_elements and not fast:
        data['exclude_elements'] = exclude_elements
    
    if placement_type in ['automatic', 'manual_placement', 'custom_coordinates']:
        data['shot_size'] = shot_size
    
    if placement_type == 'manual_placement':
        data['manual_placement_selection'] = manual_placement_selection
    
    if placement_type == 'manual_padding':
        data['padding_values'] = padding_values
    
    if placement_type == 'custom_coordinates':
        if foreground_image_size:
            data['foreground_image_size'] = foreground_image_size
        if foreground_image_location:
            data['foreground_image_location'] = foreground_image_location
    
    if sku:
        data['sku'] = sku
    
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
        raise Exception(f"Lifestyle shot generation failed: {str(e)}")

def lifestyle_shot_by_image(
    api_key: str,
    image_data: bytes,
    reference_image: bytes,
    placement_type: str = "original",
    num_results: int = 4,
    sync: bool = False,
    original_quality: bool = False,
    shot_size: List[int] = [1000, 1000],
    manual_placement_selection: List[str] = ["upper_left"],
    padding_values: List[int] = [0, 0, 0, 0],
    foreground_image_size: Optional[List[int]] = None,
    foreground_image_location: Optional[List[int]] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False,
    sku: Optional[str] = None,
    enhance_ref_image: bool = True,
    ref_image_influence: float = 1.0
) -> Dict[str, Any]:
    """
    Generate a lifestyle shot using a reference image.
    """
    url = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_image"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Convert images to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    reference_base64 = base64.b64encode(reference_image).decode('utf-8')
    
    # Prepare request data
    data = {
        'file': image_base64,
        'ref_image_file': reference_base64,
        'placement_type': placement_type,
        'num_results': num_results,
        'sync': sync,
        'original_quality': original_quality,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation,
        'enhance_ref_image': enhance_ref_image,
        'ref_image_influence': ref_image_influence
    }
    
    # Add optional parameters
    if placement_type in ['automatic', 'manual_placement', 'custom_coordinates']:
        data['shot_size'] = shot_size
    
    if placement_type == 'manual_placement':
        data['manual_placement_selection'] = manual_placement_selection
    
    if placement_type == 'manual_padding':
        data['padding_values'] = padding_values
    
    if placement_type == 'custom_coordinates':
        if foreground_image_size:
            data['foreground_image_size'] = foreground_image_size
        if foreground_image_location:
            data['foreground_image_location'] = foreground_image_location
    
    if sku:
        data['sku'] = sku
    
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
        raise Exception(f"Lifestyle shot generation failed: {str(e)}") 