# RFM Insights - Monitoring Module

import time
import logging
import functools
import os
from typing import Dict, Any, Optional, Callable
from uuid import uuid4

# Import monitoring configuration
from config.monitoring_config import (
    SENTRY_DSN, 
    SENTRY_ENVIRONMENT, 
    SENTRY_TRACES_SAMPLE_RATE,
    SENTRY_PROFILES_SAMPLE_RATE,
    SENTRY_ENABLE_TRACING,
    PROMETHEUS_METRICS_PORT,
    PROMETHEUS_ENABLE,
    METRICS,
    PERFORMANCE_THRESHOLDS,
    ALERT_EMAIL_RECIPIENTS,
    ALERT_SLACK_WEBHOOK,
    ALERT_CRITICAL_THRESHOLD,
    LOGGING_CONTEXT_FIELDS
)

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize context for request tracking
class RequestContext:
    """Store context information for the current request"""
    _context = {}

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set a context value"""
        cls._context[key] = value

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a context value"""
        return cls._context.get(key, default)

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all context values"""
        return cls._context.copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all context values"""
        cls._context.clear()

    @classmethod
    def generate_request_id(cls) -> str:
        """Generate a unique request ID"""
        request_id = str(uuid4())
        cls.set('request_id', request_id)
        return request_id

# Initialize Prometheus metrics if enabled
if PROMETHEUS_ENABLE:
    try:
        from prometheus_client import Counter, Histogram, Gauge, start_http_server
        
        # Initialize Prometheus metrics
        prometheus_metrics = {}
        
        for metric_name, metric_config in METRICS.items():
            if metric_config['type'] == 'counter':
                prometheus_metrics[metric_name] = Counter(
                    metric_name, 
                    metric_config['description'], 
                    metric_config['labels']
                )
            elif metric_config['type'] == 'histogram':
                prometheus_metrics[metric_name] = Histogram(
                    metric_name, 
                    metric_config['description'], 
                    metric_config['labels'],
                    buckets=metric_config.get('buckets', Histogram.DEFAULT_BUCKETS)
                )
            elif metric_config['type'] == 'gauge':
                prometheus_metrics[metric_name] = Gauge(
                    metric_name, 
                    metric_config['description'], 
                    metric_config['labels']
                )
        
        # Start Prometheus HTTP server
        def start_metrics_server():
            """Start Prometheus metrics server"""
            try:
                start_http_server(PROMETHEUS_METRICS_PORT)
                logger.info(f"Prometheus metrics server started on port {PROMETHEUS_METRICS_PORT}")
            except Exception as e:
                logger.error(f"Failed to start Prometheus metrics server: {str(e)}")
        
        # Function to increment counter metrics
        def increment_counter(metric_name: str, labels: Dict[str, str] = None) -> None:
            """Increment a counter metric"""
            if metric_name in prometheus_metrics:
                try:
                    if labels:
                        prometheus_metrics[metric_name].labels(**labels).inc()
                    else:
                        prometheus_metrics[metric_name].inc()
                except Exception as e:
                    logger.error(f"Failed to increment counter {metric_name}: {str(e)}")
        
        # Function to observe histogram metrics
        def observe_histogram(metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
            """Observe a histogram metric"""
            if metric_name in prometheus_metrics:
                try:
                    if labels:
                        prometheus_metrics[metric_name].labels(**labels).observe(value)
                    else:
                        prometheus_metrics[metric_name].observe(value)
                except Exception as e:
                    logger.error(f"Failed to observe histogram {metric_name}: {str(e)}")
        
        # Function to set gauge metrics
        def set_gauge(metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
            """Set a gauge metric"""
            if metric_name in prometheus_metrics:
                try:
                    if labels:
                        prometheus_metrics[metric_name].labels(**labels).set(value)
                    else:
                        prometheus_metrics[metric_name].set(value)
                except Exception as e:
                    logger.error(f"Failed to set gauge {metric_name}: {str(e)}")
    
    except ImportError:
        logger.warning("Prometheus client not installed. Metrics collection disabled.")
        PROMETHEUS_ENABLE = False

# Initialize Sentry if DSN is provided
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        
        # Configure Sentry SDK
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=SENTRY_ENVIRONMENT,
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
            enable_tracing=SENTRY_ENABLE_TRACING,
            integrations=[
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
                SqlalchemyIntegration(),
                FastApiIntegration()
            ]
        )
        
        logger.info(f"Sentry initialized for environment: {SENTRY_ENVIRONMENT}")
        
        # Function to capture exceptions with Sentry
        def capture_exception(exception: Exception, context: Dict[str, Any] = None) -> None:
            """Capture an exception with Sentry"""
            try:
                # Add request context to Sentry scope
                with sentry_sdk.push_scope() as scope:
                    # Add request context
                    request_context = RequestContext.get_all()
                    for key, value in request_context.items():
                        scope.set_tag(key, value)
                    
                    # Add additional context
                    if context:
                        for key, value in context.items():
                            scope.set_extra(key, value)
                    
                    # Capture the exception
                    sentry_sdk.capture_exception(exception)
            except Exception as e:
                logger.error(f"Failed to capture exception with Sentry: {str(e)}")
    
    except ImportError:
        logger.warning("Sentry SDK not installed. Exception tracking disabled.")

# Alert functions
def send_alert(message: str, level: str = "warning", context: Dict[str, Any] = None) -> None:
    """Send an alert via configured channels"""
    try:
        # Log the alert
        if level == "critical":
            logger.critical(message, extra={"alert": True, "context": context})
        elif level == "error":
            logger.error(message, extra={"alert": True, "context": context})
        else:
            logger.warning(message, extra={"alert": True, "context": context})
        
        # Send email alert if recipients are configured
        if ALERT_EMAIL_RECIPIENTS and any(ALERT_EMAIL_RECIPIENTS):
            _send_email_alert(message, level, context)
        
        # Send Slack alert if webhook is configured
        if ALERT_SLACK_WEBHOOK:
            _send_slack_alert(message, level, context)
    
    except Exception as e:
        logger.error(f"Failed to send alert: {str(e)}")

def _send_email_alert(message: str, level: str, context: Dict[str, Any] = None) -> None:
    """Send an email alert"""
    # This is a placeholder for email alert implementation
    # In a real implementation, you would use an email service to send alerts
    logger.info(f"Email alert would be sent to {ALERT_EMAIL_RECIPIENTS}: {message}")

def _send_slack_alert(message: str, level: str, context: Dict[str, Any] = None) -> None:
    """Send a Slack alert"""
    try:
        import requests
        
        # Prepare Slack message payload
        color = "#ff0000" if level == "critical" else "#ffa500" if level == "error" else "#ffff00"
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"RFM Insights Alert: {level.upper()}",
                    "text": message,
                    "fields": []
                }
            ]
        }
        
        # Add context fields if provided
        if context:
            for key, value in context.items():
                payload["attachments"][0]["fields"].append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
        
        # Send the request to Slack webhook
        response = requests.post(ALERT_SLACK_WEBHOOK, json=payload)
        response.raise_for_status()
    
    except ImportError:
        logger.warning("Requests library not installed. Slack alerts disabled.")
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {str(e)}")

# Performance monitoring decorators
def monitor_performance(func_name: str = None, threshold: float = None, metric_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function name if not provided
            nonlocal func_name
            if not func_name:
                func_name = func.__name__
            
            # Get threshold from configuration if not provided
            nonlocal threshold
            if not threshold and func_name in PERFORMANCE_THRESHOLDS:
                threshold = PERFORMANCE_THRESHOLDS[func_name]
            
            # Start timing
            start_time = time.time()
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Log performance
                logger.debug(
                    f"Performance: {func_name} executed in {execution_time:.4f}s",
                    extra={"execution_time": execution_time, "function": func_name}
                )
                
                # Record metric if Prometheus is enabled
                if PROMETHEUS_ENABLE and metric_name:
                    observe_histogram(metric_name, execution_time, {"function": func_name})
                
                # Check if execution time exceeds threshold
                if threshold and execution_time > threshold:
                    send_alert(
                        f"Performance threshold exceeded: {func_name} took {execution_time:.4f}s (threshold: {threshold}s)",
                        level="warning" if execution_time < threshold * 2 else "error",
                        context={"function": func_name, "execution_time": execution_time, "threshold": threshold}
                    )
                
                return result
            
            except Exception as e:
                # Calculate execution time even if there's an exception
                execution_time = time.time() - start_time
                
                # Log exception with performance information
                logger.error(
                    f"Exception in {func_name}: {str(e)}",
                    exc_info=True,
                    extra={"execution_time": execution_time, "function": func_name}
                )
                
                # Capture exception with Sentry if available
                if 'capture_exception' in globals():
                    capture_exception(e, {"function": func_name, "execution_time": execution_time})
                
                # Re-raise the exception
                raise
        
        return wrapper
    
    # Handle case where decorator is used without arguments
    if callable(func_name):
        f = func_name
        func_name = None
        return decorator(f)
    
    return decorator

# Database query monitoring
def monitor_database_query(query_type: str, table: str = None):
    """Decorator to monitor database query performance"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Start timing
            start_time = time.time()
            
            try:
                # Execute the query
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Log query performance
                logger.debug(
                    f"Database query: {query_type} on {table or 'unknown'} executed in {execution_time:.4f}s",
                    extra={"execution_time": execution_time, "query_type": query_type, "table": table}
                )
                
                # Record metric if Prometheus is enabled
                if PROMETHEUS_ENABLE:
                    observe_histogram(
                        "database_query_duration_seconds", 
                        execution_time, 
                        {"query_type": query_type, "table": table or "unknown"}
                    )
                
                # Check if execution time exceeds threshold
                threshold = PERFORMANCE_THRESHOLDS.get("database_query_time")
                if threshold and execution_time > threshold:
                    send_alert(
                        f"Database query threshold exceeded: {query_type} on {table or 'unknown'} took {execution_time:.4f}s (threshold: {threshold}s)",
                        level="warning" if execution_time < threshold * 2 else "error",
                        context={"query_type": query_type, "table": table, "execution_time": execution_time, "threshold": threshold}
                    )
                
                return result
            
            except Exception as e:
                # Calculate execution time even if there's an exception
                execution_time = time.time() - start_time
                
                # Log exception with performance information
                logger.error(
                    f"Exception in database query {query_type} on {table or 'unknown'}: {str(e)}",
                    exc_info=True,
                    extra={"execution_time": execution_time, "query_type": query_type, "table": table}
                )
                
                # Capture exception with Sentry if available
                if 'capture_exception' in globals():
                    capture_exception(e, {"query_type": query_type, "table": table, "execution_time": execution_time})
                
                # Re-raise the exception
                raise
        
        return wrapper
    
    return decorator

# API request monitoring middleware for FastAPI
class MonitoringMiddleware:
    """Middleware for monitoring API requests"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # Generate request ID
        request_id = RequestContext.generate_request_id()
        
        # Extract request information
        method = scope.get("method", "")
        path = scope.get("path", "")
        
        # Set request context
        RequestContext.set("endpoint", path)
        RequestContext.set("http_method", method)
        
        # Start timing
        start_time = time.time()
        
        # Process the request
        try:
            # Call the next middleware or route handler
            await self.app(scope, receive, send)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record metrics if Prometheus is enabled
            if PROMETHEUS_ENABLE:
                # Increment request counter
                increment_counter(
                    "http_requests_total", 
                    {"method": method, "endpoint": path, "status": "success"}
                )
                
                # Record request duration
                observe_histogram(
                    "http_request_duration_seconds", 
                    response_time, 
                    {"method": method, "endpoint": path}
                )
            
            # Check if response time exceeds threshold
            threshold = PERFORMANCE_THRESHOLDS.get("api_response_time")
            if threshold and response_time > threshold:
                send_alert(
                    f"API response time threshold exceeded: {method} {path} took {response_time:.4f}s (threshold: {threshold}s)",
                    level="warning" if response_time < threshold * 2 else "error",
                    context={"method": method, "endpoint": path, "response_time": response_time, "threshold": threshold}
                )
        
        except Exception as e:
            # Calculate response time even if there's an exception
            response_time = time.time() - start_time
            
            # Record metrics for failed request
            if PROMETHEUS_ENABLE:
                increment_counter(
                    "http_requests_total", 
                    {"method": method, "endpoint": path, "status": "error"}
                )
            
            # Log exception
            logger.error(
                f"Exception in API request {method} {path}: {str(e)}",
                exc_info=True,
                extra={"response_time": response_time, "method": method, "endpoint": path}
            )
            
            # Capture exception with Sentry if available
            if 'capture_exception' in globals():
                capture_exception(e, {"method": method, "endpoint": path, "response_time": response_time})
            
            # Re-raise the exception
            raise
        
        finally:
            # Clear request context
            RequestContext.clear()

# System monitoring functions
def monitor_system_resources():
    """Monitor system resources (CPU, memory) and record metrics"""
    try:
        import psutil
        
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used
        
        # Log resource usage
        logger.debug(
            f"System resources: CPU: {cpu_percent}%, Memory: {memory_percent}% ({memory_used / (1024 * 1024):.1f} MB)",
            extra={"cpu_percent": cpu_percent, "memory_percent": memory_percent, "memory_used": memory_used}
        )
        
        # Record metrics if Prometheus is enabled
        if PROMETHEUS_ENABLE:
            set_gauge("cpu_usage_percent", cpu_percent, {"service": "api"})
            set_gauge("memory_usage_bytes", memory_used, {"service": "api"})
        
        # Check if resource usage exceeds thresholds
        cpu_threshold = PERFORMANCE_THRESHOLDS.get("cpu_usage_percent")
        if cpu_threshold and cpu_percent > cpu_threshold:
            send_alert(
                f"CPU usage threshold exceeded: {cpu_percent}% (threshold: {cpu_threshold}%)",
                level="warning" if cpu_percent < cpu_threshold * 1.2 else "error",
                context={"cpu_percent": cpu_percent, "threshold": cpu_threshold}
            )
        
        memory_threshold = PERFORMANCE_THRESHOLDS.get("memory_usage_percent")
        if memory_threshold and memory_percent > memory_threshold:
            send_alert(
                f"Memory usage threshold exceeded: {memory_percent}% (threshold: {memory_threshold}%)",
                level="warning" if memory_percent < memory_threshold * 1.2 else "error",
                context={"memory_percent": memory_percent, "threshold": memory_threshold}
            )
    
    except ImportError:
        logger.warning("psutil library not installed. System monitoring disabled.")
    except Exception as e:
        logger.error(f"Failed to monitor system resources: {str(e)}")

# Initialize monitoring
def initialize_monitoring():
    """Initialize monitoring components"""
    try:
        # Start Prometheus metrics server if enabled
        if PROMETHEUS_ENABLE and 'start_metrics_server' in globals():
            start_metrics_server()
        
        # Log initialization
        logger.info("Monitoring system initialized")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {str(e)}")
        return False