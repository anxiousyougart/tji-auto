#!/usr/bin/env python3
"""
Configuration file for the Daily Tech Digest Pipeline

This file contains all configuration settings including API keys, timeouts,
and other parameters used across all scrapers.

Author: Augment Agent
Date: 2025-01-25
"""

import os
from typing import Dict, Any

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Groq API Configuration
# Priority: Environment variable > Config file > Working fallback key
GROQ_API_KEY = os.getenv('GROQ_API_KEY', "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")

# Fallback behavior when API key is not available
ENABLE_AI_SELECTION = bool(GROQ_API_KEY)

# ============================================================================
# SCRAPER CONFIGURATION
# ============================================================================

# Request settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
REQUEST_DELAY = 1  # seconds between requests

# User agent for web scraping
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Headers for requests
DEFAULT_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# ============================================================================
# DATE FILTERING CONFIGURATION
# ============================================================================

# Date filtering windows (in hours)
TECH_NEWS_DATE_WINDOW = 48  # 2 days
INTERNSHIP_DATE_WINDOW = 48  # 2 days
JOB_DATE_WINDOW = 24  # 1 day (strict)
UPSKILL_DATE_WINDOW = 168  # 7 days (more lenient for educational content)

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Output file names
OUTPUT_FILES = {
    'tech_news': 'ai_selected_article.json',
    'internships': 'selected_internship.json',
    'jobs': 'selected_job.json',
    'upskill': 'ai_selected_upskill_article.json',
    'daily_digest': 'daily_tech_digest.json'
}

# Log file names
LOG_FILES = {
    'pipeline': 'daily_digest_pipeline.log',
    'tech_news': 'tech_news_scraper.log',
    'internships': 'internship_scraper.log',
    'jobs': 'jobs_scraper.log',
    'upskill': 'upskill_scraper.log'
}

# ============================================================================
# PIPELINE CONFIGURATION
# ============================================================================

# Timeout settings for each scraper (in seconds)
SCRAPER_TIMEOUTS = {
    'tech_news': 300,    # 5 minutes
    'internships': 600,  # 10 minutes
    'jobs': 600,         # 10 minutes
    'upskill': 300,      # 5 minutes
    'aggregator': 60,    # 1 minute
    'url_shortener': 300 # 5 minutes
}

# ============================================================================
# TINYURL SHORTENER CONFIGURATION
# ============================================================================

# TinyURL API Configuration
TINYURL_CONFIG = {
    'api_key': 'Rmg2VwW1ZBaL9LP3myDkCtq7AzFXWg8csW5CwXIGmBW5iAkUy3gn8mmwmmZq',
    'api_endpoint': 'https://api.tinyurl.com/create',
    'domain': 'tinyurl.com',
    'input_file': 'daily_tech_digest.json',
    'output_file': 'shortened_urls_digest.json',
    'log_file': 'tinyurl_shortener.log',
    'request_timeout': 30,
    'max_retries_per_url': 3,
    'delay_between_requests': 1,  # seconds
    'rate_limit_delay': 5,  # seconds to wait when rate limited
    'counter_file': 'tinyurl_run_counter.json'
}

# Category alias mappings for shortened URLs (TinyURL compatible format)
URL_ALIAS_FORMATS = {
    'tech_news': 'tech-news-tji-{}',
    'internships': 'internship-tji-{}',
    'jobs': 'placement-update-tji-{}',
    'upskill_articles': 'upskill-tji-{}'
}

# Counter file to track script runs
TINYURL_COUNTER_FILE = 'tinyurl_run_counter.json'

# ============================================================================
# FALLBACK BEHAVIOR CONFIGURATION
# ============================================================================

# What to do when scrapers fail
CREATE_FALLBACK_FILES = True
CONTINUE_ON_FAILURE = True
MIN_SUCCESSFUL_SCRAPERS = 1  # Minimum scrapers needed for pipeline success

# ============================================================================
# KEYWORD FILTERING CONFIGURATION
# ============================================================================

# Keywords for tech news filtering
TECH_NEWS_INCLUDE_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 'deep learning',
    'software', 'programming', 'developer', 'technology', 'tech',
    'startup', 'innovation', 'breakthrough', 'algorithm', 'data science',
    'cloud computing', 'cybersecurity', 'blockchain', 'cryptocurrency',
    'mobile app', 'web development', 'API', 'framework', 'library',
    'open source', 'github', 'coding', 'computer science'
]

TECH_NEWS_EXCLUDE_KEYWORDS = [
    'opinion', 'editorial', 'blog post', 'personal view', 'commentary',
    'drama', 'controversy', 'gossip', 'rumor', 'speculation',
    'politics', 'lawsuit', 'legal battle', 'court case'
]

# Keywords for job filtering
JOB_INCLUDE_KEYWORDS = [
    'engineer', 'developer', 'analyst', 'specialist', 'programmer',
    'software', 'technical', 'IT', 'computer science', 'technology'
]

JOB_EXCLUDE_KEYWORDS = [
    'intern', 'internship', 'trainee', 'graduate trainee', 'apprentice',
    'senior', 'lead', 'principal', 'manager', 'director', 'head of'
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_groq_api_key() -> str:
    """
    Get Groq API key with fallback logic.

    Returns:
        API key string or None if not available
    """
    return GROQ_API_KEY

def is_ai_enabled() -> bool:
    """
    Check if AI selection is enabled (API key available).

    Returns:
        True if AI selection is available, False otherwise
    """
    return ENABLE_AI_SELECTION

def get_config_summary() -> Dict[str, Any]:
    """
    Get a summary of current configuration.

    Returns:
        Dictionary with configuration summary
    """
    return {
        'ai_enabled': is_ai_enabled(),
        'api_key_available': bool(GROQ_API_KEY),
        'fallback_files': CREATE_FALLBACK_FILES,
        'continue_on_failure': CONTINUE_ON_FAILURE,
        'scraper_timeouts': SCRAPER_TIMEOUTS,
        'date_windows': {
            'tech_news': TECH_NEWS_DATE_WINDOW,
            'internships': INTERNSHIP_DATE_WINDOW,
            'jobs': JOB_DATE_WINDOW,
            'upskill': UPSKILL_DATE_WINDOW
        }
    }

def print_config_status():
    """Print current configuration status."""
    print("🔧 CONFIGURATION STATUS")
    print("-" * 40)

    api_status = "✅ Available" if is_ai_enabled() else "❌ Not Available"
    print(f"🤖 AI Selection: {api_status}")

    if not is_ai_enabled():
        print("   ⚠️  Set GROQ_API_KEY environment variable to enable AI selection")
        print("   📝 Scrapers will use fallback selection methods")

    print(f"📁 Fallback Files: {'✅ Enabled' if CREATE_FALLBACK_FILES else '❌ Disabled'}")
    print(f"🔄 Continue on Failure: {'✅ Yes' if CONTINUE_ON_FAILURE else '❌ No'}")
    print(f"⏱️  Timeouts: Tech({SCRAPER_TIMEOUTS['tech_news']}s), Jobs({SCRAPER_TIMEOUTS['jobs']}s)")
    print()

if __name__ == "__main__":
    print_config_status()

    print("📋 FULL CONFIGURATION:")
    print("-" * 40)
    import json
    config = get_config_summary()
    print(json.dumps(config, indent=2))
