"""
ProductAI Pro - Pricing Strategy & Business Model
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import stripe  # For payment processing

class PricingTier:
    """Define pricing tiers and their capabilities"""
    
    TIERS = {
        "free": {
            "name": "Free Trial",
            "price_monthly": 0,
            "price_yearly": 0,
            "description": "Try ProductAI Pro with limited features",
            "features": {
                "ai_generations": 10,
                "product_photography": 5,
                "batch_processing": False,
                "brand_kit": False,
                "ab_testing": False,
                "api_access": False,
                "priority_support": False,
                "custom_branding": False
            },
            "limits": {
                "max_file_size_mb": 5,
                "max_resolution": "1024x1024",
                "concurrent_requests": 1,
                "storage_days": 7
            },
            "target_audience": "Individual users trying the platform"
        },
        
        "starter": {
            "name": "Starter",
            "price_monthly": 29,
            "price_yearly": 290,  # 2 months free
            "description": "Perfect for small businesses and individual sellers",
            "features": {
                "ai_generations": 100,
                "product_photography": 50,
                "batch_processing": 10,  # Max 10 items per batch
                "brand_kit": 1,
                "ab_testing": False,
                "api_access": False,
                "priority_support": False,
                "custom_branding": False
            },
            "limits": {
                "max_file_size_mb": 10,
                "max_resolution": "2048x2048",
                "concurrent_requests": 2,
                "storage_days": 30
            },
            "target_audience": "Small e-commerce sellers, individual entrepreneurs"
        },
        
        "professional": {
            "name": "Professional",
            "price_monthly": 99,
            "price_yearly": 990,  # 2 months free
            "description": "Ideal for growing e-commerce businesses",
            "features": {
                "ai_generations": 500,
                "product_photography": 300,
                "batch_processing": 50,  # Max 50 items per batch
                "brand_kit": 5,
                "ab_testing": True,
                "api_access": "basic",
                "priority_support": True,
                "custom_branding": False
            },
            "limits": {
                "max_file_size_mb": 25,
                "max_resolution": "4096x4096",
                "concurrent_requests": 5,
                "storage_days": 90
            },
            "target_audience": "Growing e-commerce businesses, marketing agencies",
            "popular": True
        },
        
        "enterprise": {
            "name": "Enterprise",
            "price_monthly": 299,
            "price_yearly": 2990,  # 2 months free
            "description": "For large businesses and agencies",
            "features": {
                "ai_generations": "unlimited",
                "product_photography": "unlimited",
                "batch_processing": "unlimited",
                "brand_kit": "unlimited",
                "ab_testing": True,
                "api_access": "full",
                "priority_support": True,
                "custom_branding": True,
                "white_label": True,
                "dedicated_support": True
            },
            "limits": {
                "max_file_size_mb": 100,
                "max_resolution": "8192x8192",
                "concurrent_requests": 20,
                "storage_days": 365
            },
            "target_audience": "Large enterprises, agencies, white-label partners"
        }
    }
    
    @classmethod
    def get_tier_info(cls, tier_name: str) -> Dict[str, Any]:
        """Get information about a specific pricing tier"""
        return cls.TIERS.get(tier_name, cls.TIERS["free"])
    
    @classmethod
    def check_usage_limits(cls, tier_name: str, current_usage: Dict[str, int]) -> Dict[str, bool]:
        """Check if user is within their tier limits"""
        tier = cls.get_tier_info(tier_name)
        limits_status = {}
        
        for feature, limit in tier["features"].items():
            if isinstance(limit, int):
                current = current_usage.get(feature, 0)
                limits_status[feature] = current < limit
            elif limit == "unlimited":
                limits_status[feature] = True
            else:
                limits_status[feature] = bool(limit)
        
        return limits_status
    
    @classmethod
    def get_upgrade_recommendations(cls, current_tier: str, usage_pattern: Dict[str, int]) -> List[str]:
        """Recommend tier upgrades based on usage patterns"""
        recommendations = []
        current_tier_info = cls.get_tier_info(current_tier)
        
        # Check if user is hitting limits
        for feature, usage in usage_pattern.items():
            if feature in current_tier_info["features"]:
                limit = current_tier_info["features"][feature]
                if isinstance(limit, int) and usage >= limit * 0.8:  # 80% of limit
                    recommendations.append(f"Consider upgrading for more {feature.replace('_', ' ')}")
        
        return recommendations

class PaymentProcessor:
    """Handle payment processing and subscription management"""
    
    def __init__(self, stripe_secret_key: str):
        stripe.api_key = stripe_secret_key
        self.webhook_secret = None
    
    def create_subscription(self, customer_email: str, tier_name: str, 
                          billing_cycle: str = "monthly") -> Dict[str, Any]:
        """Create a new subscription for a customer"""
        try:
            # Create customer
            customer = stripe.Customer.create(
                email=customer_email,
                metadata={"tier": tier_name}
            )
            
            # Get price ID based on tier and billing cycle
            price_id = self._get_price_id(tier_name, billing_cycle)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "customer_id": customer.id
            }
            
        except stripe.error.StripeError as e:
            return {"error": str(e)}
    
    def _get_price_id(self, tier_name: str, billing_cycle: str) -> str:
        """Get Stripe price ID for tier and billing cycle"""
        # These would be your actual Stripe price IDs
        price_ids = {
            "starter": {
                "monthly": "price_starter_monthly",
                "yearly": "price_starter_yearly"
            },
            "professional": {
                "monthly": "price_professional_monthly", 
                "yearly": "price_professional_yearly"
            },
            "enterprise": {
                "monthly": "price_enterprise_monthly",
                "yearly": "price_enterprise_yearly"
            }
        }
        
        return price_ids.get(tier_name, {}).get(billing_cycle, "price_starter_monthly")
    
    def handle_webhook(self, payload: str, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            if event["type"] == "customer.subscription.created":
                # Handle new subscription
                subscription = event["data"]["object"]
                return self._handle_subscription_created(subscription)
            
            elif event["type"] == "customer.subscription.updated":
                # Handle subscription changes
                subscription = event["data"]["object"]
                return self._handle_subscription_updated(subscription)
            
            elif event["type"] == "customer.subscription.deleted":
                # Handle subscription cancellation
                subscription = event["data"]["object"]
                return self._handle_subscription_cancelled(subscription)
            
            return {"status": "success"}
            
        except ValueError as e:
            return {"error": "Invalid payload"}
        except stripe.error.SignatureVerificationError as e:
            return {"error": "Invalid signature"}
    
    def _handle_subscription_created(self, subscription: Dict) -> Dict[str, Any]:
        """Handle new subscription creation"""
        # Update user's tier in your database
        customer_id = subscription["customer"]
        tier_name = subscription["metadata"].get("tier", "starter")
        
        # Your database update logic here
        return {"status": "subscription_created", "tier": tier_name}
    
    def _handle_subscription_updated(self, subscription: Dict) -> Dict[str, Any]:
        """Handle subscription updates (upgrades/downgrades)"""
        # Update user's tier and reset usage counters
        return {"status": "subscription_updated"}
    
    def _handle_subscription_cancelled(self, subscription: Dict) -> Dict[str, Any]:
        """Handle subscription cancellation"""
        # Downgrade user to free tier
        return {"status": "subscription_cancelled"}

class UsageTracker:
    """Track user usage across different features"""
    
    def __init__(self, database_connection):
        self.db = database_connection
    
    def record_usage(self, user_id: str, feature: str, quantity: int = 1):
        """Record feature usage for a user"""
        query = """
        INSERT INTO usage_tracking (user_id, feature, quantity, recorded_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, feature, date_trunc('month', recorded_at))
        DO UPDATE SET quantity = usage_tracking.quantity + %s
        """
        
        self.db.execute(query, (user_id, feature, quantity, datetime.now(), quantity))
    
    def get_monthly_usage(self, user_id: str) -> Dict[str, int]:
        """Get user's usage for the current month"""
        query = """
        SELECT feature, SUM(quantity) as total
        FROM usage_tracking
        WHERE user_id = %s 
        AND date_trunc('month', recorded_at) = date_trunc('month', CURRENT_DATE)
        GROUP BY feature
        """
        
        results = self.db.execute(query, (user_id,)).fetchall()
        return {row["feature"]: row["total"] for row in results}
    
    def check_limits(self, user_id: str, tier_name: str) -> Dict[str, Any]:
        """Check if user is within their tier limits"""
        usage = self.get_monthly_usage(user_id)
        limits_status = PricingTier.check_usage_limits(tier_name, usage)
        
        return {
            "current_usage": usage,
            "limits_status": limits_status,
            "can_use_feature": all(limits_status.values())
        }

# Business Metrics and KPIs
class BusinessMetrics:
    """Track key business metrics"""
    
    METRICS = {
        "monthly_recurring_revenue": "MRR",
        "annual_recurring_revenue": "ARR", 
        "customer_acquisition_cost": "CAC",
        "lifetime_value": "LTV",
        "churn_rate": "Monthly Churn %",
        "conversion_rate": "Trial to Paid %",
        "average_revenue_per_user": "ARPU"
    }
    
    @staticmethod
    def calculate_mrr(subscriptions: List[Dict]) -> float:
        """Calculate Monthly Recurring Revenue"""
        mrr = 0
        for sub in subscriptions:
            if sub["status"] == "active":
                if sub["billing_cycle"] == "monthly":
                    mrr += sub["amount"]
                elif sub["billing_cycle"] == "yearly":
                    mrr += sub["amount"] / 12
        return mrr
    
    @staticmethod
    def calculate_churn_rate(customers_start: int, customers_lost: int) -> float:
        """Calculate monthly churn rate"""
        return (customers_lost / customers_start) * 100 if customers_start > 0 else 0
    
    @staticmethod
    def calculate_ltv_cac_ratio(ltv: float, cac: float) -> float:
        """Calculate LTV:CAC ratio (should be > 3:1)"""
        return ltv / cac if cac > 0 else 0

# Competitive Analysis
COMPETITIVE_LANDSCAPE = {
    "canva": {
        "pricing": "$12.99/month",
        "strengths": ["Easy to use", "Templates", "Brand recognition"],
        "weaknesses": ["Limited AI", "Not product-focused", "Generic results"]
    },
    "photoroom": {
        "pricing": "$9.99/month", 
        "strengths": ["Good background removal", "Mobile app"],
        "weaknesses": ["Limited features", "No batch processing", "No A/B testing"]
    },
    "remove_bg": {
        "pricing": "$9.99/month",
        "strengths": ["Excellent background removal"],
        "weaknesses": ["One-trick pony", "No generation", "Limited editing"]
    }
}

# Our competitive advantages
COMPETITIVE_ADVANTAGES = [
    "AI-powered product-specific generation",
    "Complete workflow from generation to optimization",
    "A/B testing and analytics built-in",
    "Batch processing for e-commerce scale",
    "Brand consistency tools",
    "Professional quality results",
    "E-commerce focused features"
]
