# RFM Insights - Logging Configuration

import os
import logging
import logging.handlers
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'logs'
logs_dir.mkdir(exist_ok=True)

# Define log file paths
app_log_file = logs_dir / 'app.log'
error_log_file = logs_dir / 'error.log'
access_log_file = logs_dir / 'access.log'

# Configure logging formatters
standard_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
)

# Configure handlers
def get_file_handler(log_file, level, formatter, max_bytes=10485760, backup_count=5):
    """Create a rotating file handler"""
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler

def get_console_handler(level=logging.INFO):
    """Create a console handler"""
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(standard_formatter)
    return handler

# Configure root logger
def configure_root_logger(level=logging.INFO):
    """Configure the root logger"""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:  
        root_logger.removeHandler(handler)
    
    # Add handlers
    root_logger.addHandler(get_console_handler())
    root_logger.addHandler(get_file_handler(app_log_file, logging.INFO, standard_formatter))
    root_logger.addHandler(get_file_handler(error_log_file, logging.ERROR, detailed_formatter))

# Configure access logger for API requests
def configure_access_logger():
    """Configure the access logger for API requests"""
    access_logger = logging.getLogger('api.access')
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False  # Don't propagate to root logger
    
    # Add handler
    access_logger.addHandler(get_file_handler(access_log_file, logging.INFO, standard_formatter))
    
    return access_logger

# Configure module-specific loggers
def get_logger(name, level=logging.INFO):
    """Get a logger for a specific module"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

# Initialize logging
def setup_logging(debug_mode=False):
    """Setup application logging"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    configure_root_logger(log_level)
    configure_access_logger()
    
    # Log startup message
    logger = get_logger('app')
    logger.info('RFM Insights logging initialized')
    if debug_mode:
        logger.debug('Debug mode enabled')
    
    return logger