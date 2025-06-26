"""
Brand Kit Generator & Manager
Handles brand identity creation, color extraction, and brand asset management
"""

import requests
from PIL import Image
import io
import colorsys
from collections import Counter
import streamlit as st
from typing import Dict, List, Tuple, Optional
import json
import base64


def extract_colors_from_image(image_url: str, num_colors: int = 5) -> List[str]:
    """Extract dominant colors from an image URL"""
    try:
        # Download image
        response = requests.get(image_url)
        if response.status_code != 200:
            return ["#667eea", "#764ba2", "#f093fb", "#28a745", "#dc3545"]  # Default colors

        # Open and process image
        image = Image.open(io.BytesIO(response.content))
        image = image.convert('RGB')

        # Resize for faster processing
        image = image.resize((150, 150))

        # Get all pixels
        pixels = list(image.getdata())

        # Count color frequencies
        color_counts = Counter(pixels)

        # Get most common colors
        common_colors = color_counts.most_common(num_colors * 3)  # Get more to filter

        # Convert to hex and filter similar colors
        hex_colors = []
        for (r, g, b), count in common_colors:
            hex_color = f"#{r:02x}{g:02x}{b:02x}"

            # Skip very dark or very light colors
            brightness = (r + g + b) / 3
            if brightness < 30 or brightness > 225:
                continue

            # Skip if too similar to existing colors
            is_similar = False
            for existing_color in hex_colors:
                if color_similarity(hex_color, existing_color) > 0.8:
                    is_similar = True
                    break

            if not is_similar:
                hex_colors.append(hex_color)

            if len(hex_colors) >= num_colors:
                break

        # Fill with default colors if needed
        default_colors = ["#667eea", "#764ba2", "#f093fb", "#28a745", "#dc3545"]
        while len(hex_colors) < num_colors:
            for color in default_colors:
                if color not in hex_colors:
                    hex_colors.append(color)
                    break

        return hex_colors[:num_colors]

    except Exception as e:
        print(f"Error extracting colors: {str(e)}")
        return ["#667eea", "#764ba2", "#f093fb", "#28a745", "#dc3545"]


def color_similarity(color1: str, color2: str) -> float:
    """Calculate similarity between two hex colors (0-1, 1 being identical)"""
    try:
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

        # Calculate Euclidean distance
        distance = ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)**0.5

        # Normalize to 0-1 scale (max distance is ~441 for RGB)
        similarity = 1 - (distance / 441)
        return max(0, similarity)

    except:
        return 0

def create_brand_kit(logo_url: str, brand_name: str, tagline: str = "") -> Dict:
    """Create a complete brand kit from a logo"""
    try:
        # Extract colors from logo
        colors = extract_colors_from_image(logo_url, 5)

        # Create brand kit
        brand_kit = {
            "brand_name": brand_name,
            "tagline": tagline,
            "logo_url": logo_url,
            "primary_color": colors[0] if colors else "#667eea",
            "secondary_color": colors[1] if len(colors) > 1 else "#764ba2",
            "accent_color": colors[2] if len(colors) > 2 else "#f093fb",
            "success_color": "#28a745",
            "warning_color": "#ffc107",
            "error_color": "#dc3545",
            "color_palette": colors,
            "fonts": {
                "primary": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                "secondary": "Roboto, Arial, sans-serif",
                "heading": "Montserrat, sans-serif"
            },
            "created_at": st.session_state.get('current_time', 'Unknown')
        }

        return brand_kit

    except Exception as e:
        st.error(f"Error creating brand kit: {str(e)}")
        return None


def apply_brand_to_prompt(prompt: str, brand_kit: Dict) -> str:
    """Apply brand colors and style to an image generation prompt"""
    if not brand_kit:
        return prompt

    try:
        brand_name = brand_kit.get("brand_name", "")
        primary_color = brand_kit.get("primary_color", "")
        secondary_color = brand_kit.get("secondary_color", "")
        accent_color = brand_kit.get("accent_color", "")
        color_palette = brand_kit.get("color_palette", [])

        # Enhanced brand-specific styling to prompt
        brand_additions = []

        # Add specific color instructions for better AI understanding
        if primary_color:
            brand_additions.append(f"dominant color scheme using {primary_color}")
        if secondary_color:
            brand_additions.append(f"complementary colors including {secondary_color}")
        if accent_color:
            brand_additions.append(f"accent highlights in {accent_color}")

        # Add color palette if available
        if color_palette and len(color_palette) > 2:
            palette_colors = ", ".join(color_palette[:4])  # Use first 4 colors
            brand_additions.append(f"color palette: {palette_colors}")

        # Add brand identity
        if brand_name:
            brand_additions.append(f"consistent with {brand_name} brand aesthetic")

        # Enhanced prompt construction for better color application
        if brand_additions:
            enhanced_prompt = f"{prompt}, featuring {', '.join(brand_additions)}, professional brand-consistent styling, cohesive color scheme"
            return enhanced_prompt

        return prompt

    except Exception as e:
        print(f"Error applying brand to prompt: {str(e)}")
        return prompt

def save_brand_kit(brand_kit: Dict) -> bool:
    """Save brand kit to session state"""
    try:
        if 'brand_kits' not in st.session_state:
            st.session_state.brand_kits = {}

        brand_name = brand_kit.get('brand_name', 'Default')
        st.session_state.brand_kits[brand_name] = brand_kit
        st.session_state.active_brand_kit = brand_kit

        return True

    except Exception as e:
        st.error(f"Error saving brand kit: {str(e)}")
        return False


def load_brand_kit(brand_name: str) -> Optional[Dict]:
    """Load brand kit from session state"""
    try:
        if 'brand_kits' not in st.session_state:
            return None

        return st.session_state.brand_kits.get(brand_name)

    except Exception as e:
        st.error(f"Error loading brand kit: {str(e)}")
        return None


def get_available_brand_kits() -> List[str]:
    """Get list of available brand kit names"""
    try:
        if 'brand_kits' not in st.session_state:
            return []

        return list(st.session_state.brand_kits.keys())

    except Exception as e:
        return []


def validate_brand_kit(brand_kit: Dict) -> Tuple[bool, str]:
    """Validate brand kit data"""
    if not brand_kit:
        return False, "Brand kit is empty"

    required_fields = ['brand_name', 'primary_color']
    for field in required_fields:
        if not brand_kit.get(field):
            return False, f"Missing required field: {field}"

    return True, "Brand kit is valid"
