#!/usr/bin/env python3
"""
GitHub Actions Configuration Module

This module provides configuration management specifically for GitHub Actions environment.
It reads API keys and configuration from environment variables instead of local files.
"""

import os
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_github_actions() -> bool:
    """Check if running in GitHub Actions environment."""
    return os.getenv('TJI_ENVIRONMENT') == 'github_actions' or os.getenv('GITHUB_ACTIONS') == 'true'

def get_groq_api_key() -> Optional[str]:
    """Get Groq API key from environment variables."""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        logger.warning("GROQ_API_KEY not found in environment variables")
        # Fallback to hardcoded key for development (not recommended for production)
        return "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"
    return api_key

def get_tinyurl_api_key() -> Optional[str]:
    """Get TinyURL API key from environment variables."""
    api_key = os.getenv('TINYURL_API_KEY')
    if not api_key:
        logger.warning("TINYURL_API_KEY not found in environment variables")
        # Fallback to hardcoded key for development
        return "Rmg2VwW1ZBaL9LP3myDkCtq7AzFXWg8csW5CwXIGmBW5iAkUy3gn8mmwmmZq"
    return api_key

def get_twilio_config() -> Dict[str, Optional[str]]:
    """Get Twilio configuration from environment variables."""
    config = {
        'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
        'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
        'phone_from': os.getenv('TWILIO_PHONE_FROM'),
        'phone_to': os.getenv('TWILIO_PHONE_TO')
    }
    
    missing_keys = [key for key, value in config.items() if not value]
    if missing_keys:
        logger.warning(f"Missing Twilio configuration: {missing_keys}")
        # Fallback configuration for development
        if not config['account_sid']:
            config['account_sid'] = "AC185a7783037edc716eaff3ca28a5993c"
        if not config['auth_token']:
            config['auth_token'] = "a48df63098f045e09f4db5ce5c881207"
        if not config['phone_from']:
            config['phone_from'] = "whatsapp:+14155238886"
        if not config['phone_to']:
            config['phone_to'] = "whatsapp:+918179399260"
    
    return config

def get_file_paths() -> Dict[str, str]:
    """Get file paths for GitHub Actions environment."""
    if is_github_actions():
        # In GitHub Actions, use absolute paths relative to workspace
        workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
        base_path = workspace
    else:
        # Local development - use relative paths
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return {
        'data_dir': os.path.join(base_path, 'data'),
        'tech_news_history': os.path.join(base_path, 'data', 'tech_news_history.json'),
        'upskill_history': os.path.join(base_path, 'data', 'upskill_articles_history.json'),
        'seen_internships': os.path.join(base_path, 'data', 'seen_internships.json'),
        'seen_jobs': os.path.join(base_path, 'data', 'seen_jobs.json'),
        'tinyurl_counter': os.path.join(base_path, 'data', 'tinyurl_run_counter.json'),
        'ai_selected_article': os.path.join(base_path, 'data', 'ai_selected_article.json'),
        'selected_internship': os.path.join(base_path, 'data', 'selected_internship.json'),
        'selected_job': os.path.join(base_path, 'data', 'selected_job.json'),
        'ai_selected_upskill': os.path.join(base_path, 'data', 'ai_selected_upskill_article.json'),
        'daily_digest': os.path.join(base_path, 'data', 'daily_tech_digest.json'),
        'shortened_urls': os.path.join(base_path, 'data', 'shortened_urls_digest.json'),
        'tji_message': os.path.join(base_path, 'data', 'tji_daily_message.json'),
        'logs_dir': os.path.join(base_path, 'data')
    }

def get_request_config() -> Dict[str, Any]:
    """Get request configuration for web scraping."""
    return {
        'timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'delay_range': (1, 3),  # seconds between requests
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }

def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    logger.info("🔍 Validating GitHub Actions environment...")
    
    required_vars = [
        'GROQ_API_KEY',
        'TINYURL_API_KEY', 
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_FROM',
        'TWILIO_PHONE_TO'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.info("Using fallback configuration for development")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def log_environment_info():
    """Log environment information for debugging."""
    logger.info("🔧 Environment Information:")
    logger.info(f"  GitHub Actions: {is_github_actions()}")
    logger.info(f"  Python Path: {os.getenv('PYTHONPATH', 'Not set')}")
    logger.info(f"  Working Directory: {os.getcwd()}")
    logger.info(f"  TJI Environment: {os.getenv('TJI_ENVIRONMENT', 'Not set')}")
    
    # Log API key status (without revealing actual keys)
    api_keys = {
        'GROQ_API_KEY': bool(os.getenv('GROQ_API_KEY')),
        'TINYURL_API_KEY': bool(os.getenv('TINYURL_API_KEY')),
        'TWILIO_ACCOUNT_SID': bool(os.getenv('TWILIO_ACCOUNT_SID')),
        'TWILIO_AUTH_TOKEN': bool(os.getenv('TWILIO_AUTH_TOKEN'))
    }
    
    logger.info("  API Keys Status:")
    for key, status in api_keys.items():
        logger.info(f"    {key}: {'✅ Set' if status else '❌ Missing'}")

# Configuration constants for backward compatibility
REQUEST_TIMEOUT = get_request_config()['timeout']
MAX_RETRIES = get_request_config()['max_retries']

# File paths
PATHS = get_file_paths()

# Output file mappings for backward compatibility
OUTPUT_FILES = {
    'tech_news': PATHS['ai_selected_article'],
    'internships': PATHS['selected_internship'],
    'jobs': PATHS['selected_job'],
    'upskill': PATHS['ai_selected_upskill'],
    'daily_digest': PATHS['daily_digest'],
    'shortened_urls': PATHS['shortened_urls'],
    'tji_message': PATHS['tji_message']
}

# Initialize environment on import
if __name__ == "__main__":
    log_environment_info()
    validate_environment()
else:
    # Only log basic info when imported
    if is_github_actions():
        logger.info("🚀 GitHub Actions configuration loaded")
        validate_environment()
