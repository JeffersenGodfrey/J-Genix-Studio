from typing import Dict, Any, Optional, List
import requests
import json
import random
import re

def generate_logo(
    prompt: str,
    api_key: str,
    logo_style: str = "modern",
    logo_type: str = "combination",
    color_scheme: str = "professional",
    model_version: str = "2.2",
    num_results: int = 1,
    aspect_ratio: str = "1:1",
    sync: bool = True,
    seed: Optional[int] = None,
    negative_prompt: str = "",
    steps_num: Optional[int] = None,
    text_guidance_scale: Optional[float] = None,
    enhance_image: bool = True,
    content_moderation: bool = True,
    ensure_variety: bool = True
) -> Dict[str, Any]:
    """
    Generate professional logos using Bria's text-to-image API with logo-specific optimizations.
    
    Args:
        prompt: The base prompt for logo generation
        api_key: API key for authentication
        logo_style: Style of logo (modern, minimalist, vintage, corporate, creative, tech)
        logo_type: Type of logo (text_based, icon_based, combination)
        color_scheme: Color scheme preference (professional, vibrant, monochrome, custom)
        model_version: Model version to use (default: "2.2")
        num_results: Number of logos to generate (1-4)
        aspect_ratio: Logo aspect ratio ("1:1", "16:9", "4:3")
        sync: Whether to wait for results or get URLs immediately
        seed: Optional seed for reproducible results (auto-randomized for variety)
        negative_prompt: Elements to exclude from generation
        steps_num: Number of refinement iterations (30-50 for logos)
        text_guidance_scale: How closely to follow text (7-9 for logos)
        enhance_image: Whether to enhance image quality
        content_moderation: Whether to enable content moderation
        ensure_variety: Whether to randomize parameters for unique results
    
    Returns:
        Dict containing the API response with generated logo URLs
    """
    
    if not prompt:
        raise ValueError("Prompt is required for logo generation")
    
    # Extract company name for accurate text rendering
    company_name = _extract_company_name(prompt)
    print(f"Logo generation for company: '{company_name}'")

    # Build logo-specific prompt with style and type modifiers
    enhanced_prompt = _build_logo_prompt(prompt, logo_style, logo_type, color_scheme)
    
    # Ensure variety by randomizing seed and some parameters if requested
    if ensure_variety and seed is None:
        seed = random.randint(1, 1000000)
    
    # Logo-optimized parameters
    logo_steps = steps_num or random.randint(35, 45) if ensure_variety else 40
    logo_guidance = text_guidance_scale or (random.uniform(7.5, 8.5) if ensure_variety else 8.0)
    
    # Build request data with logo-specific optimizations
    data = {
        "prompt": enhanced_prompt,
        "num_results": max(1, min(num_results, 4)),
        "sync": sync,
        "negative_prompt": _build_logo_negative_prompt(negative_prompt),
        "medium": "art",  # Art medium works better for logos than photography
        "steps_num": logo_steps,
        "text_guidance_scale": logo_guidance,
        "enhance_image": enhance_image,
        "content_moderation": content_moderation
    }
    
    # Add optional parameters
    if aspect_ratio:
        data["aspect_ratio"] = aspect_ratio
    if seed is not None:
        data["seed"] = seed
    
    url = f"https://engine.prod.bria-api.com/v1/text-to-image/hd/{model_version}"
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Making logo generation request to: {url}")
        print(f"Enhanced prompt: {enhanced_prompt}")
        print(f"Logo parameters - Style: {logo_style}, Type: {logo_type}, Colors: {color_scheme}")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        result = response.json()
        
        # Add metadata about the logo generation
        if isinstance(result, dict) and "result" in result:
            result["logo_metadata"] = {
                "style": logo_style,
                "type": logo_type,
                "color_scheme": color_scheme,
                "seed_used": seed,
                "enhanced_prompt": enhanced_prompt
            }
        
        return result
        
    except Exception as e:
        raise Exception(f"Logo generation failed: {str(e)}")

def _extract_company_name(prompt: str) -> str:
    """Extract the company name from the user prompt with advanced parsing"""

    if not prompt or not prompt.strip():
        return "Company"

    # Clean the prompt
    cleaned_prompt = prompt.strip()

    # Special case: If it's a single word that looks like a company name, use it directly
    words = cleaned_prompt.split()
    if len(words) == 1 and len(words[0]) > 1 and words[0].isalpha():
        return words[0]

    # Pattern 1: Look for quoted company names
    quoted_match = re.search(r'["\']([^"\']+)["\']', cleaned_prompt)
    if quoted_match:
        return quoted_match.group(1).strip()

    # Pattern 2: Look for "company name is X" or "brand name is X"
    name_pattern = re.search(r'(?:company|brand|business)\s+(?:name|called)\s+(?:is\s+)?([A-Za-z0-9\s&]+?)(?:\s|,|$)', cleaned_prompt, re.IGNORECASE)
    if name_pattern:
        return name_pattern.group(1).strip()

    # Pattern 3: Look for "for X company" or "for X brand"
    for_pattern = re.search(r'for\s+([A-Za-z0-9\s&]+?)\s+(?:company|brand|business|corp|inc|llc)', cleaned_prompt, re.IGNORECASE)
    if for_pattern:
        return for_pattern.group(1).strip()

    # Pattern 4: Extract first 1-3 words that could be company names
    words = cleaned_prompt.split()
    company_words = []

    for word in words[:5]:  # Check first 5 words
        # Skip common descriptive words
        if word.lower() in ['logo', 'design', 'for', 'company', 'brand', 'business', 'create', 'make', 'generate', 'a', 'an', 'the']:
            continue

        # Accept any word that could be a company name (including lowercase)
        if len(word) > 1 and word.isalpha():
            company_words.append(word)
        else:
            break  # Stop at first non-alphabetic word

    if company_words:
        company_name = ' '.join(company_words[:3])  # Max 3 words
        # Clean up common suffixes
        company_name = re.sub(r'\s+(inc|llc|corp|ltd|co)\.?$', '', company_name, flags=re.IGNORECASE)
        return company_name.strip()

    # Pattern 5: Fallback - take first word if it's reasonable length
    first_word = words[0] if words else "Company"
    if len(first_word) > 1 and first_word.isalpha():
        return first_word

    return "Company"

def validate_company_name_extraction(prompt: str) -> Dict[str, str]:
    """Validate and debug company name extraction"""
    extracted_name = _extract_company_name(prompt)

    return {
        "original_prompt": prompt,
        "extracted_company_name": extracted_name,
        "extraction_method": _get_extraction_method(prompt),
        "is_valid": len(extracted_name) > 0 and extracted_name != "Company"
    }

def _get_extraction_method(prompt: str) -> str:
    """Determine which method was used to extract the company name"""
    if not prompt or not prompt.strip():
        return "empty_prompt"

    cleaned_prompt = prompt.strip()

    if re.search(r'["\']([^"\']+)["\']', cleaned_prompt):
        return "quoted_name"
    elif re.search(r'(?:company|brand|business)\s+(?:name|called)\s+(?:is\s+)?([A-Za-z0-9\s&]+?)(?:\s|,|$)', cleaned_prompt, re.IGNORECASE):
        return "explicit_name_pattern"
    elif re.search(r'for\s+([A-Za-z0-9\s&]+?)\s+(?:company|brand|business|corp|inc|llc)', cleaned_prompt, re.IGNORECASE):
        return "for_company_pattern"
    else:
        return "capitalized_words"

def _build_logo_prompt(base_prompt: str, style: str, logo_type: str, color_scheme: str) -> str:
    """Build an enhanced prompt specifically optimized for logo generation with accurate text rendering"""

    # Style modifiers
    style_modifiers = {
        "modern": "modern, clean, contemporary, sleek",
        "minimalist": "minimalist, simple, clean lines, geometric",
        "vintage": "vintage, retro, classic, timeless",
        "corporate": "corporate, professional, business, formal",
        "creative": "creative, artistic, unique, innovative",
        "tech": "tech, digital, futuristic, high-tech",
        "elegant": "elegant, sophisticated, refined, luxury",
        "playful": "playful, fun, friendly, approachable"
    }
    
    # Logo type modifiers
    type_modifiers = {
        "text_based": "typography-focused, wordmark, text logo, lettering",
        "icon_based": "icon, symbol, pictorial mark, graphic symbol",
        "combination": "logo with text and icon, combination mark, text and symbol"
    }
    
    # Color scheme modifiers
    color_modifiers = {
        "professional": "professional color palette, business colors",
        "vibrant": "vibrant colors, bold color scheme, energetic colors",
        "monochrome": "monochrome, black and white, single color",
        "earth_tones": "earth tones, natural colors, organic palette",
        "tech_colors": "tech colors, blue and gray, digital palette",
        "luxury": "luxury colors, gold and black, premium palette"
    }
    
    # Extract company name with advanced parsing
    company_name = _extract_company_name(base_prompt)

    # Build the enhanced prompt with maximum emphasis on text accuracy
    prompt_parts = [
        f"professional logo design with text '{company_name}'",
        f"exact text '{company_name}' spelled correctly",
        f"company name '{company_name}' in clear readable typography",
        f"text '{company_name}' must be spelled exactly as written",
        style_modifiers.get(style, "modern, clean"),
        type_modifiers.get(logo_type, "combination mark"),
        color_modifiers.get(color_scheme, "professional color palette"),
        "vector style logo design, scalable graphics",
        "professional typography, clear letterforms",
        "accurate text rendering, perfect spelling",
        "crisp text edges, high contrast lettering",
        "business logo, corporate branding",
        "text must be legible and correctly spelled"
    ]
    
    return ", ".join(prompt_parts)

def _build_logo_negative_prompt(base_negative: str) -> str:
    """Build negative prompt to avoid common logo generation issues"""
    
    logo_negative_terms = [
        # Quality issues
        "blurry", "pixelated", "low quality", "distorted", "fuzzy",
        "cluttered", "busy", "complex background", "photographic",
        "realistic photo", "3D render", "overly detailed",
        "multiple logos", "watermark", "copyright",

        # Text and typography issues
        "misspelled text", "incorrect spelling", "garbled text",
        "unreadable text", "distorted letters", "broken typography",
        "wrong spelling", "scrambled letters", "illegible text",
        "corrupted text", "malformed letters", "text artifacts",
        "gibberish text", "nonsense words", "random characters",
        "backwards text", "upside down text", "rotated letters",
        "overlapping text", "cut off text", "partial letters",
        "blurred text", "faded text", "unclear lettering",
        "wrong font", "inconsistent typography", "mixed fonts",

        # Layout issues
        "text overlay", "frame", "border", "multiple text elements",
        "scattered text", "floating letters", "disconnected text",
        "text outside logo", "misaligned text", "cropped text"
    ]
    
    if base_negative:
        return f"{base_negative}, {', '.join(logo_negative_terms)}"
    else:
        return ", ".join(logo_negative_terms)

def get_logo_style_options() -> List[Dict[str, str]]:
    """Get available logo style options with descriptions"""
    return [
        {"value": "modern", "label": "Modern", "description": "Clean, contemporary design"},
        {"value": "minimalist", "label": "Minimalist", "description": "Simple, geometric shapes"},
        {"value": "vintage", "label": "Vintage", "description": "Retro, classic styling"},
        {"value": "corporate", "label": "Corporate", "description": "Professional, business-focused"},
        {"value": "creative", "label": "Creative", "description": "Artistic, unique approach"},
        {"value": "tech", "label": "Tech", "description": "Digital, futuristic feel"},
        {"value": "elegant", "label": "Elegant", "description": "Sophisticated, luxury appeal"},
        {"value": "playful", "label": "Playful", "description": "Fun, friendly, approachable"}
    ]

def get_logo_type_options() -> List[Dict[str, str]]:
    """Get available logo type options with descriptions"""
    return [
        {"value": "combination", "label": "Combination", "description": "Text + Icon (most versatile)"},
        {"value": "text_based", "label": "Text-Based", "description": "Typography-focused wordmark"},
        {"value": "icon_based", "label": "Icon-Based", "description": "Symbol or pictorial mark"}
    ]

def get_color_scheme_options() -> List[Dict[str, str]]:
    """Get available color scheme options with descriptions"""
    return [
        {"value": "professional", "label": "Professional", "description": "Business-appropriate colors"},
        {"value": "vibrant", "label": "Vibrant", "description": "Bold, energetic colors"},
        {"value": "monochrome", "label": "Monochrome", "description": "Black, white, and grays"},
        {"value": "earth_tones", "label": "Earth Tones", "description": "Natural, organic colors"},
        {"value": "tech_colors", "label": "Tech Colors", "description": "Blue, gray, digital palette"},
        {"value": "luxury", "label": "Luxury", "description": "Premium gold, black, silver"}
    ]

def validate_logo_prompt(prompt: str, is_enhanced: bool = False) -> tuple[bool, str]:
    """Validate logo generation prompt and provide suggestions"""

    if not prompt or len(prompt.strip()) < 2:
        return False, "Please enter a company or brand name for logo generation"

    # ALWAYS allow prompts up to 500 characters for logo generation
    # This bypasses the original/enhanced distinction that was causing issues
    max_length = 500

    if len(prompt) > max_length:
        return False, f"Prompt is too long. Please keep it under {max_length} characters for best results"

    # Allow more flexible input - only check for obvious spam/inappropriate content
    spam_terms = ["spam", "test123", "asdf", "qwerty"]
    if any(term in prompt.lower() for term in spam_terms):
        return False, "Please enter a real company or brand name"

    # Provide helpful suggestions
    suggestions = []
    if len(prompt.split()) == 1:
        suggestions.append("💡 Consider adding your industry (e.g., 'TechCorp software company')")

    if not any(word in prompt.lower() for word in ["company", "corp", "inc", "llc", "business", "studio", "group", "services"]):
        suggestions.append("💡 You can include business type or industry for better results")

    return True, ". ".join(suggestions) if suggestions else "Prompt looks good!"

def enhance_logo_prompt(base_prompt: str, api_key: str) -> str:
    """
    Enhance a logo prompt using AI or rule-based enhancement.
    This function creates a more detailed, professional prompt for logo generation.
    """
    if not base_prompt or not base_prompt.strip():
        raise ValueError("Base prompt cannot be empty")

    if not api_key or not api_key.strip():
        print("No API key provided, using rule-based enhancement")
        return _rule_based_logo_enhancement(base_prompt)

    try:
        # First, try to use the Bria AI prompt enhancer
        from .prompt_enhancement import enhance_prompt

        # Create a logo-specific context for enhancement
        logo_context = f"Create a professional logo design prompt for: {base_prompt}"
        enhanced = enhance_prompt(api_key, logo_context)

        # If enhancement worked and returned something different, use it
        if enhanced and enhanced != logo_context and len(enhanced) > len(logo_context):
            print(f"AI enhancement successful: {len(enhanced)} chars")

            # If AI enhancement is too long, try to trim it or use rule-based
            if len(enhanced) > 450:
                print(f"AI enhancement too long ({len(enhanced)} chars), using rule-based")
                return _rule_based_logo_enhancement(base_prompt)

            return enhanced
        else:
            print("AI enhancement returned similar result, using rule-based")
            # Fall back to rule-based enhancement
            return _rule_based_logo_enhancement(base_prompt)

    except Exception as e:
        print(f"AI enhancement failed, using rule-based: {str(e)}")
        # Fall back to rule-based enhancement
        return _rule_based_logo_enhancement(base_prompt)

def _rule_based_logo_enhancement(base_prompt: str) -> str:
    """
    Rule-based logo prompt enhancement when AI enhancement fails.
    Generates concise, optimized prompts under 450 characters.
    """
    # Parse the input to extract company name and preferences
    prompt_lower = base_prompt.lower()

    # Extract company name (usually the first part)
    parts = base_prompt.split(',')
    company_name = parts[0].strip()

    # Build enhanced prompt with shorter, more focused terms
    enhanced_parts = [f"professional logo for {company_name}"]

    # Add style preferences if mentioned (shorter keywords)
    style_keywords = {
        'modern': 'modern, sleek',
        'minimalist': 'minimalist, clean',
        'vintage': 'vintage, classic',
        'corporate': 'corporate, professional',
        'creative': 'creative, artistic',
        'tech': 'tech, digital',
        'elegant': 'elegant, sophisticated',
        'playful': 'playful, friendly'
    }

    for style, keywords in style_keywords.items():
        if style in prompt_lower:
            enhanced_parts.append(keywords)
            break

    # Add color preferences if mentioned (shorter descriptions)
    color_keywords = {
        'blue': 'blue colors',
        'red': 'red colors',
        'green': 'green colors',
        'black': 'black and white',
        'gold': 'gold accents',
        'colorful': 'vibrant colors',
        'monochrome': 'monochrome'
    }

    for color, description in color_keywords.items():
        if color in prompt_lower:
            enhanced_parts.append(description)
            break

    # Add essential professional terms (shorter list)
    enhanced_parts.extend([
        "vector design",
        "scalable",
        "brand identity",
        "commercial quality"
    ])

    # Join and ensure it's under 450 characters
    result = ", ".join(enhanced_parts)

    # If still too long, trim to essential parts
    if len(result) > 450:
        essential_parts = [enhanced_parts[0]]  # Company name
        if len(enhanced_parts) > 1:
            essential_parts.append(enhanced_parts[1])  # Style
        essential_parts.extend(["vector design", "professional"])
        result = ", ".join(essential_parts)

    return result

def get_logo_generation_tips() -> List[str]:
    """Get tips for better logo generation results"""
    return [
        "💡 Include company name + industry (e.g., 'TechCorp software company')",
        "🎨 Add style preferences (e.g., 'modern and professional', 'vintage feel')",
        "🌈 Specify color preferences (e.g., 'blue colors', 'warm tones', 'monochrome')",
        "✨ Use prompt enhancement to optimize your description",
        "🔄 Generate multiple variations to compare different approaches",
        "📐 Square (1:1) aspect ratio works best for most logo applications",
        "🎯 Be specific but concise - include what matters most to your brand"
    ]
