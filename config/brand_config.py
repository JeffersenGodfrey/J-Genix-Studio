"""
J-Genix Studio - Brand Configuration
Professional AI-powered product image generation platform
"""

# Brand Identity
BRAND_NAME = "J-Genix Studio"
BRAND_TAGLINE = "Professional AI Image Generation for E-commerce"
BRAND_DESCRIPTION = "Transform your product photography with AI-powered image generation, editing, and optimization tools designed for modern businesses."

# Color Palette
BRAND_COLORS = {
    "primary": "#667eea",      # Professional blue-purple
    "secondary": "#764ba2",    # Deeper purple
    "accent": "#f093fb",       # Light pink accent
    "success": "#28a745",      # Green for success states
    "warning": "#ffc107",      # Yellow for warnings
    "error": "#dc3545",        # Red for errors
    "dark": "#2c3e50",         # Dark text
    "light": "#f8f9fa",        # Light backgrounds
    "white": "#ffffff"         # Pure white
}

# Typography
BRAND_FONTS = {
    "primary": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
    "secondary": "Roboto, Arial, sans-serif",
    "monospace": "Monaco, Consolas, monospace"
}

# Brand Voice & Messaging
BRAND_VOICE = {
    "tone": "Professional yet approachable",
    "personality": ["Innovative", "Reliable", "Efficient", "User-focused"],
    "messaging_pillars": [
        "AI-Powered Excellence",
        "Professional Results",
        "Time-Saving Automation",
        "Business Growth"
    ]
}

# UI Configuration
UI_CONFIG = {
    "header_gradient": f"linear-gradient(90deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['secondary']} 100%)",
    "button_gradient": f"linear-gradient(90deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['secondary']} 100%)",
    "card_shadow": "0 2px 10px rgba(0,0,0,0.1)",
    "border_radius": "10px",
    "spacing_unit": "1rem"
}

# Feature Descriptions (User-Facing)
FEATURE_DESCRIPTIONS = {
    "image_generation": {
        "title": "AI Image Generation",
        "description": "Create stunning product images from simple text descriptions using advanced AI technology.",
        "icon": "🎨",
        "benefits": [
            "Generate unlimited variations",
            "Professional quality results",
            "No photography equipment needed",
            "Instant results in minutes"
        ]
    },
    "product_photography": {
        "title": "Product Photography Suite",
        "description": "Transform your product photos with professional packshots, shadows, and lifestyle settings.",
        "icon": "📸",
        "benefits": [
            "Remove backgrounds instantly",
            "Add realistic shadows",
            "Create lifestyle contexts",
            "Professional studio quality"
        ]
    },
    "batch_processing": {
        "title": "Batch Processing",
        "description": "Process hundreds of products simultaneously with automated workflows and bulk operations.",
        "icon": "🔄",
        "benefits": [
            "Save hours of manual work",
            "Consistent results across products",
            "CSV upload and export",
            "Automated quality control"
        ]
    },
    "brand_kit": {
        "title": "Brand Consistency Kit",
        "description": "Maintain consistent brand identity across all generated images with custom style guides.",
        "icon": "🎨",
        "benefits": [
            "Custom brand colors and styles",
            "Automated brand application",
            "Style template library",
            "Brand compliance checking"
        ]
    },
    "ab_testing": {
        "title": "A/B Testing & Analytics",
        "description": "Test different image variations and optimize for maximum conversion rates.",
        "icon": "📊",
        "benefits": [
            "Data-driven optimization",
            "Performance tracking",
            "Conversion rate insights",
            "ROI measurement"
        ]
    },
    "logo_generation": {
        "title": "AI Logo Generation",
        "description": "Create professional, unique logos for your brand using advanced AI technology.",
        "icon": "🎨",
        "benefits": [
            "Unlimited logo variations",
            "Professional brand identity",
            "Multiple styles and formats",
            "Instant logo creation"
        ]
    }
}

# Pricing Tiers
PRICING_TIERS = {
    "starter": {
        "name": "Starter",
        "price": "$29/month",
        "description": "Perfect for small businesses and individual sellers",
        "features": [
            "100 AI-generated images/month",
            "Basic product photography tools",
            "Standard support",
            "1 brand kit"
        ],
        "cta": "Start Free Trial"
    },
    "professional": {
        "name": "Professional",
        "price": "$99/month",
        "description": "Ideal for growing e-commerce businesses",
        "features": [
            "500 AI-generated images/month",
            "Advanced editing tools",
            "Batch processing (up to 50 items)",
            "A/B testing (basic)",
            "Priority support",
            "5 brand kits"
        ],
        "cta": "Upgrade to Pro",
        "popular": True
    },
    "enterprise": {
        "name": "Enterprise",
        "price": "Custom",
        "description": "For large businesses and agencies",
        "features": [
            "Unlimited AI-generated images",
            "Full feature access",
            "Unlimited batch processing",
            "Advanced A/B testing",
            "White-label options",
            "Dedicated account manager",
            "Custom integrations"
        ],
        "cta": "Contact Sales"
    }
}

# Marketing Messages
MARKETING_COPY = {
    "hero_headline": "Transform Your Product Photography with AI",
    "hero_subheadline": "Generate professional product images, lifestyle shots, and marketing visuals in minutes, not hours.",
    "value_propositions": [
        "🚀 10x faster than traditional photography",
        "💰 90% cost reduction vs. hiring photographers",
        "🎯 Proven to increase conversion rates by 35%",
        "⚡ Generate unlimited variations instantly"
    ],
    "social_proof": {
        "customer_count": "10,000+",
        "images_generated": "1M+",
        "time_saved": "50,000+ hours",
        "satisfaction_rate": "98%"
    }
}

# Legal & Compliance
LEGAL_INFO = {
    "company_name": "ProductAI Pro LLC",
    "support_email": "support@productaipro.com",
    "privacy_policy_url": "/privacy",
    "terms_of_service_url": "/terms",
    "data_retention_days": 90,
    "gdpr_compliant": True
}

# Technical Configuration
TECHNICAL_CONFIG = {
    "max_file_size_mb": 10,
    "supported_formats": ["JPG", "JPEG", "PNG", "WEBP"],
    "max_batch_size": 100,
    "api_timeout_seconds": 30,
    "max_concurrent_requests": 5,
    "image_quality_default": 95,
    "cache_duration_hours": 24
}

def get_brand_css():
    """Generate CSS with brand colors and styling"""
    return f"""
    :root {{
        --primary-color: {BRAND_COLORS['primary']};
        --secondary-color: {BRAND_COLORS['secondary']};
        --accent-color: {BRAND_COLORS['accent']};
        --success-color: {BRAND_COLORS['success']};
        --warning-color: {BRAND_COLORS['warning']};
        --error-color: {BRAND_COLORS['error']};
        --dark-color: {BRAND_COLORS['dark']};
        --light-color: {BRAND_COLORS['light']};
        --white-color: {BRAND_COLORS['white']};
        
        --font-primary: {BRAND_FONTS['primary']};
        --font-secondary: {BRAND_FONTS['secondary']};
        --font-monospace: {BRAND_FONTS['monospace']};
        
        --border-radius: {UI_CONFIG['border_radius']};
        --spacing-unit: {UI_CONFIG['spacing_unit']};
    }}
    
    .brand-header {{
        background: {UI_CONFIG['header_gradient']};
        color: var(--white-color);
        padding: 2rem 1rem;
        border-radius: var(--border-radius);
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .brand-button {{
        background: {UI_CONFIG['button_gradient']};
        color: var(--white-color);
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .brand-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }}
    
    .feature-card {{
        background: var(--white-color);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: {UI_CONFIG['card_shadow']};
        border-left: 4px solid var(--primary-color);
        margin-bottom: var(--spacing-unit);
    }}
    """

def get_welcome_message():
    """Get personalized welcome message"""
    return f"""
    Welcome to {BRAND_NAME}! 
    
    {BRAND_TAGLINE}
    
    Ready to transform your product photography? Let's create something amazing together.
    """
