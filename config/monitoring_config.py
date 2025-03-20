# RFM Insights - Monitoring Configuration

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sentry Configuration
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2"))
SENTRY_PROFILES_SAMPLE_RATE = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))
SENTRY_ENABLE_TRACING = os.getenv("SENTRY_ENABLE_TRACING", "True").lower() == "true"

# Prometheus Configuration
PROMETHEUS_METRICS_PORT = int(os.getenv("PROMETHEUS_METRICS_PORT", "9090"))
PROMETHEUS_ENABLE = os.getenv("PROMETHEUS_ENABLE", "True").lower() == "true"

# Grafana Configuration
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://grafana:3000")

# Alert Configuration
ALERT_EMAIL_RECIPIENTS = os.getenv("ALERT_EMAIL_RECIPIENTS", "").split(",")
ALERT_SLACK_WEBHOOK = os.getenv("ALERT_SLACK_WEBHOOK", "")
ALERT_CRITICAL_THRESHOLD = int(os.getenv("ALERT_CRITICAL_THRESHOLD", "3"))

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "api_response_time": float(os.getenv("THRESHOLD_API_RESPONSE_TIME", "1.0")),  # seconds
    "database_query_time": float(os.getenv("THRESHOLD_DATABASE_QUERY_TIME", "0.5")),  # seconds
    "memory_usage_percent": float(os.getenv("THRESHOLD_MEMORY_USAGE", "85.0")),  # percentage
    "cpu_usage_percent": float(os.getenv("THRESHOLD_CPU_USAGE", "80.0"))  # percentage
}

# Logging Context Fields
LOGGING_CONTEXT_FIELDS = [
    "request_id",
    "user_id",
    "tenant_id",
    "ip_address",
    "user_agent",
    "endpoint",
    "http_method",
    "status_code",
    "response_time"
]

# Define metrics to collect
METRICS = {
    "http_requests_total": {
        "type": "counter",
        "description": "Total number of HTTP requests",
        "labels": ["method", "endpoint", "status"]
    },
    "http_request_duration_seconds": {
        "type": "histogram",
        "description": "HTTP request duration in seconds",
        "labels": ["method", "endpoint"],
        "buckets": [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    },
    "database_query_duration_seconds": {
        "type": "histogram",
        "description": "Database query duration in seconds",
        "labels": ["query_type", "table"],
        "buckets": [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
    },
    "active_users": {
        "type": "gauge",
        "description": "Number of active users",
        "labels": ["tenant"]
    },
    "rfm_analysis_duration_seconds": {
        "type": "histogram",
        "description": "RFM analysis duration in seconds",
        "labels": ["dataset_size", "analysis_type"],
        "buckets": [0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
    },
    "memory_usage_bytes": {
        "type": "gauge",
        "description": "Memory usage in bytes",
        "labels": ["service"]
    },
    "cpu_usage_percent": {
        "type": "gauge",
        "description": "CPU usage percentage",
        "labels": ["service"]
    }
}