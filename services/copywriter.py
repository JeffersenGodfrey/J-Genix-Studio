"""
AI Content Copywriter
Generates marketing copy, product descriptions, and social media content
"""

import requests
import json
import streamlit as st
from typing import Dict, List, Optional, Tuple
import time


def generate_copy_with_openai(prompt: str, api_key: str, copy_type: str = "product_description", 
                             tone: str = "professional", length: str = "medium") -> Optional[str]:
    """Generate copy using OpenAI API"""
    try:
        # OpenAI API endpoint
        url = "https://api.openai.com/v1/chat/completions"
        
        # Create system prompt based on copy type and tone
        system_prompts = {
            "product_description": f"You are a professional copywriter specializing in e-commerce product descriptions. Write compelling, SEO-friendly product descriptions in a {tone} tone.",
            "social_media": f"You are a social media marketing expert. Create engaging social media captions and posts in a {tone} tone that drive engagement.",
            "ad_copy": f"You are an advertising copywriter. Create persuasive ad copy that converts in a {tone} tone.",
            "blog_content": f"You are a content marketing specialist. Write informative and engaging blog content in a {tone} tone.",
            "email_marketing": f"You are an email marketing expert. Create compelling email content that drives action in a {tone} tone."
        }
        
        # Length guidelines
        length_guidelines = {
            "short": "Keep it concise, under 50 words.",
            "medium": "Write 50-150 words.",
            "long": "Write 150-300 words with detailed information."
        }
        
        system_prompt = system_prompts.get(copy_type, system_prompts["product_description"])
        length_guide = length_guidelines.get(length, length_guidelines["medium"])
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": f"{system_prompt} {length_guide}"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error generating copy with OpenAI: {str(e)}")
        return None


def generate_copy_with_claude(prompt: str, api_key: str, copy_type: str = "product_description", 
                             tone: str = "professional", length: str = "medium") -> Optional[str]:
    """Generate copy using Claude API"""
    try:
        # Claude API endpoint
        url = "https://api.anthropic.com/v1/messages"
        
        # Create system prompt
        system_prompts = {
            "product_description": f"You are a professional copywriter specializing in e-commerce. Write compelling product descriptions in a {tone} tone.",
            "social_media": f"You are a social media expert. Create engaging content in a {tone} tone.",
            "ad_copy": f"You are an advertising copywriter. Create persuasive ad copy in a {tone} tone.",
            "blog_content": f"You are a content marketing specialist. Write informative content in a {tone} tone.",
            "email_marketing": f"You are an email marketing expert. Create compelling email content in a {tone} tone."
        }
        
        length_guidelines = {
            "short": "Keep it concise, under 50 words.",
            "medium": "Write 50-150 words.",
            "long": "Write 150-300 words with detailed information."
        }
        
        system_prompt = system_prompts.get(copy_type, system_prompts["product_description"])
        length_guide = length_guidelines.get(length, length_guidelines["medium"])
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 500,
            "system": f"{system_prompt} {length_guide}",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"].strip()
        else:
            print(f"Claude API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error generating copy with Claude: {str(e)}")
        return None


def generate_marketing_copy(image_description: str, brand_kit: Optional[Dict] = None, 
                          copy_type: str = "product_description", tone: str = "professional",
                          length: str = "medium", api_provider: str = "openai", 
                          api_key: str = "") -> Optional[str]:
    """Generate marketing copy based on image and brand information"""
    try:
        # Build context prompt
        context_parts = [f"Based on this image/product: {image_description}"]
        
        # Add brand context if available
        if brand_kit:
            brand_name = brand_kit.get("brand_name", "")
            tagline = brand_kit.get("tagline", "")
            
            if brand_name:
                context_parts.append(f"Brand: {brand_name}")
            if tagline:
                context_parts.append(f"Brand tagline: {tagline}")
        
        # Add specific instructions based on copy type
        copy_instructions = {
            "product_description": "Write a compelling product description that highlights key features, benefits, and appeals to potential customers.",
            "social_media": "Create an engaging social media post with relevant hashtags that would drive engagement and shares.",
            "ad_copy": "Write persuasive advertising copy that would convert viewers into customers, including a clear call-to-action.",
            "blog_content": "Write informative blog content that educates readers about this product/topic.",
            "email_marketing": "Create compelling email content that would drive opens, clicks, and conversions."
        }
        
        instruction = copy_instructions.get(copy_type, copy_instructions["product_description"])
        context_parts.append(instruction)
        
        # Combine context
        full_prompt = ". ".join(context_parts)
        
        # Generate copy based on provider
        if api_provider == "openai":
            return generate_copy_with_openai(full_prompt, api_key, copy_type, tone, length)
        elif api_provider == "claude":
            return generate_copy_with_claude(full_prompt, api_key, copy_type, tone, length)
        else:
            return None
            
    except Exception as e:
        print(f"Error generating marketing copy: {str(e)}")
        return None


def generate_multiple_copy_variations(image_description: str, brand_kit: Optional[Dict] = None,
                                    copy_type: str = "product_description", 
                                    api_provider: str = "openai", api_key: str = "") -> List[Dict]:
    """Generate multiple copy variations with different tones and lengths"""
    variations = []
    
    # Define variation combinations
    variation_configs = [
        {"tone": "professional", "length": "medium", "label": "Professional (Medium)"},
        {"tone": "casual", "length": "short", "label": "Casual (Short)"},
        {"tone": "enthusiastic", "length": "long", "label": "Enthusiastic (Long)"},
        {"tone": "luxury", "length": "medium", "label": "Luxury (Medium)"}
    ]
    
    for config in variation_configs:
        try:
            copy_text = generate_marketing_copy(
                image_description=image_description,
                brand_kit=brand_kit,
                copy_type=copy_type,
                tone=config["tone"],
                length=config["length"],
                api_provider=api_provider,
                api_key=api_key
            )
            
            if copy_text:
                variations.append({
                    "label": config["label"],
                    "tone": config["tone"],
                    "length": config["length"],
                    "text": copy_text,
                    "word_count": len(copy_text.split())
                })
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error generating variation {config['label']}: {str(e)}")
            continue
    
    return variations


def validate_api_key(api_key: str, provider: str) -> Tuple[bool, str]:
    """Validate API key for the specified provider"""
    if not api_key:
        return False, "API key is required"
    
    if provider == "openai":
        if not api_key.startswith("sk-"):
            return False, "OpenAI API key should start with 'sk-'"
    elif provider == "claude":
        if len(api_key) < 20:
            return False, "Claude API key appears to be too short"
    
    return True, "API key format is valid"


def get_copy_type_options() -> List[Dict]:
    """Get available copy type options"""
    return [
        {"value": "product_description", "label": "Product Description", "description": "Detailed product descriptions for e-commerce"},
        {"value": "social_media", "label": "Social Media", "description": "Engaging posts for social platforms"},
        {"value": "ad_copy", "label": "Advertisement Copy", "description": "Persuasive advertising content"},
        {"value": "blog_content", "label": "Blog Content", "description": "Informative blog posts and articles"},
        {"value": "email_marketing", "label": "Email Marketing", "description": "Compelling email campaigns"}
    ]


def get_tone_options() -> List[str]:
    """Get available tone options"""
    return ["professional", "casual", "enthusiastic", "luxury", "friendly", "authoritative", "playful", "sophisticated"]


def get_length_options() -> List[Dict]:
    """Get available length options"""
    return [
        {"value": "short", "label": "Short (Under 50 words)", "description": "Concise and to the point"},
        {"value": "medium", "label": "Medium (50-150 words)", "description": "Balanced detail and brevity"},
        {"value": "long", "label": "Long (150-300 words)", "description": "Comprehensive and detailed"}
    ]
