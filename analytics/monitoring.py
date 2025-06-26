"""
ProductAI Pro - Analytics and Monitoring System
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserEvent:
    """Structure for user events"""
    user_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    session_id: str
    ip_address: str
    user_agent: str

class AnalyticsTracker:
    """Track user behavior and application metrics"""
    
    def __init__(self, database_connection=None):
        self.db = database_connection
        self.events_buffer = []
        self.buffer_size = 100
        
        # Initialize analytics services
        self.google_analytics_id = os.getenv('GA_MEASUREMENT_ID')
        self.mixpanel_token = os.getenv('MIXPANEL_TOKEN')
        self.amplitude_api_key = os.getenv('AMPLITUDE_API_KEY')
    
    def track_event(self, user_id: str, event_type: str, event_data: Dict[str, Any] = None,
                   session_id: str = None, ip_address: str = None, user_agent: str = None):
        """Track a user event"""
        event = UserEvent(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data or {},
            timestamp=datetime.now(),
            session_id=session_id or "unknown",
            ip_address=ip_address or "unknown",
            user_agent=user_agent or "unknown"
        )
        
        # Add to buffer
        self.events_buffer.append(event)
        
        # Flush buffer if full
        if len(self.events_buffer) >= self.buffer_size:
            self.flush_events()
        
        # Send to external analytics services
        self._send_to_external_services(event)
    
    def flush_events(self):
        """Flush events buffer to database"""
        if not self.events_buffer or not self.db:
            return
        
        try:
            query = """
            INSERT INTO user_events (user_id, event_type, event_data, timestamp, 
                                   session_id, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            for event in self.events_buffer:
                self.db.execute(query, (
                    event.user_id,
                    event.event_type,
                    json.dumps(event.event_data),
                    event.timestamp,
                    event.session_id,
                    event.ip_address,
                    event.user_agent
                ))
            
            self.db.commit()
            self.events_buffer.clear()
            logger.info(f"Flushed {len(self.events_buffer)} events to database")
            
        except Exception as e:
            logger.error(f"Failed to flush events: {str(e)}")
    
    def _send_to_external_services(self, event: UserEvent):
        """Send event to external analytics services"""
        # Google Analytics 4
        if self.google_analytics_id:
            self._send_to_ga4(event)
        
        # Mixpanel
        if self.mixpanel_token:
            self._send_to_mixpanel(event)
        
        # Amplitude
        if self.amplitude_api_key:
            self._send_to_amplitude(event)
    
    def _send_to_ga4(self, event: UserEvent):
        """Send event to Google Analytics 4"""
        try:
            payload = {
                "client_id": event.user_id,
                "events": [{
                    "name": event.event_type.replace("_", ""),
                    "params": {
                        **event.event_data,
                        "session_id": event.session_id,
                        "timestamp_micros": int(event.timestamp.timestamp() * 1000000)
                    }
                }]
            }
            
            url = f"https://www.google-analytics.com/mp/collect?measurement_id={self.google_analytics_id}&api_secret={os.getenv('GA_API_SECRET')}"
            requests.post(url, json=payload, timeout=5)
            
        except Exception as e:
            logger.error(f"Failed to send to GA4: {str(e)}")
    
    def _send_to_mixpanel(self, event: UserEvent):
        """Send event to Mixpanel"""
        try:
            payload = {
                "event": event.event_type,
                "properties": {
                    "distinct_id": event.user_id,
                    "time": int(event.timestamp.timestamp()),
                    "$ip": event.ip_address,
                    "$user_agent": event.user_agent,
                    **event.event_data
                }
            }
            
            url = "https://api.mixpanel.com/track"
            requests.post(url, json=payload, auth=(self.mixpanel_token, ""), timeout=5)
            
        except Exception as e:
            logger.error(f"Failed to send to Mixpanel: {str(e)}")
    
    def _send_to_amplitude(self, event: UserEvent):
        """Send event to Amplitude"""
        try:
            payload = {
                "api_key": self.amplitude_api_key,
                "events": [{
                    "user_id": event.user_id,
                    "event_type": event.event_type,
                    "time": int(event.timestamp.timestamp() * 1000),
                    "session_id": event.session_id,
                    "ip": event.ip_address,
                    "event_properties": event.event_data,
                    "user_properties": {}
                }]
            }
            
            url = "https://api2.amplitude.com/2/httpapi"
            requests.post(url, json=payload, timeout=5)
            
        except Exception as e:
            logger.error(f"Failed to send to Amplitude: {str(e)}")

class PerformanceMonitor:
    """Monitor application performance and health"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = []
        
        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 5000,
            "error_rate_percent": 5.0,
            "memory_usage_percent": 80.0,
            "cpu_usage_percent": 80.0
        }
    
    def record_request(self, endpoint: str, response_time_ms: float, 
                      status_code: int, user_id: str = None):
        """Record API request metrics"""
        timestamp = datetime.now()
        
        # Store in metrics
        if endpoint not in self.metrics:
            self.metrics[endpoint] = {
                "requests": [],
                "errors": [],
                "response_times": []
            }
        
        self.metrics[endpoint]["requests"].append({
            "timestamp": timestamp,
            "response_time_ms": response_time_ms,
            "status_code": status_code,
            "user_id": user_id
        })
        
        if status_code >= 400:
            self.metrics[endpoint]["errors"].append({
                "timestamp": timestamp,
                "status_code": status_code,
                "user_id": user_id
            })
        
        self.metrics[endpoint]["response_times"].append(response_time_ms)
        
        # Check for alerts
        self._check_performance_alerts(endpoint, response_time_ms, status_code)
    
    def _check_performance_alerts(self, endpoint: str, response_time_ms: float, status_code: int):
        """Check if performance metrics exceed thresholds"""
        # Response time alert
        if response_time_ms > self.thresholds["response_time_ms"]:
            self._create_alert("high_response_time", {
                "endpoint": endpoint,
                "response_time_ms": response_time_ms,
                "threshold": self.thresholds["response_time_ms"]
            })
        
        # Error rate alert
        if status_code >= 500:
            self._create_alert("server_error", {
                "endpoint": endpoint,
                "status_code": status_code
            })
    
    def _create_alert(self, alert_type: str, data: Dict[str, Any]):
        """Create performance alert"""
        alert = {
            "type": alert_type,
            "timestamp": datetime.now(),
            "data": data,
            "severity": self._get_alert_severity(alert_type)
        }
        
        self.alerts.append(alert)
        logger.warning(f"Performance alert: {alert_type} - {data}")
        
        # Send to monitoring service (e.g., PagerDuty, Slack)
        self._send_alert_notification(alert)
    
    def _get_alert_severity(self, alert_type: str) -> str:
        """Get alert severity level"""
        severity_map = {
            "high_response_time": "warning",
            "server_error": "critical",
            "high_error_rate": "critical",
            "resource_exhaustion": "critical"
        }
        return severity_map.get(alert_type, "info")
    
    def _send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification to monitoring services"""
        # Slack notification
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if slack_webhook:
            try:
                payload = {
                    "text": f"🚨 ProductAI Pro Alert: {alert['type']}",
                    "attachments": [{
                        "color": "danger" if alert['severity'] == "critical" else "warning",
                        "fields": [
                            {"title": "Type", "value": alert['type'], "short": True},
                            {"title": "Severity", "value": alert['severity'], "short": True},
                            {"title": "Data", "value": json.dumps(alert['data']), "short": False}
                        ]
                    }]
                }
                requests.post(slack_webhook, json=payload, timeout=5)
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {str(e)}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        summary = {}
        
        for endpoint, data in self.metrics.items():
            recent_requests = [r for r in data["requests"] if r["timestamp"] > cutoff_time]
            recent_errors = [e for e in data["errors"] if e["timestamp"] > cutoff_time]
            
            if recent_requests:
                response_times = [r["response_time_ms"] for r in recent_requests]
                summary[endpoint] = {
                    "total_requests": len(recent_requests),
                    "error_count": len(recent_errors),
                    "error_rate_percent": (len(recent_errors) / len(recent_requests)) * 100,
                    "avg_response_time_ms": sum(response_times) / len(response_times),
                    "max_response_time_ms": max(response_times),
                    "min_response_time_ms": min(response_times)
                }
        
        return summary

class BusinessMetricsTracker:
    """Track business-specific metrics"""
    
    def __init__(self, database_connection=None):
        self.db = database_connection
    
    def track_conversion(self, user_id: str, from_tier: str, to_tier: str, 
                        conversion_value: float):
        """Track tier conversion/upgrade"""
        if self.db:
            query = """
            INSERT INTO conversions (user_id, from_tier, to_tier, conversion_value, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute(query, (user_id, from_tier, to_tier, conversion_value, datetime.now()))
    
    def track_feature_usage(self, user_id: str, feature: str, usage_count: int = 1):
        """Track feature usage for product insights"""
        if self.db:
            query = """
            INSERT INTO feature_usage (user_id, feature, usage_count, timestamp)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, feature, date_trunc('day', timestamp))
            DO UPDATE SET usage_count = feature_usage.usage_count + %s
            """
            self.db.execute(query, (user_id, feature, usage_count, datetime.now(), usage_count))
    
    def get_conversion_funnel(self, days: int = 30) -> Dict[str, Any]:
        """Get conversion funnel metrics"""
        if not self.db:
            return {}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get funnel data
        query = """
        SELECT 
            COUNT(DISTINCT CASE WHEN created_at > %s THEN user_id END) as signups,
            COUNT(DISTINCT CASE WHEN first_generation_at > %s THEN user_id END) as activated,
            COUNT(DISTINCT CASE WHEN subscription_start > %s THEN user_id END) as converted
        FROM users
        """
        
        result = self.db.execute(query, (cutoff_date, cutoff_date, cutoff_date)).fetchone()
        
        if result:
            signups = result["signups"] or 0
            activated = result["activated"] or 0
            converted = result["converted"] or 0
            
            return {
                "signups": signups,
                "activated": activated,
                "converted": converted,
                "activation_rate": (activated / signups * 100) if signups > 0 else 0,
                "conversion_rate": (converted / activated * 100) if activated > 0 else 0,
                "overall_conversion": (converted / signups * 100) if signups > 0 else 0
            }
        
        return {}

# Event tracking helpers for Streamlit
def track_page_view(user_id: str, page_name: str, analytics_tracker: AnalyticsTracker):
    """Track page view event"""
    analytics_tracker.track_event(user_id, "page_view", {"page": page_name})

def track_feature_use(user_id: str, feature: str, analytics_tracker: AnalyticsTracker, 
                     **kwargs):
    """Track feature usage event"""
    analytics_tracker.track_event(user_id, "feature_use", {"feature": feature, **kwargs})

def track_generation(user_id: str, generation_type: str, success: bool, 
                    processing_time: float, analytics_tracker: AnalyticsTracker):
    """Track image generation event"""
    analytics_tracker.track_event(user_id, "image_generation", {
        "type": generation_type,
        "success": success,
        "processing_time_ms": processing_time * 1000
    })
