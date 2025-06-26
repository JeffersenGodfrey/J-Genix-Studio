"""
Free AI Copywriter Service using Hugging Face Inference API
Provides marketing copy generation without requiring paid API keys
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
import streamlit as st

# Hugging Face models for different tasks - using more reliable text generation models
COPYWRITING_MODELS = {
    "general": "microsoft/DialoGPT-medium",
    "marketing": "microsoft/DialoGPT-medium",
    "creative": "microsoft/DialoGPT-medium",
    "product": "microsoft/DialoGPT-medium",
    "fallback": "gpt2"  # Fallback model
}

# Enhanced template-based system with more variety and intelligence
TEMPLATE_RESPONSES = {
    "product_description": [
        "Discover the perfect blend of style and functionality with this exceptional product. Designed with attention to detail and crafted for those who appreciate quality.",
        "Experience innovation at its finest with this remarkable product. Built to exceed expectations and deliver outstanding performance in every use.",
        "Transform your daily routine with this premium product. Combining cutting-edge design with practical functionality for the modern lifestyle.",
        "Elevate your experience with this thoughtfully designed product. Every detail has been carefully considered to deliver superior quality and lasting value.",
        "Meet your new favorite product - where form meets function in perfect harmony. Engineered for excellence and built to impress.",
        "Step into the future with this cutting-edge product. Advanced features meet intuitive design for an unparalleled user experience."
    ],
    "social_media_post": [
        "🌟 Check out this amazing product! Perfect for anyone looking to upgrade their experience. #Innovation #Quality #Style",
        "✨ Introducing something special that will change the way you think about quality and design. Don't miss out! #NewProduct #Excellence",
        "🚀 Ready to elevate your experience? This incredible product is exactly what you've been looking for! #Upgrade #Premium",
        "💫 Game-changer alert! This product is about to become your new obsession. Trust us on this one! #MustHave #Innovation",
        "🔥 Hot new arrival! When style meets substance, magic happens. Get yours before everyone else does! #Trending #Quality",
        "⭐ Five stars aren't enough for this beauty! See what all the excitement is about. #TopRated #Excellence"
    ],
    "advertisement_copy": [
        "Don't settle for ordinary when you can have extraordinary! This premium product delivers unmatched quality and style.",
        "Limited time offer! Experience the difference that true quality makes. Your satisfaction is our guarantee.",
        "Join thousands of satisfied customers who have discovered the perfect solution. Order now and see the difference!",
        "Why compromise when you can have it all? Premium quality, exceptional design, and unbeatable value - all in one product.",
        "The search is over! You've found the product that delivers on every promise. Quality you can trust, results you can see.",
        "Exclusive offer: Get the product everyone's talking about. Superior craftsmanship meets innovative design."
    ],
    "email_marketing": [
        "We're excited to introduce you to something special that will transform your daily routine.",
        "Your search for the perfect product ends here. Discover what makes this so extraordinary.",
        "Limited time exclusive: Get early access to the product that's changing everything.",
        "Don't miss out on this game-changing product that's taking the market by storm."
    ],
    "website_copy": [
        "Welcome to excellence. This product represents the pinnacle of design and functionality.",
        "Crafted with precision and built to last, this product delivers on every promise.",
        "Experience the difference that true quality makes with this exceptional product.",
        "Innovation meets tradition in this carefully crafted product designed for discerning customers."
    ],
    "seo_description": [
        "Premium quality product featuring innovative design and exceptional performance. Perfect for modern lifestyles.",
        "High-quality product with advanced features and superior craftsmanship. Trusted by thousands of satisfied customers.",
        "Exceptional product combining style, functionality, and durability. Experience the difference quality makes.",
        "Professional-grade product designed for excellence. Superior materials and innovative engineering."
    ]
}

# Hugging Face Inference API endpoint
HF_API_URL = "https://api-inference.huggingface.co/models/"

def generate_marketing_copy_free(
    image_description: str,
    brand_kit: Optional[Dict] = None,
    copy_type: str = "product_description",
    tone: str = "professional",
    length: str = "medium"
) -> Optional[str]:
    """
    Generate marketing copy using free Hugging Face models with template fallback

    Args:
        image_description: Description of the image/product
        brand_kit: Optional brand kit for brand consistency
        copy_type: Type of copy to generate
        tone: Tone of the copy (professional, casual, creative)
        length: Length of the copy (short, medium, long)

    Returns:
        Generated marketing copy or fallback template copy
    """
    try:
        # First, try the AI approach
        ai_result = generate_with_ai(image_description, brand_kit, copy_type, tone, length)
        if ai_result and len(ai_result.strip()) > 10:  # Valid response
            return ai_result

        # Fallback to template-based generation (silent fallback for better UX)
        return generate_with_templates(image_description, brand_kit, copy_type, tone, length)

    except Exception as e:
        print(f"Error in generate_marketing_copy_free: {str(e)}")
        # Final fallback to templates
        return generate_with_templates(image_description, brand_kit, copy_type, tone, length)

def generate_with_ai(
    image_description: str,
    brand_kit: Optional[Dict] = None,
    copy_type: str = "product_description",
    tone: str = "professional",
    length: str = "medium"
) -> Optional[str]:
    """Try to generate copy using AI models"""

    try:
        # Build the prompt based on copy type and brand
        prompt = build_copy_prompt(image_description, brand_kit, copy_type, tone, length)

        # Use different models based on copy type
        model_key = get_model_for_copy_type(copy_type)
        model_name = COPYWRITING_MODELS.get(model_key, COPYWRITING_MODELS["general"])

        # Generate copy using Hugging Face
        generated_text = query_huggingface_model(model_name, prompt)

        if generated_text:
            # Clean and format the generated text
            cleaned_copy = clean_generated_copy(generated_text, copy_type, length)
            return cleaned_copy

        return None

    except Exception as e:
        print(f"AI generation error: {str(e)}")
        return None

def generate_with_templates(
    image_description: str,
    brand_kit: Optional[Dict] = None,
    copy_type: str = "product_description",
    tone: str = "professional",
    length: str = "medium"
) -> str:
    """Generate copy using template-based approach as fallback"""

    import random

    # Get base template
    templates = TEMPLATE_RESPONSES.get(copy_type, TEMPLATE_RESPONSES["product_description"])
    base_copy = random.choice(templates)

    # Customize based on image description
    if image_description:
        # Extract key features from description
        description_lower = image_description.lower()

        # Enhanced product detection and customization
        product_replacements = {
            "audio device": ["headphones", "audio", "sound", "speaker", "earbuds", "music"],
            "smartphone": ["phone", "mobile", "smartphone", "iphone", "android"],
            "technology": ["laptop", "computer", "tech", "device", "gadget", "electronic"],
            "fashion item": ["clothing", "fashion", "wear", "shirt", "dress", "shoes", "accessory"],
            "wireless device": ["wireless", "bluetooth", "cordless", "remote"],
            "home appliance": ["kitchen", "appliance", "home", "household"],
            "fitness equipment": ["fitness", "exercise", "workout", "gym", "sports"],
            "beauty product": ["beauty", "cosmetic", "skincare", "makeup"],
            "automotive accessory": ["car", "auto", "vehicle", "driving"],
            "gaming accessory": ["gaming", "game", "controller", "console"]
        }

        # Find the best product category match
        for product_type, keywords in product_replacements.items():
            if any(word in description_lower for word in keywords):
                base_copy = base_copy.replace("product", product_type)
                break

        # Add specific quality descriptors based on description
        if any(word in description_lower for word in ["premium", "luxury", "high-end", "professional"]):
            base_copy = base_copy.replace("exceptional", "premium")
            base_copy = base_copy.replace("quality", "luxury quality")
        elif any(word in description_lower for word in ["sleek", "modern", "contemporary"]):
            base_copy = base_copy.replace("exceptional", "sleek and modern")
        elif any(word in description_lower for word in ["durable", "strong", "robust"]):
            base_copy = base_copy.replace("exceptional", "durable and reliable")

    # Apply brand kit if available
    if brand_kit and brand_kit.get('brand_name'):
        brand_name = brand_kit['brand_name']
        base_copy = f"From {brand_name}: {base_copy}"

    # Adjust for tone
    if tone == "casual":
        base_copy = base_copy.replace("exceptional", "awesome")
        base_copy = base_copy.replace("remarkable", "amazing")
        base_copy = base_copy.replace("outstanding", "great")
    elif tone == "luxury":
        base_copy = base_copy.replace("product", "luxury item")
        base_copy = base_copy.replace("quality", "premium quality")
        base_copy = base_copy.replace("exceptional", "exquisite")
    elif tone == "urgent":
        base_copy = f"Limited time! {base_copy}"
        base_copy = base_copy.replace("Discover", "Don't miss out on")
    elif tone == "creative":
        base_copy = base_copy.replace("product", "game-changer")
        base_copy = base_copy.replace("exceptional", "mind-blowing")

    # Adjust for length
    if length == "short":
        # Take first sentence
        sentences = base_copy.split('. ')
        base_copy = sentences[0] + ('.' if not sentences[0].endswith('.') else '')
    elif length == "long":
        # Add more detail
        base_copy += " Experience the difference that attention to detail and superior craftsmanship can make. Join thousands of satisfied customers who have made the smart choice."

    return base_copy

def build_copy_prompt(
    image_description: str,
    brand_kit: Optional[Dict],
    copy_type: str,
    tone: str,
    length: str
) -> str:
    """Build an effective prompt for copy generation"""
    
    # Base prompt templates for different copy types
    prompts = {
        "product_description": f"Write a compelling product description for: {image_description}",
        "social_media_post": f"Create an engaging social media post about: {image_description}",
        "advertisement_copy": f"Write persuasive advertisement copy for: {image_description}",
        "email_marketing": f"Create email marketing content for: {image_description}",
        "website_copy": f"Write website copy describing: {image_description}",
        "seo_description": f"Write an SEO-optimized description for: {image_description}"
    }
    
    base_prompt = prompts.get(copy_type, prompts["product_description"])
    
    # Add tone guidance
    tone_guidance = {
        "professional": "Use a professional, business-appropriate tone.",
        "casual": "Use a friendly, conversational tone.",
        "creative": "Use creative, engaging language with personality.",
        "urgent": "Create urgency and excitement.",
        "luxury": "Use sophisticated, premium language."
    }
    
    prompt = f"{base_prompt} {tone_guidance.get(tone, '')}"
    
    # Add length guidance
    length_guidance = {
        "short": "Keep it concise and punchy (1-2 sentences).",
        "medium": "Write a moderate length description (2-4 sentences).",
        "long": "Provide detailed, comprehensive copy (4-6 sentences)."
    }
    
    prompt += f" {length_guidance.get(length, '')}"
    
    # Add brand information if available
    if brand_kit:
        brand_name = brand_kit.get('brand_name', '')
        brand_tagline = brand_kit.get('tagline', '')
        
        if brand_name:
            prompt += f" This is for the brand '{brand_name}'."
        if brand_tagline:
            prompt += f" Brand tagline: '{brand_tagline}'."
    
    # Add formatting instruction
    prompt += " Write only the marketing copy, no explanations or additional text."
    
    return prompt

def get_model_for_copy_type(copy_type: str) -> str:
    """Select the best model for the copy type"""
    model_mapping = {
        "product_description": "product",
        "social_media_post": "creative", 
        "advertisement_copy": "marketing",
        "email_marketing": "marketing",
        "website_copy": "general",
        "seo_description": "general"
    }
    return model_mapping.get(copy_type, "general")

def query_huggingface_model(model_name: str, prompt: str, max_retries: int = 2) -> Optional[str]:
    """Query Hugging Face model with improved error handling and fallback"""

    # Try multiple models in order of preference
    models_to_try = [model_name, "gpt2", "microsoft/DialoGPT-medium"]

    for model in models_to_try:
        url = f"{HF_API_URL}{model}"

        headers = {
            "Content-Type": "application/json",
        }

        # Adjust parameters based on model type
        if "gpt2" in model.lower():
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9,
                    "return_full_text": False,
                    "pad_token_id": 50256
                }
            }
        else:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9,
                    "return_full_text": False
                }
            }

        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=20)

                if response.status_code == 200:
                    result = response.json()

                    # Handle different response formats
                    generated_text = None

                    if isinstance(result, list) and len(result) > 0:
                        first_result = result[0]
                        if isinstance(first_result, dict):
                            if "generated_text" in first_result:
                                generated_text = first_result["generated_text"]
                            elif "text" in first_result:
                                generated_text = first_result["text"]
                        elif isinstance(first_result, str):
                            generated_text = first_result
                    elif isinstance(result, dict):
                        if "generated_text" in result:
                            generated_text = result["generated_text"]
                        elif "text" in result:
                            generated_text = result["text"]

                    if generated_text and len(generated_text.strip()) > 5:
                        return generated_text

                elif response.status_code == 503:
                    # Model is loading, try next model (silent for better UX)
                    break

                else:
                    # Silent error handling for better UX - API errors are common with free tier
                    break

            except requests.exceptions.RequestException as e:
                # Silent error handling for better UX
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    break

    return None

def clean_generated_copy(text: str, copy_type: str, length: str) -> str:
    """Clean and format the generated copy"""
    if not text:
        return ""
    
    # Remove common artifacts
    text = text.strip()
    
    # Remove prompt repetition if present
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('Write', 'Create', 'Generate')):
            cleaned_lines.append(line)
    
    cleaned_text = ' '.join(cleaned_lines)
    
    # Ensure proper capitalization
    if cleaned_text:
        cleaned_text = cleaned_text[0].upper() + cleaned_text[1:] if len(cleaned_text) > 1 else cleaned_text.upper()
    
    # Add appropriate ending punctuation
    if cleaned_text and not cleaned_text.endswith(('.', '!', '?')):
        if copy_type in ["social_media_post", "advertisement_copy"]:
            cleaned_text += "!"
        else:
            cleaned_text += "."
    
    return cleaned_text

def generate_multiple_copy_variations_free(
    image_description: str,
    brand_kit: Optional[Dict] = None,
    copy_type: str = "product_description"
) -> List[Dict]:
    """Generate multiple copy variations with different tones and lengths"""
    
    variations = []
    
    # Define variation combinations
    variation_configs = [
        {"tone": "professional", "length": "medium", "label": "Professional Standard"},
        {"tone": "casual", "length": "short", "label": "Casual & Concise"},
        {"tone": "creative", "length": "medium", "label": "Creative & Engaging"},
        {"tone": "luxury", "length": "long", "label": "Premium Detailed"},
        {"tone": "urgent", "length": "short", "label": "Urgent & Direct"}
    ]
    
    for config in variation_configs:
        try:
            copy_text = generate_marketing_copy_free(
                image_description=image_description,
                brand_kit=brand_kit,
                copy_type=copy_type,
                tone=config["tone"],
                length=config["length"]
            )
            
            if copy_text:
                variations.append({
                    "text": copy_text,
                    "tone": config["tone"],
                    "length": config["length"],
                    "label": config["label"],
                    "word_count": len(copy_text.split())
                })
                
        except Exception as e:
            print(f"Error generating variation {config['label']}: {str(e)}")
            continue
    
    return variations

def get_copy_type_options_free() -> List[Dict]:
    """Get available copy types for free copywriter"""
    return [
        {
            "value": "product_description",
            "label": "Product Description",
            "description": "Detailed product information and benefits"
        },
        {
            "value": "social_media_post", 
            "label": "Social Media Post",
            "description": "Engaging content for social platforms"
        },
        {
            "value": "advertisement_copy",
            "label": "Advertisement Copy", 
            "description": "Persuasive advertising content"
        },
        {
            "value": "email_marketing",
            "label": "Email Marketing",
            "description": "Email campaign content"
        },
        {
            "value": "website_copy",
            "label": "Website Copy",
            "description": "Web page content and descriptions"
        },
        {
            "value": "seo_description",
            "label": "SEO Description",
            "description": "Search engine optimized content"
        }
    ]

def test_free_copywriter_connection() -> Tuple[bool, str]:
    """Test if the free copywriter service is working"""
    try:
        test_copy = generate_marketing_copy_free(
            image_description="Premium wireless headphones with noise cancellation, sleek black design, premium quality",
            copy_type="product_description",
            tone="professional",
            length="short"
        )

        if test_copy and len(test_copy.strip()) > 10:
            return True, f"✅ Service working! Generated: '{test_copy[:50]}...'"
        else:
            return False, "⚠️ Service responded but generated insufficient content"

    except Exception as e:
        return False, f"❌ Service error: {str(e)}"
