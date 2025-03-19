# RFM Insights - Database Connection Helper

import os
import socket
import logging

logger = logging.getLogger('app.database')

def is_running_in_docker():
    """
    Detect if the application is running inside a Docker container
    """
    try:
        with open('/proc/1/cgroup', 'r') as f:
            return 'docker' in f.read()
    except:
        # If we can't read the file, we're probably not in Docker
        return False

def get_database_url():
    """
    Get the appropriate database URL based on the environment
    
    If running in Docker, use the container name as the host
    If running standalone, use localhost or the environment-specified host
    """
    # Get the database URL from environment
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        return None
    
    # If we're not in Docker and the URL contains a container name, replace it with localhost
    if not is_running_in_docker() and 'rfminsights-postgres' in db_url:
        logger.info("Running outside Docker, adjusting database connection")
        # Replace the container name with localhost
        db_url = db_url.replace('rfminsights-postgres', 'localhost')
        logger.info(f"Adjusted DATABASE_URL: {db_url}")
    
    return db_url

def check_database_connection(db_url=None):
    """
    Check if the database is reachable
    """
    if not db_url:
        db_url = get_database_url()
    
    if not db_url:
        return False
    
    # Extract host and port from the database URL
    # Format: postgresql://user:password@host:port/dbname
    try:
        host = db_url.split('@')[1].split('/')[0].split(':')[0]
        port = 5432  # Default PostgreSQL port
        
        # If port is specified in the URL
        if ':' in db_url.split('@')[1].split('/')[0]:
            port = int(db_url.split('@')[1].split('/')[0].split(':')[1])
        
        # Try to connect to the database host
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex((host, port))
        s.close()
        
        return result == 0
    except Exception as e:
        logger.error(f"Error checking database connection: {e}")
        return False