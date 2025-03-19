# RFM Insights - Environment Validation Module

import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger('app.config')

class EnvValidator:
    """Validates environment variables and their values"""
    
    def __init__(self):
        self.required_vars = [
            'DATABASE_URL',
            'JWT_SECRET_KEY'
        ]
        
        self.optional_vars = [
            'OPENAI_API_KEY'
        ]
        
        self.sensitive_vars = [
            'JWT_SECRET_KEY',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'OPENAI_API_KEY'
        ]
        
        self.default_values = {
            'JWT_SECRET_KEY': 'your-secret-key-should-be-very-long-and-secure',
            'OPENAI_API_KEY': 'your-secret-key'
        }
        
        self.validation_errors = []
    
    def validate_required_vars(self) -> bool:
        """Check if all required environment variables are set"""
        missing_vars = []
        
        for var in self.required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False
        
        return True
    
    def validate_sensitive_vars(self) -> bool:
        """Check if sensitive variables have been changed from default values and have sufficient security"""
        unchanged_vars = []
        insecure_vars = []
        
        for var in self.sensitive_vars:
            env_value = os.getenv(var)
            
            # Skip validation for optional variables that are not set
            if not env_value and var in self.optional_vars:
                continue
                
            if env_value and var in self.default_values:
                if env_value == self.default_values[var]:
                    unchanged_vars.append(var)
            
            # Additional security checks for specific variables
            if var == 'JWT_SECRET_KEY' and env_value and len(env_value) < 32:
                insecure_vars.append(f"{var} (too short, should be at least 32 characters)")
        
        has_errors = False
        
        if unchanged_vars:
            error_msg = f"Default values detected for sensitive variables: {', '.join(unchanged_vars)}"
            self.validation_errors.append(error_msg)
            logger.warning(error_msg)
            has_errors = True
        
        if insecure_vars:
            error_msg = f"Insecure values detected for sensitive variables: {', '.join(insecure_vars)}"
            self.validation_errors.append(error_msg)
            logger.warning(error_msg)
            has_errors = True
        
        return not has_errors
    
    def validate_database_url(self) -> bool:
        """Validate database URL format"""
        db_url = os.getenv('DATABASE_URL')
        if db_url and 'postgresql://' not in db_url:
            error_msg = "DATABASE_URL must be in format: postgresql://user:password@host/dbname"
            self.validation_errors.append(error_msg)
            logger.error(error_msg)
            return False
        
        return True
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validations and return results"""
        self.validation_errors = []
        
        required_valid = self.validate_required_vars()
        sensitive_valid = self.validate_sensitive_vars()
        db_url_valid = self.validate_database_url()
        
        all_valid = required_valid and sensitive_valid and db_url_valid
        
        return {
            "valid": all_valid,
            "errors": self.validation_errors
        }


def validate_environment() -> Dict[str, Any]:
    """Validate environment variables and return validation results"""
    validator = EnvValidator()
    return validator.validate_all()


def check_environment(exit_on_error: bool = False) -> bool:
    """Check environment variables and optionally exit on validation errors"""
    validation_result = validate_environment()
    
    if not validation_result["valid"]:
        logger.error("Environment validation failed!")
        for error in validation_result["errors"]:
            logger.error(f"  - {error}")
        
        if exit_on_error:
            logger.critical("Exiting application due to environment validation errors")
            exit(1)
        
        return False
    
    logger.info("Environment validation successful")
    return True