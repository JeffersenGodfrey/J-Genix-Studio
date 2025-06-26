from typing import Dict, Any, Optional
from services import (
    lifestyle_shot_by_text,
    add_shadow,
    create_packshot,
    generate_hd_image
)

def generate_ad_set(
    api_key: str,
    image: Optional[bytes] = None,
    prompt: Optional[str] = None,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate a set of product ads based on configuration.
    """
    if not config:
        config = {}
    
    result = {}
    
    # Generate HD image if prompt provided
    if prompt and not image:
        hd_response = generate_hd_image(
            api_key=api_key,
            prompt=prompt,
            num_results=config.get("num_results", 1),
            aspect_ratio=config.get("aspect_ratio", "1:1"),
            sync=config.get("sync", True)
        )
        result["hd_image"] = hd_response
        image = hd_response.get("result_url")
    
    # Create packshot if requested
    if config.get("create_packshot", False) and image:
        packshot_response = create_packshot(
            api_key=api_key,
            image_data=image,
            background_color=config.get("background_color", "#FFFFFF")
        )
        result["packshot"] = packshot_response
    
    # Add shadow if requested
    if config.get("add_shadow", False) and image:
        shadow_response = add_shadow(
            api_key=api_key,
            image_data=image,
            shadow_type=config.get("shadow_type", "natural")
        )
        result["shadow"] = shadow_response
    
    # Create lifestyle shot if requested
    if config.get("lifestyle_shot", False) and image:
        lifestyle_response = lifestyle_shot_by_text(
            api_key=api_key,
            image_data=image,
            scene_description=config.get("scene_description", ""),
            num_results=config.get("num_results", 1)
        )
        result["lifestyle"] = lifestyle_response
    
    return result 