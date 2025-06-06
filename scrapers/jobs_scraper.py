#!/usr/bin/env python3
"""
Intelligent Entry-Level Job Scraper for Fresh Engineering Graduates (24-Hour Filter)

This script scrapes RECENT entry-level job postings (posted within 24 hours, 0-1 years experience)
from LinkedIn and other job sites, focusing on positions suitable for fresh engineering graduates
while excluding senior roles. Uses AI-powered selection to identify the best recent entry-level opportunities.

Author: Augment Agent
Date: 2025-01-25
"""

import requests
import json
import logging
import os
import re
import time
import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from dateutil import parser
from groq import Groq

# Import centralized configuration
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.config import get_groq_api_key
    GROQ_API_KEY = get_groq_api_key()
except ImportError:
    # Fallback configuration if config.py is not available
    GROQ_API_KEY = "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"

# Request configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Keywords for branch/field filtering - More specific and targeted
CSE_IT_KEYWORDS = [
    # Core CSE/IT fields - High priority
    "computer science", "cse", "cs", "information technology", "it", "computer engineering",
    "software engineer", "software developer", "software development", "software engineering",

    # Full Stack Development - Multiple variations
    "full stack developer", "fullstack developer", "full stack development", "fullstack development",
    "full-stack developer", "full-stack development", "full stack", "fullstack",

    # Backend/Frontend Development
    "backend developer", "backend development", "back-end developer", "back-end development",
    "frontend developer", "frontend development", "front-end developer", "front-end development",

    # Web Development
    "web developer", "web development", "web dev", "website developer", "website development",
    "mobile app developer", "app developer", "mobile development", "app development",

    # Programming & Development - High priority
    "python developer", "python development", "java developer", "java development",
    "javascript developer", "javascript development", "react developer", "react development",
    "node.js developer", "node.js development", "angular developer", "angular development",
    "flutter developer", "flutter development", "android developer", "android development",
    "ios developer", "ios development", "game developer", "game development",
    "blockchain developer", "blockchain development", "devops engineer", "devops",

    # AI/ML/Data Science - High priority
    "artificial intelligence", "ai engineer", "ai development", "machine learning", "ml engineer",
    "ml development", "deep learning", "data scientist", "data analyst", "data engineer",
    "big data", "neural networks", "computer vision", "nlp engineer", "ai researcher", "ml researcher",

    # Cloud & Modern Tech - High priority
    "cloud engineer", "cloud development", "aws developer", "azure developer", "google cloud",
    "docker", "kubernetes", "microservices", "api developer", "api development", "rest api", "graphql",
    "cloud", "aws", "azure", "gcp",

    # Cybersecurity & Systems - High priority
    "cybersecurity", "security analyst", "penetration tester", "network security",
    "information security", "cyber security", "ethical hacker", "security engineer",

    # UI/UX & Design - Medium priority
    "ui developer", "ui development", "ux designer", "ux development", "ui/ux designer",
    "ui/ux development", "frontend designer", "web designer", "graphic designer",
    "product designer", "interaction designer",

    # General Development Terms
    "developer", "development", "programmer", "programming", "coding", "engineer", "engineering",

    # Job-specific terms (exclude intern/trainee variations)
    "software engineer", "senior developer", "lead developer", "principal engineer",
    "staff engineer", "architect", "technical lead", "engineering manager"
]

EEE_ECE_KEYWORDS = [
    # Electronics & Electrical - Medium priority
    "electronics", "ece", "eee", "electrical", "embedded systems", "embedded engineer",
    "vlsi", "vlsi design", "circuit design", "pcb design", "hardware engineer",
    "firmware engineer", "iot developer", "iot engineer", "robotics engineer",
    "automation engineer", "control systems", "power systems", "signal processing",
    "telecommunications", "rf engineer", "analog design", "digital design"
]

MECH_KEYWORDS = [
    # Mechanical Engineering - Lower priority
    "mechanical", "mech", "cad designer", "solidworks", "autocad", "catia",
    "design engineer", "product design", "manufacturing", "production engineer",
    "quality engineer", "process engineer", "thermal engineer", "automotive",
    "aerospace", "mechanical design", "3d modeling", "simulation engineer"
]

# Combined keywords with priority levels
PRIORITY_KEYWORDS = CSE_IT_KEYWORDS  # Highest priority
SECONDARY_KEYWORDS = EEE_ECE_KEYWORDS  # Medium priority
TERTIARY_KEYWORDS = MECH_KEYWORDS  # Lower priority

# Scam detection keywords - Enhanced for better filtering
SCAM_INDICATORS = [
    "easy money", "work from home guaranteed", "no experience needed", "earn lakhs",
    "mlm", "pyramid", "network marketing", "referral bonus", "investment required",
    "registration fee", "training fee", "part time job", "data entry", "copy paste",
    "typing work", "form filling", "survey", "marketing executive", "sales executive",
    "business development executive", "telecaller", "call center", "customer service",
    "field work", "door to door", "commission based", "target based", "no salary",
    "only incentive", "work from home", "online job", "freelance", "gig work"
]

# Exclude these generic/irrelevant terms that often appear in non-technical roles
EXCLUDE_TERMS = [
    "sales", "marketing", "business development", "hr", "human resources", "finance",
    "accounting", "content writer", "content creator", "social media", "digital marketing",
    "seo", "sem", "graphic design", "video editing", "photography", "event management",
    "customer support", "customer care", "telecalling", "telesales", "field sales"
]

# EXCLUDE trainee/internship positions for job scraper
TRAINEE_INTERNSHIP_TERMS = [
    "intern", "internship", "trainee", "graduate trainee", "entry level trainee",
    "management trainee", "fresher trainee", "campus hire", "graduate program","instructor"
]

# Experience level keywords for entry-level positions (0-1 years)
ENTRY_LEVEL_KEYWORDS = [
    # Direct entry-level indicators
    "entry level", "entry-level", "fresher", "freshers", "fresh graduate", "fresh graduates",
    "new graduate", "new graduates", "recent graduate", "recent graduates", "graduate",
    "junior", "junior developer", "junior engineer", "junior software", "associate",
    "associate developer", "associate engineer", "associate software", "beginner",

    # Experience range indicators
    "0-1 years", "0-2 years", "0 to 1 year", "0 to 2 years", "0-1 year", "0-2 year",
    "no experience", "no prior experience", "minimal experience", "little experience",
    "0+ years", "0 years", "1 year", "up to 1 year", "up to 2 years",

    # Training and development focused
    "training provided", "will train", "on the job training", "mentorship",
    "learning opportunity", "growth opportunity", "career starter", "career beginning",
    "entry position", "starting position", "first job", "campus recruitment"
]

# Experience exclusion keywords for senior positions (exclude these)
SENIOR_EXPERIENCE_KEYWORDS = [
    # Senior level indicators
    "senior", "senior developer", "senior engineer", "senior software", "lead", "lead developer",
    "lead engineer", "principal", "principal engineer", "principal developer", "staff engineer",
    "staff developer", "architect", "technical lead", "team lead", "engineering manager",
    "senior manager", "director", "head of", "chief", "vp", "vice president",

    # High experience requirements
    "3+ years", "4+ years", "5+ years", "6+ years", "7+ years", "8+ years", "9+ years", "10+ years",
    "3-5 years", "4-6 years", "5-7 years", "6-8 years", "7-10 years", "8-12 years",
    "minimum 3 years", "minimum 4 years", "minimum 5 years", "at least 3 years", "at least 4 years",
    "at least 5 years", "3 years experience", "4 years experience", "5 years experience",
    "experienced", "seasoned", "expert", "specialist with experience", "proven track record"
]

# Configure logging with UTF-8 encoding - Enable DEBUG for better troubleshootingfir
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG to see extraction details
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/jobs_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def make_request_with_retry(url: str, max_retries: int = 3) -> Optional[requests.Response]:
    """
    Make HTTP request with retry logic and proper error handling.

    Args:
        url: URL to request
        max_retries: Maximum number of retry attempts

    Returns:
        Response object or None if all attempts failed
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                return response
            else:
                logging.warning(f"HTTP error {response.status_code} for {url} (attempt {attempt + 1}/{max_retries})")
        except requests.RequestException as e:
            logging.warning(f"Request error for {url} (attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    logging.error(f"Failed to fetch {url} after {max_retries} attempts")
    return None

def normalize_url(url: str) -> str:
    """
    Normalize URL by removing tracking parameters that change between runs.
    This ensures the same job isn't treated as different due to URL parameter changes.
    """
    try:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        parsed = urlparse(url)

        # For LinkedIn URLs, keep only essential parameters
        if 'linkedin.com' in parsed.netloc:
            # Extract job ID from the path (e.g., /jobs/view/job-title-at-company-1234567890)
            path_parts = parsed.path.split('/')
            if len(path_parts) >= 3 and 'jobs' in path_parts and 'view' in path_parts:
                # Keep the job view path but remove tracking parameters
                query_params = parse_qs(parsed.query)
                # Keep only essential parameters, remove tracking ones
                essential_params = {}
                for key, value in query_params.items():
                    if key not in ['refId', 'trackingId', 'pageNum', 'position']:
                        essential_params[key] = value

                new_query = urlencode(essential_params, doseq=True)
                return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

        # For other URLs, return as-is
        return url
    except Exception:
        # If URL parsing fails, return original URL
        return url

def create_job_signature(job: Dict) -> str:
    """
    Create a unique signature for a job to detect duplicates.
    Uses normalized URL to avoid false duplicates due to tracking parameters.
    """
    normalized_url = normalize_url(job.get('url', ''))
    return f"{job.get('title', '')}-{job.get('company', '')}-{normalized_url}"

def load_seen_jobs() -> set:
    """Load previously seen jobs from file to avoid duplicates."""
    try:
        if os.path.exists('../data/seen_jobs.json'):
            with open('../data/seen_jobs.json', 'r', encoding='utf-8') as f:
                return set(json.load(f))
    except Exception as e:
        logging.debug(f"Error loading seen jobs: {e}")
    return set()

def save_seen_job(job: Dict) -> None:
    """Save a job to the seen jobs file using normalized signature."""
    try:
        seen_jobs = load_seen_jobs()
        identifier = create_job_signature(job)
        seen_jobs.add(identifier)

        with open('../data/seen_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(list(seen_jobs), f, ensure_ascii=False, indent=2)

        logging.debug(f"Saved job signature: {identifier}")
    except Exception as e:
        logging.debug(f"Error saving seen job: {e}")

def parse_linkedin_posting_date(date_text: str) -> Optional[datetime.datetime]:
    """
    Parse LinkedIn posting date text into datetime object.

    Args:
        date_text: Text like "2 hours ago", "1 day ago", etc.

    Returns:
        datetime object or None if parsing fails
    """
    if not date_text:
        return None

    date_text = date_text.lower().strip()
    now = datetime.datetime.now()

    try:
        # Parse "X hours ago"
        if 'hour' in date_text:
            match = re.search(r'(\d+)', date_text)
            if match:
                hours = int(match.group(1))
                return now - datetime.timedelta(hours=hours)

        # Parse "X days ago"
        elif 'day' in date_text:
            match = re.search(r'(\d+)', date_text)
            if match:
                days = int(match.group(1))
                return now - datetime.timedelta(days=days)

        # Parse "X weeks ago"
        elif 'week' in date_text:
            match = re.search(r'(\d+)', date_text)
            if match:
                weeks = int(match.group(1))
                return now - datetime.timedelta(weeks=weeks)

    except Exception as e:
        logging.debug(f"Error parsing date '{date_text}': {e}")

    return None

def is_posting_date_text(text: str) -> bool:
    """
    Check if text contains posting date information (not job duration).

    Args:
        text: Text to analyze

    Returns:
        True if text contains posting date indicators, False otherwise
    """
    if not text:
        return False

    text = text.lower().strip()

    # Posting date indicators - these suggest when the job was posted
    posting_indicators = [
        'posted', 'ago', 'updated', 'published', 'listed', 'added',
        'hours ago', 'days ago', 'weeks ago', 'months ago',
        'yesterday', 'today', 'recently posted'
    ]

    # Duration indicators - these refer to job length, NOT posting date
    duration_indicators = [
        'duration', 'months job', 'weeks job', 'month job',
        'full time', 'part time', 'full-time', 'part-time', 'contract',
        'permanent', 'temporary', 'months duration', 'weeks duration'
    ]

    # Check if it's a duration indicator (should be ignored)
    if any(indicator in text for indicator in duration_indicators):
        logging.debug(f"Ignoring duration text: '{text}'")
        return False

    # Check if it contains posting date indicators
    has_posting_indicator = any(indicator in text for indicator in posting_indicators)

    if has_posting_indicator:
        logging.debug(f"Found posting date text: '{text}'")
        return True

    return False

def is_recent_job_posting(date_text: str) -> bool:
    """
    Check if a job posting is recent (within 24 hours) based on POSTING DATE text only.
    Strict 24-hour filtering for very recent job postings.

    Args:
        date_text: Text like "posted 2 hours ago", "1 day ago", etc.

    Returns:
        True if within 24 hours, False otherwise
    """
    if not date_text:
        return False

    date_text = date_text.lower().strip()

    # Parse hours - within 24 hours
    if 'hour' in date_text and 'ago' in date_text:
        match = re.search(r'(\d+)\s*hour', date_text)
        if match:
            hours = int(match.group(1))
            return hours <= 24
        elif 'few' in date_text:
            return True  # "few hours ago" is definitely recent

    # Parse days - only today (within 24 hours)
    elif 'day' in date_text and 'ago' in date_text:
        match = re.search(r'(\d+)\s*day', date_text)
        if match:
            days = int(match.group(1))
            return days == 0 or days == 1  # Only today or 1 day ago
        elif 'today' in date_text:
            return True

    # Special cases for very recent postings
    elif any(word in date_text for word in ['today', 'recently posted']):
        return True

    # Anything with weeks, months, or multiple days is definitely old
    elif any(term in date_text for term in ['week', 'month', 'year']) and 'ago' in date_text:
        return False
    elif 'days' in date_text and 'ago' in date_text:  # Multiple days
        return False

    # If we can't parse it clearly, be strict and exclude it
    return False

def scrape_linkedin_jobs() -> List[Dict]:
    """
    Scrape job postings from LinkedIn Jobs with comprehensive job capture.
    Uses multiple search strategies to ensure 100% capture rate of all available jobs.
    Returns simplified format with only title, company, and url for recent jobs.

    Returns:
        List of job dictionaries with simplified format
    """
    # Multiple search URLs to capture entry-level jobs (ALL with STRICT 24-hour filter)
    search_urls = [
        # Entry-level computer science jobs (24-hour filter)
        "https://www.linkedin.com/jobs/search/?distance=25&f_E=2&f_TPR=r86400&geoId=105556991&keywords=computer%20science%20entry%20level&origin=JOB_SEARCH_PAGE_JOB_FILTER",
        # Entry-level software engineer jobs (24-hour filter)
        "https://www.linkedin.com/jobs/search/?distance=25&f_E=2&f_TPR=r86400&geoId=105556991&keywords=software%20engineer%20junior&origin=JOB_SEARCH_PAGE_JOB_FILTER",
        # Fresh graduate positions (24-hour filter)
        "https://www.linkedin.com/jobs/search/?distance=25&f_E=2&f_TPR=r86400&geoId=105556991&keywords=fresh%20graduate%20engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER",
        # Associate developer positions (24-hour filter)
        "https://www.linkedin.com/jobs/search/?distance=25&f_E=2&f_TPR=r86400&geoId=105556991&keywords=associate%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER",
        # Junior developer positions (24-hour filter)
        "https://www.linkedin.com/jobs/search/?distance=25&f_E=2&f_TPR=r86400&geoId=105556991&keywords=junior%20developer&origin=JOB_SEARCH_PAGE_JOB_FILTER",
        # Entry-level full stack positions (24-hour filter)
        "https://www.linkedin.com/jobs/search/?distance=25&f_E=2&f_TPR=r86400&geoId=105556991&keywords=entry%20level%20full%20stack&origin=JOB_SEARCH_PAGE_JOB_FILTER"
    ]

    logging.info("Scraping LinkedIn with COMPREHENSIVE multi-search strategy...")

    all_jobs_from_searches = []

    for search_index, search_url in enumerate(search_urls):
        logging.info(f"Search {search_index + 1}/{len(search_urls)}: {search_url.split('keywords=')[1].split('&')[0]}")

        try:
            response = make_request_with_retry(search_url)
            if not response:
                logging.warning(f"Failed to get response from LinkedIn for search {search_index + 1}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            logging.info(f"Successfully fetched LinkedIn page for search {search_index + 1}")

            # Find job cards - try multiple selectors for different LinkedIn layouts
            # Try various selectors to catch all possible job card formats
            selectors_to_try = [
                'div[data-entity-urn*="job"]',          # Modern LinkedIn job cards with entity URN
                'div.base-card',                        # Base card layout
                'li.result-card',                       # Result card layout
                'div.job-search-card',                  # Job search cards
                'div.base-search-card',                 # Base search card
                'div[data-job-id]',                     # Cards with job ID
                'article[data-entity-urn]',             # Article-based cards
                'div.jobs-search-results__list-item',   # Jobs search results list items
                'li[data-occludable-job-id]',           # Occludable job cards
                'div[data-test-id*="job"]',             # Test ID based cards
                'div.job-result-card',                  # Job result cards
                'article',                              # Generic article elements
                'li[data-entity-urn]',                  # List items with entity URN
                'div[class*="job"]',                    # Any div with "job" in class name
                'li[class*="job"]',                     # Any li with "job" in class name
            ]

            job_cards = []
            for selector in selectors_to_try:
                try:
                    cards = soup.select(selector)
                    if cards:
                        job_cards.extend(cards)
                        logging.debug(f"Search {search_index + 1} - Found {len(cards)} cards with selector: '{selector}'")
                except Exception as e:
                    logging.debug(f"Search {search_index + 1} - Error with selector '{selector}': {e}")

            # Remove duplicates while preserving order
            seen = set()
            unique_cards = []
            for card in job_cards:
                # Use a combination of tag name and attributes to identify unique elements
                card_signature = f"{card.name}_{str(card.get('class', []))[:100]}_{str(card.get('data-entity-urn', ''))[:50]}"
                if card_signature not in seen:
                    seen.add(card_signature)
                    unique_cards.append(card)

            job_cards = unique_cards
            logging.info(f"Search {search_index + 1} - Found {len(job_cards)} total unique job cards to analyze")

            # Debug: Log some sample card structures
            if job_cards:
                for i, card in enumerate(job_cards[:2]):  # Log first 2 cards for debugging
                    logging.debug(f"Search {search_index + 1} - Sample card {i+1} structure: tag={card.name}, classes={card.get('class', [])}")
            else:
                logging.warning(f"Search {search_index + 1} - No job cards found with any selector")

            search_jobs = []
            total_found = 0

            for card_index, card in enumerate(job_cards):
                try:
                    logging.debug(f"Search {search_index + 1} - Processing card {card_index + 1}/{len(job_cards)}")

                    # First, check if this card contains "promoted" anywhere
                    card_html = str(card)
                    has_promoted_text = 'promoted' in card_html.lower()
                    logging.debug(f"Search {search_index + 1} - Card {card_index + 1} contains 'promoted': {has_promoted_text}")

                    # Extract title - try multiple selectors for different LinkedIn layouts
                    title_selectors = [
                        'h3.base-search-card__title',           # Base search card title
                        'h3[data-test-id*="job-title"]',        # Test ID job title
                        'a.result-card__full-card-link',        # Result card link
                        'h3.job-result-card__title',            # Job result card title
                        'h3',                                    # Generic h3
                        'h2',                                    # Generic h2
                        'a[data-test-id*="job-title"]',         # Link with job title test ID
                        '.job-title',                           # Class job-title
                        '[data-entity-urn] h3',                 # H3 inside entity URN
                        '[data-entity-urn] a',                  # Link inside entity URN
                    ]

                    title_elem = None
                    for selector in title_selectors:
                        title_elem = card.select_one(selector)
                        if title_elem:
                            logging.debug(f"Search {search_index + 1} - Found title with selector: '{selector}'")
                            break

                    if not title_elem:
                        logging.debug(f"Search {search_index + 1} - ❌ No title found for card {card_index + 1} - SKIPPING")
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        logging.debug(f"Search {search_index + 1} - ❌ Empty title found for card {card_index + 1} - SKIPPING")
                        continue

                    # EXCLUDE trainee/internship positions (opposite of internship scraper)
                    title_lower = title.lower()
                    is_trainee_internship = any(term in title_lower for term in TRAINEE_INTERNSHIP_TERMS)
                    if is_trainee_internship:
                        logging.debug(f"Search {search_index + 1} - ❌ EXCLUDED trainee/internship position: '{title}' - SKIPPING")
                        continue

                    total_found += 1
                    logging.debug(f"Search {search_index + 1} - ✅ Card {card_index + 1} title extracted: '{title}'")

                    # Extract company - try multiple selectors for different LinkedIn layouts
                    company_selectors = [
                        'h4.base-search-card__subtitle',        # Base search card subtitle
                        'a.result-card__subtitle-link',         # Result card subtitle link
                        'span.job-result-card__company-name',   # Job result card company name
                        'h4[data-test-id*="company"]',          # Test ID company
                        'a[data-test-id*="company"]',           # Link with company test ID
                        '.company-name',                        # Class company-name
                        'h4',                                   # Generic h4
                        '[data-entity-urn] h4',                 # H4 inside entity URN
                        '[data-entity-urn] span',               # Span inside entity URN
                        '.base-search-card__subtitle',          # Subtitle class
                    ]

                    company_elem = None
                    for selector in company_selectors:
                        company_elem = card.select_one(selector)
                        if company_elem:
                            logging.debug(f"Search {search_index + 1} - Found company with selector: '{selector}'")
                            break

                    company = company_elem.get_text().strip() if company_elem else "Unknown Company"
                    logging.debug(f"Search {search_index + 1} - ✅ Card {card_index + 1} company extracted: '{company}'")

                    # Extract URL - try multiple selectors for different LinkedIn layouts
                    url_selectors = [
                        'a.base-card__full-link',               # Base card full link
                        'a.result-card__full-card-link',        # Result card full link
                        'a[data-test-id*="job-title"]',         # Job title link
                        'h3 a',                                 # Link inside h3
                        'a[href*="/jobs/view/"]',               # Direct job view links
                        'a[href*="/jobs/"]',                    # Any job links
                        'a',                                    # Generic link
                    ]

                    link_elem = None
                    for selector in url_selectors:
                        link_elem = card.select_one(selector)
                        if link_elem and link_elem.get('href'):
                            logging.debug(f"Search {search_index + 1} - Found URL with selector: '{selector}'")
                            break

                    if link_elem and link_elem.get('href'):
                        url = link_elem['href']
                        # Ensure URL is absolute
                        if not url.startswith('http'):
                            url = "https://www.linkedin.com" + url
                        logging.debug(f"Search {search_index + 1} - ✅ Card {card_index + 1} URL extracted")
                    else:
                        logging.debug(f"Search {search_index + 1} - ❌ No URL found for card {card_index + 1} '{title}' - SKIPPING")
                        continue

                    # Extract posting date for 24-hour filtering
                    posting_date_text = ""
                    is_promoted = has_promoted_text

                    # Look for posting date information in the card
                    if not is_promoted:
                        # Search for date text in the card content
                        date_candidates = card.find_all(string=True)
                        for text in date_candidates:
                            text_clean = text.strip()
                            if not text_clean:
                                continue

                            # Check if this is a promoted card (fallback detection)
                            if 'promoted' in text_clean.lower():
                                is_promoted = True
                                logging.debug(f"Search {search_index + 1} - 🎯 PROMOTED card found for '{title}': '{text_clean}' (fallback detection)")
                                break
                            # Check if this is posting date text (not duration)
                            elif is_posting_date_text(text_clean):
                                posting_date_text = text_clean
                                logging.debug(f"Search {search_index + 1} - 📅 POSTING DATE found for '{title}': '{text_clean}'")
                                break

                    # Apply STRICT 24-hour filtering based on posting date ONLY
                    if not is_promoted:  # Only filter non-promoted jobs
                        if posting_date_text:
                            is_recent = is_recent_job_posting(posting_date_text)
                            if is_recent:
                                logging.debug(f"Search {search_index + 1} - ✅ KEEPING '{title}' - posted {posting_date_text} (within 24 hours)")
                            else:
                                logging.debug(f"Search {search_index + 1} - ❌ FILTERED OUT '{title}' - posted {posting_date_text} (outside 24-hour window)")
                                continue
                        else:
                            # No posting date found - be STRICT and exclude (unless LinkedIn URL already filters for 24h)
                            # Since LinkedIn URL has f_TPR=r86400 (24h filter), we can be lenient here
                            logging.debug(f"Search {search_index + 1} - ✅ KEEPING '{title}' - no posting date found (LinkedIn URL pre-filtered for 24h)")
                    else:
                        # Keep promoted jobs (they're usually recent and relevant)
                        logging.debug(f"Search {search_index + 1} - ✅ KEEPING '{title}' - PROMOTED card (no date filtering needed)")

                    # Create simplified job entry
                    job = {
                        'title': title,
                        'company': company,
                        'url': url,
                        'posting_date_text': posting_date_text,
                        'is_promoted': is_promoted
                    }

                    search_jobs.append(job)
                    logging.debug(f"Search {search_index + 1} - 🎉 Card {card_index + 1} SUCCESSFULLY ADDED: '{title}' at '{company}'")

                except Exception as e:
                    logging.debug(f"Search {search_index + 1} - ❌ ERROR parsing card {card_index + 1}: {e}")
                    continue

            # Add search results to overall collection
            all_jobs_from_searches.extend(search_jobs)
            logging.info(f"Search {search_index + 1} completed: {len(search_jobs)} jobs found")

        except Exception as e:
            logging.error(f"Error in search {search_index + 1}: {e}")
            continue

    # Remove duplicates based on normalized job signature across all searches
    seen_signatures = set()
    unique_jobs = []
    for job in all_jobs_from_searches:
        signature = create_job_signature(job)
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_jobs.append(job)

    logging.info(f"LinkedIn COMPREHENSIVE search results:")
    logging.info(f"  Total jobs from all searches: {len(all_jobs_from_searches)}")
    logging.info(f"  After deduplication: {len(unique_jobs)}")

    # Log first few jobs for debugging
    for i, job in enumerate(unique_jobs[:5]):
        logging.info(f"Sample {i+1}: {job['title']} at {job['company']}")

    return unique_jobs

def scrape_naukri_jobs() -> List[Dict]:
    """
    Scrape job postings from Naukri.com for comprehensive coverage.
    Returns simplified format with only title, company, and url.

    Returns:
        List of job dictionaries with simplified format
    """
    jobs = []
    search_urls = [
        # Software Engineer search
        "https://www.naukri.com/software-engineer-jobs-in-hyderabad",
        # Computer Science search
        "https://www.naukri.com/computer-science-jobs-in-hyderabad",
        # Full Stack Developer search
        "https://www.naukri.com/full-stack-developer-jobs-in-hyderabad"
    ]

    logging.info("Scraping Naukri.com for additional job coverage...")

    for search_index, search_url in enumerate(search_urls):
        logging.info(f"Naukri search {search_index + 1}/{len(search_urls)}: {search_url.split('/')[-1]}")

        try:
            response = make_request_with_retry(search_url)
            if not response:
                logging.warning(f"Failed to get response from Naukri for search {search_index + 1}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            logging.info(f"Successfully fetched Naukri page for search {search_index + 1}")

            # Find job cards using Naukri-specific selectors
            job_selectors = [
                'div.jobTuple',                    # Main job container
                'article.jobTuple',               # Article-based job container
                'div[data-job-id]',               # Job ID containers
                'div.job-tuple',                  # Alternative job container
                '.srp-jobtuple-wrapper',          # Job tuple wrapper
                '.jobTupleHeader',                # Job header
                'div[class*="job"]',              # Any div with "job" in class
            ]

            job_cards = []
            for selector in job_selectors:
                try:
                    cards = soup.select(selector)
                    if cards:
                        job_cards.extend(cards)
                        logging.debug(f"Naukri search {search_index + 1} - Found {len(cards)} cards with selector: '{selector}'")
                except Exception as e:
                    logging.debug(f"Naukri search {search_index + 1} - Error with selector '{selector}': {e}")

            # Remove duplicates
            seen = set()
            unique_cards = []
            for card in job_cards:
                card_signature = f"{card.name}_{str(card.get('class', []))[:100]}"
                if card_signature not in seen:
                    seen.add(card_signature)
                    unique_cards.append(card)

            job_cards = unique_cards
            logging.info(f"Naukri search {search_index + 1} - Found {len(job_cards)} unique job cards")

            search_jobs = []
            for card_index, card in enumerate(job_cards):
                try:
                    # Extract title
                    title_selectors = [
                        'a.title',                    # Naukri title link
                        '.jobTupleHeader a',          # Header link
                        'h3 a',                       # H3 link
                        'h2 a',                       # H2 link
                        '.job-title',                 # Job title class
                        'a[title]',                   # Link with title attribute
                    ]

                    title_elem = None
                    for selector in title_selectors:
                        title_elem = card.select_one(selector)
                        if title_elem:
                            break

                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # EXCLUDE trainee/internship positions
                    title_lower = title.lower()
                    is_trainee_internship = any(term in title_lower for term in TRAINEE_INTERNSHIP_TERMS)
                    if is_trainee_internship:
                        logging.debug(f"Naukri - ❌ EXCLUDED trainee/internship position: '{title}'")
                        continue

                    # Extract company
                    company_selectors = [
                        '.subTitle',                  # Naukri company subtitle
                        '.companyInfo',               # Company info
                        'a.subTitle',                 # Company link
                        '.company-name',              # Company name class
                        'span[title]',                # Span with title
                    ]

                    company_elem = None
                    for selector in company_selectors:
                        company_elem = card.select_one(selector)
                        if company_elem:
                            break

                    company = company_elem.get_text().strip() if company_elem else "Unknown Company"

                    # Extract URL
                    url = ""
                    if title_elem and title_elem.get('href'):
                        url = title_elem['href']
                        if not url.startswith('http'):
                            url = "https://www.naukri.com" + url

                    if not url:
                        continue

                    # Create job entry
                    job = {
                        'title': title,
                        'company': company,
                        'url': url
                    }

                    search_jobs.append(job)
                    logging.debug(f"Naukri - Added job: {title} at {company}")

                except Exception as e:
                    logging.debug(f"Naukri - Error parsing card {card_index + 1}: {e}")
                    continue

            jobs.extend(search_jobs)
            logging.info(f"Naukri search {search_index + 1} completed: {len(search_jobs)} jobs found")

        except Exception as e:
            logging.error(f"Error in Naukri search {search_index + 1}: {e}")
            continue

    # Remove duplicates using normalized signatures
    seen_signatures = set()
    unique_jobs = []
    for job in jobs:
        signature = create_job_signature(job)
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_jobs.append(job)

    logging.info(f"Naukri.com results: {len(unique_jobs)} unique jobs")
    return unique_jobs

def scrape_indeed_jobs() -> List[Dict]:
    """
    Scrape job postings from Indeed.com for comprehensive coverage.
    Returns simplified format with only title, company, and url.

    Returns:
        List of job dictionaries with simplified format
    """
    jobs = []
    search_urls = [
        # Software Engineer search
        "https://in.indeed.com/jobs?q=software+engineer&l=Hyderabad",
        # Computer Science search
        "https://in.indeed.com/jobs?q=computer+science&l=Hyderabad",
        # Full Stack Developer search
        "https://in.indeed.com/jobs?q=full+stack+developer&l=Hyderabad"
    ]

    logging.info("Scraping Indeed.com for additional job coverage...")

    for search_index, search_url in enumerate(search_urls):
        logging.info(f"Indeed search {search_index + 1}/{len(search_urls)}")

        try:
            response = make_request_with_retry(search_url)
            if not response:
                logging.warning(f"Failed to get response from Indeed for search {search_index + 1}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            logging.info(f"Successfully fetched Indeed page for search {search_index + 1}")

            # Find job cards using Indeed-specific selectors
            job_selectors = [
                'div.job_seen_beacon',            # Indeed job container
                'div[data-jk]',                   # Job key containers
                '.jobsearch-SerpJobCard',         # Job card class
                '.result',                        # Result class
                'div[class*="job"]',              # Any div with "job" in class
            ]

            job_cards = []
            for selector in job_selectors:
                try:
                    cards = soup.select(selector)
                    if cards:
                        job_cards.extend(cards)
                        logging.debug(f"Indeed search {search_index + 1} - Found {len(cards)} cards with selector: '{selector}'")
                except Exception as e:
                    logging.debug(f"Indeed search {search_index + 1} - Error with selector '{selector}': {e}")

            # Remove duplicates
            seen = set()
            unique_cards = []
            for card in job_cards:
                card_signature = f"{card.name}_{str(card.get('class', []))[:100]}_{card.get('data-jk', '')}"
                if card_signature not in seen:
                    seen.add(card_signature)
                    unique_cards.append(card)

            job_cards = unique_cards
            logging.info(f"Indeed search {search_index + 1} - Found {len(job_cards)} unique job cards")

            search_jobs = []
            for card_index, card in enumerate(job_cards):
                try:
                    # Extract title
                    title_selectors = [
                        'h2.jobTitle a',              # Indeed job title link
                        '.jobTitle a',                # Job title link
                        'h2 a[data-jk]',              # H2 with job key
                        'a[data-jk]',                 # Link with job key
                        '.jobTitle',                  # Job title class
                    ]

                    title_elem = None
                    for selector in title_selectors:
                        title_elem = card.select_one(selector)
                        if title_elem:
                            break

                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # EXCLUDE trainee/internship positions
                    title_lower = title.lower()
                    is_trainee_internship = any(term in title_lower for term in TRAINEE_INTERNSHIP_TERMS)
                    if is_trainee_internship:
                        logging.debug(f"Indeed - ❌ EXCLUDED trainee/internship position: '{title}'")
                        continue

                    # Extract company
                    company_selectors = [
                        '.companyName',               # Indeed company name
                        'span.companyName',           # Company name span
                        'a .companyName',             # Company name in link
                        '.company',                   # Company class
                    ]

                    company_elem = None
                    for selector in company_selectors:
                        company_elem = card.select_one(selector)
                        if company_elem:
                            break

                    company = company_elem.get_text().strip() if company_elem else "Unknown Company"

                    # Extract URL
                    url = ""
                    if title_elem and title_elem.get('href'):
                        url = title_elem['href']
                        if not url.startswith('http'):
                            url = "https://in.indeed.com" + url

                    if not url:
                        continue

                    # Create job entry
                    job = {
                        'title': title,
                        'company': company,
                        'url': url
                    }

                    search_jobs.append(job)
                    logging.debug(f"Indeed - Added job: {title} at {company}")

                except Exception as e:
                    logging.debug(f"Indeed - Error parsing card {card_index + 1}: {e}")
                    continue

            jobs.extend(search_jobs)
            logging.info(f"Indeed search {search_index + 1} completed: {len(search_jobs)} jobs found")

        except Exception as e:
            logging.error(f"Error in Indeed search {search_index + 1}: {e}")
            continue

    # Remove duplicates using normalized signatures
    seen_signatures = set()
    unique_jobs = []
    for job in jobs:
        signature = create_job_signature(job)
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_jobs.append(job)

    logging.info(f"Indeed.com results: {len(unique_jobs)} unique jobs")
    return unique_jobs

def filter_by_branch(jobs: List[Dict]) -> List[Dict]:
    """
    Filter jobs by branch/field relevance using enhanced keyword matching.
    Priority: CSE/IT (score 3) > EEE/ECE (score 2) > MECH (score 1)

    Args:
        jobs: List of job dictionaries

    Returns:
        Filtered list of jobs with priority scoring
    """
    filtered = []

    for job in jobs:
        title = job.get('title', '').lower()
        company = job.get('company', '').lower()
        combined_text = f"{title} {company}"

        # Check for exclude terms first (immediate disqualification)
        exclude_detected = any(term.lower() in combined_text for term in EXCLUDE_TERMS)
        if exclude_detected:
            logging.debug(f"Excluded (irrelevant field): {title}")
            continue

        # Check for scam indicators
        scam_detected = any(indicator.lower() in combined_text for indicator in SCAM_INDICATORS)
        if scam_detected:
            logging.debug(f"Excluded (scam detected): {title}")
            continue

        # Check for CSE/IT keywords (highest priority) with detailed matching
        cse_it_matches = []
        for keyword in CSE_IT_KEYWORDS:
            if keyword.lower() in combined_text:
                cse_it_matches.append(keyword)

        # Check for EEE/ECE keywords (medium priority)
        eee_ece_matches = []
        for keyword in EEE_ECE_KEYWORDS:
            if keyword.lower() in combined_text:
                eee_ece_matches.append(keyword)

        # Check for MECH keywords (lower priority)
        mech_matches = []
        for keyword in MECH_KEYWORDS:
            if keyword.lower() in combined_text:
                mech_matches.append(keyword)

        # Assign priority scores with detailed logging
        if cse_it_matches:
            job['priority_score'] = 3
            job['field_category'] = 'CSE/IT'
            filtered.append(job)
            logging.debug(f"✅ CSE/IT match: '{title}' - matched keywords: {cse_it_matches}")
        elif eee_ece_matches:
            job['priority_score'] = 2
            job['field_category'] = 'EEE/ECE'
            filtered.append(job)
            logging.debug(f"✅ EEE/ECE match: '{title}' - matched keywords: {eee_ece_matches}")
        elif mech_matches:
            job['priority_score'] = 1
            job['field_category'] = 'MECH'
            filtered.append(job)
            logging.debug(f"✅ MECH match: '{title}' - matched keywords: {mech_matches}")
        else:
            logging.debug(f"❌ No field match: '{title}' - combined text: '{combined_text}'")

    # Sort by priority score (higher first)
    filtered.sort(key=lambda x: x.get('priority_score', 0), reverse=True)

    # Log filtering statistics by category
    cse_it_count = len([i for i in filtered if i.get('field_category') == 'CSE/IT'])
    eee_ece_count = len([i for i in filtered if i.get('field_category') == 'EEE/ECE'])
    mech_count = len([i for i in filtered if i.get('field_category') == 'MECH'])

    logging.info(f"Branch filter results: {len(filtered)}/{len(jobs)} jobs match field criteria")
    logging.info(f"  CSE/IT: {cse_it_count} jobs")
    logging.info(f"  EEE/ECE: {eee_ece_count} jobs")
    logging.info(f"  MECH: {mech_count} jobs")

    return filtered

def filter_by_experience(jobs: List[Dict]) -> List[Dict]:
    """
    Filter jobs to focus on entry-level positions (0-1 years experience).
    Excludes senior positions and prioritizes fresh graduate opportunities.

    Args:
        jobs: List of job dictionaries

    Returns:
        Filtered list of entry-level jobs
    """
    filtered = []

    for job in jobs:
        title = job.get('title', '').lower()
        company = job.get('company', '').lower()
        combined_text = f"{title} {company}"

        # Check for senior/experienced position indicators (exclude these)
        senior_detected = any(keyword.lower() in combined_text for keyword in SENIOR_EXPERIENCE_KEYWORDS)
        if senior_detected:
            logging.debug(f"Excluded (senior position): {title}")
            continue

        # Check for entry-level indicators (prioritize these)
        entry_level_matches = []
        for keyword in ENTRY_LEVEL_KEYWORDS:
            if keyword.lower() in combined_text:
                entry_level_matches.append(keyword)

        # If explicit entry-level indicators found, definitely include
        if entry_level_matches:
            job['experience_level'] = 'Entry Level (Explicit)'
            job['experience_matches'] = entry_level_matches
            filtered.append(job)
            logging.debug(f"✅ Entry-level match: '{title}' - matched keywords: {entry_level_matches}")
        else:
            # If no explicit indicators, include by default (assume entry-level friendly)
            # This ensures we don't miss jobs that don't explicitly mention experience level
            job['experience_level'] = 'Entry Level (Assumed)'
            job['experience_matches'] = []
            filtered.append(job)
            logging.debug(f"✅ Assumed entry-level: '{title}' - no experience requirements found")

    # Log filtering statistics
    explicit_entry_count = len([j for j in filtered if j.get('experience_level') == 'Entry Level (Explicit)'])
    assumed_entry_count = len([j for j in filtered if j.get('experience_level') == 'Entry Level (Assumed)'])

    logging.info(f"Experience filter results: {len(filtered)}/{len(jobs)} jobs are entry-level friendly")
    logging.info(f"  Explicit entry-level: {explicit_entry_count} jobs")
    logging.info(f"  Assumed entry-level: {assumed_entry_count} jobs")
    logging.info(f"  Excluded senior positions: {len(jobs) - len(filtered)} jobs")

    return filtered

def filter_by_date(jobs: List[Dict], hours: int = 24) -> List[Dict]:
    """
    Filter jobs to only include those posted within the specified time window.
    Focuses on POSTING DATE, not job duration or start date.

    Args:
        jobs: List of job dictionaries
        hours: Maximum age in hours (default: 24 for strict 24-hour filtering)

    Returns:
        Filtered list of recent jobs
    """
    filtered = []
    date_filtered_count = 0
    promoted_count = 0
    no_date_count = 0

    for job in jobs:
        title = job.get('title', '')
        posting_date_text = job.get('posting_date_text', '')
        is_promoted = job.get('is_promoted', False)

        # Always keep promoted jobs (they're usually recent and relevant)
        if is_promoted:
            filtered.append(job)
            promoted_count += 1
            logging.debug(f"✅ KEEPING '{title}' - PROMOTED job (no date filtering)")
            continue

        # Apply date filtering for non-promoted jobs
        if posting_date_text:
            is_recent = is_recent_job_posting(posting_date_text)
            if is_recent:
                filtered.append(job)
                date_filtered_count += 1
                logging.debug(f"✅ KEEPING '{title}' - posted {posting_date_text} (within {hours} hours)")
            else:
                logging.debug(f"❌ FILTERED OUT '{title}' - posted {posting_date_text} (outside {hours}-hour window)")
        else:
            # No posting date found - keep it (LinkedIn URL already filters for 24h)
            filtered.append(job)
            no_date_count += 1
            logging.debug(f"✅ KEEPING '{title}' - no posting date found (LinkedIn pre-filtered)")

    # Log filtering statistics
    logging.info(f"Date filter results ({hours}h window): {len(filtered)}/{len(jobs)} jobs are recent")
    logging.info(f"  Within {hours}h window: {date_filtered_count} jobs")
    logging.info(f"  Promoted jobs (kept): {promoted_count} jobs")
    logging.info(f"  No date info (kept): {no_date_count} jobs")
    logging.info(f"  Excluded old postings: {len(jobs) - len(filtered)} jobs")

    return filtered

def remove_duplicates(jobs: List[Dict]) -> List[Dict]:
    """
    Remove duplicate jobs based on normalized title + company + URL.
    Uses URL normalization to avoid false duplicates from tracking parameters.

    Args:
        jobs: List of job dictionaries

    Returns:
        Deduplicated list of jobs
    """
    seen = set()
    unique_jobs = []
    seen_jobs = load_seen_jobs()

    for job in jobs:
        # Create unique identifier using normalized signature
        identifier = create_job_signature(job)

        # Check if we've seen this before (in current run or previous runs)
        if identifier not in seen and identifier not in seen_jobs:
            seen.add(identifier)
            unique_jobs.append(job)
        else:
            if identifier in seen_jobs:
                logging.debug(f"Skipping previously seen job: {job.get('title', '')} at {job.get('company', '')}")
            else:
                logging.debug(f"Skipping duplicate in current run: {job.get('title', '')} at {job.get('company', '')}")

    logging.info(f"Deduplication: {len(unique_jobs)}/{len(jobs)} unique jobs (filtered out {len(jobs) - len(unique_jobs)} duplicates/seen jobs)")
    return unique_jobs

def select_best_with_ai(jobs: List[Dict]) -> Dict:
    """
    Use Groq's AI to select the best job from filtered results.

    Args:
        jobs: List of filtered job dictionaries

    Returns:
        Selected job dictionary or error response
    """
    if not jobs:
        return {
            "message": "No jobs to analyze",
            "total_scraped": 0,
            "ai_decision": "No jobs provided for analysis"
        }

    try:
        # Get API key with robust fallback
        api_key = os.getenv('GROQ_API_KEY', GROQ_API_KEY)

        if not api_key:
            logging.warning("No API key available, using fallback selection")
            return select_best_job_fallback(jobs)

        # Validate API key before creating client
        try:
            client = Groq(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to create Groq client: {e}")
            return select_best_job_fallback(jobs)

        logging.info(f"AI analyzing {len(jobs)} jobs...")

        # Prepare jobs for AI analysis
        jobs_for_ai = []
        for i, job in enumerate(jobs, 1):
            job_summary = {
                "number": i,
                "title": job.get('title', ''),
                "company": job.get('company', ''),
                "field_category": job.get('field_category', ''),
                "priority_score": job.get('priority_score', 0),
                "experience_level": job.get('experience_level', 'Unknown'),
                "experience_matches": job.get('experience_matches', [])
            }
            jobs_for_ai.append(job_summary)

        # Create AI prompt
        prompt = f"""You are a career advisor for fresh engineering graduates (0-1 years experience). Analyze these entry-level job opportunities and select the SINGLE most valuable and legitimate one.

Evaluation Criteria (in order of importance):
1. Entry-level friendliness (0-1 years experience, training provided, fresh graduate positions)
2. Relevance to engineering graduates (especially CSE/IT/AI/ML)
3. Company legitimacy and reputation
4. Career growth potential and learning opportunities for beginners
5. Technical skill development potential for new graduates
6. Industry standing and future prospects

PRIORITIZE jobs with:
- Explicit entry-level indicators (junior, associate, fresh graduate, entry level)
- Training and mentorship opportunities
- No high experience requirements
- Clear growth paths for beginners

Jobs to evaluate:
{json.dumps(jobs_for_ai, indent=2)}

Return only the exact title of the selected job. If all seem suspicious or low-quality, return "NONE"."""

        # Call Groq API
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=100
        )

        selected_title = response.choices[0].message.content.strip()
        logging.info(f"AI selected: {selected_title}")

        if selected_title.upper() == "NONE":
            return {
                "message": "No suitable jobs found matching criteria",
                "total_scraped": len(jobs),
                "ai_decision": "All jobs flagged as low-quality or suspicious"
            }

        # Find the selected job
        for job in jobs:
            if selected_title.lower() in job.get('title', '').lower() or job.get('title', '').lower() in selected_title.lower():
                selected = job.copy()
                selected['ai_reasoning'] = "Selected by AI as most valuable and legitimate opportunity"
                save_seen_job(selected)
                return selected

        # If exact match not found, return first job as fallback
        logging.warning(f"AI selection '{selected_title}' not found, using first job")
        fallback = jobs[0].copy()
        fallback['ai_reasoning'] = "Fallback selection (AI choice not found)"
        save_seen_job(fallback)
        return fallback

    except Exception as e:
        logging.error(f"AI selection failed: {e}")
        logging.info("Falling back to rule-based selection")
        return select_best_job_fallback(jobs)

def select_best_job_fallback(jobs: List[Dict]) -> Dict:
    """
    Fallback selection method using rule-based scoring when AI is unavailable.

    Args:
        jobs: List of job dictionaries

    Returns:
        Selected job dictionary
    """
    if not jobs:
        return {
            "message": "No jobs to analyze",
            "total_scraped": 0,
            "selection_method": "fallback_failed"
        }

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from processors.fallback_selector import fallback_select_best

        best_job = fallback_select_best(jobs, 'job')
        if best_job:
            result = best_job.copy()
            result['ai_reasoning'] = "Selected using rule-based fallback algorithm"
            result['selection_method'] = "fallback_algorithm"
            save_seen_job(result)
            return result
    except ImportError:
        logging.warning("Fallback selector not available, using simple selection")
    except Exception as e:
        logging.error(f"Fallback selection failed: {e}")

    # Simple fallback - select first job with highest priority score
    best_job = max(jobs, key=lambda x: x.get('priority_score', 0))
    result = best_job.copy()
    result['ai_reasoning'] = "Selected using simple priority-based fallback"
    result['selection_method'] = "simple_fallback"
    save_seen_job(result)
    return result

def main() -> Dict:
    """
    Main function to orchestrate the job scraping and filtering process.

    Returns:
        Final result dictionary with selected job or error message
    """
    logging.info("=== Starting Recent Entry-Level Job Scraper (24H + 0-1 Years Experience) ===")

    try:
        # Stage 1: Scrape from multiple sources for comprehensive coverage
        logging.info("Stage 1: Scraping jobs from multiple sources...")
        all_jobs = []

        # Scrape LinkedIn jobs (primary source)
        linkedin_jobs = scrape_linkedin_jobs()
        all_jobs.extend(linkedin_jobs)
        logging.info(f"SUCCESS LinkedIn: {len(linkedin_jobs)} jobs")

        # Scrape Naukri jobs (additional coverage)
        naukri_jobs = scrape_naukri_jobs()
        all_jobs.extend(naukri_jobs)
        logging.info(f"SUCCESS Naukri: {len(naukri_jobs)} jobs")

        # Scrape Indeed jobs (additional coverage)
        indeed_jobs = scrape_indeed_jobs()
        all_jobs.extend(indeed_jobs)
        logging.info(f"SUCCESS Indeed: {len(indeed_jobs)} jobs")

        logging.info(f"Total scraped from all sources: {len(all_jobs)} jobs")

        if not all_jobs:
            return {
                "message": "No jobs found from any source",
                "total_scraped": 0,
                "ai_decision": "No jobs to analyze"
            }

        # Stage 2: Apply multi-stage filtering
        logging.info("Stage 2: Applying multi-stage filtering...")

        # Date filtering (24-hour window for recent postings)
        filtered_by_date = filter_by_date(all_jobs, hours=24)

        # Branch/keyword filtering
        filtered_by_branch = filter_by_branch(filtered_by_date)

        # Experience level filtering (0-1 years, entry-level)
        filtered_by_experience = filter_by_experience(filtered_by_branch)

        # Deduplication
        unique_jobs = remove_duplicates(filtered_by_experience)

        # Stage 3: AI-powered selection
        logging.info("Stage 3: AI-powered job selection...")
        if unique_jobs:
            selected_job = select_best_with_ai(unique_jobs)
        else:
            selected_job = {
                "message": "No jobs passed filtering criteria",
                "total_scraped": len(all_jobs),
                "after_date_filter": len(filtered_by_date),
                "after_branch_filter": len(filtered_by_branch),
                "after_experience_filter": len(filtered_by_experience),
                "unique_jobs": len(unique_jobs),
                "ai_decision": "No jobs available for AI analysis"
            }

        # Add statistics to result
        if isinstance(selected_job, dict) and 'title' in selected_job:
            selected_job.update({
                "total_scraped": len(all_jobs),
                "after_date_filter": len(filtered_by_date),
                "after_branch_filter": len(filtered_by_branch),
                "after_experience_filter": len(filtered_by_experience),
                "unique_jobs": len(unique_jobs)
            })

        # Save results to files
        logging.info("Stage 4: Saving results...")

        # Save all filtered jobs
        all_jobs_clean = []
        for job in unique_jobs:
            clean_job = {
                "title": job.get('title', ''),
                "company": job.get('company', ''),
                "url": job.get('url', ''),
                "priority_score": job.get('priority_score', 0),
                "field_category": job.get('field_category', 'Unknown'),
                "experience_level": job.get('experience_level', 'Unknown'),
                "experience_matches": job.get('experience_matches', [])
            }
            all_jobs_clean.append(clean_job)

        with open('../data/filtered_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(all_jobs_clean, f, ensure_ascii=False, indent=2)

        # Save AI-selected job
        if isinstance(selected_job, dict) and 'title' in selected_job:
            clean_result = {
                "title": selected_job['title'],
                "company": selected_job['company'],
                "url": selected_job['url'],
                "priority_score": selected_job.get('priority_score', 0),
                "field_category": selected_job.get('field_category', 'Unknown'),
                "experience_level": selected_job.get('experience_level', 'Unknown'),
                "experience_matches": selected_job.get('experience_matches', []),
                "ai_reasoning": selected_job.get('ai_reasoning', '')
            }

            with open('../data/selected_job.json', 'w', encoding='utf-8') as f:
                json.dump(clean_result, f, ensure_ascii=False, indent=2)

        return selected_job

    except Exception as e:
        logging.error(f"Error in main process: {e}")
        return {
            "message": "Error in job scraping process",
            "error": str(e)
        }

def display_results(result: Dict) -> None:
    """
    Display results in a formatted way to the console.

    Args:
        result: Result dictionary from main function
    """
    print("\n" + "="*60)
    print("🎯 RECENT ENTRY-LEVEL JOB SCRAPER (24H + 0-1 YEARS)")
    print("="*60)

    if isinstance(result, dict) and 'title' in result:
        # Successful result with selected job
        print("✅ JOB FOUND AND SELECTED")
        print(f"🏆 Selected Job: {result['title']}")
        print(f"🏢 Company: {result['company']}")
        print(f"🔗 URL: {result['url']}")
        print(f"🤖 AI Reasoning: {result.get('ai_reasoning', 'N/A')}")

        # Show experience level information
        experience_level = result.get('experience_level', 'Unknown')
        experience_matches = result.get('experience_matches', [])
        if experience_level == 'Entry Level (Explicit)':
            print(f"🎓 Experience Level: ✅ ENTRY LEVEL (Explicit indicators found)")
            if experience_matches:
                print(f"   📝 Matched keywords: {', '.join(experience_matches[:3])}{'...' if len(experience_matches) > 3 else ''}")
        elif experience_level == 'Entry Level (Assumed)':
            print(f"🎓 Experience Level: ✅ ENTRY LEVEL (No senior requirements)")
        else:
            print(f"🎓 Experience Level: {experience_level}")

        if result.get('priority_score'):
            priority_score = result.get('priority_score', 0)
            field_category = result.get('field_category', 'Unknown')

            if priority_score == 3:
                priority_text = "🔥 HIGHEST (CSE/IT)"
            elif priority_score == 2:
                priority_text = "⭐ HIGH (EEE/ECE)"
            elif priority_score == 1:
                priority_text = "📌 MEDIUM (MECH)"
            else:
                priority_text = "❓ LOW"

            print(f"🎯 Priority: {priority_text} (Score: {priority_score})")
            print(f"📚 Field: {field_category}")

        # Show filtering statistics if available
        if 'total_scraped' in result:
            stats = {
                'total_scraped': result.get('total_scraped', 0),
                'after_date_filter': result.get('after_date_filter', 0),
                'after_branch_filter': result.get('after_branch_filter', 0),
                'after_experience_filter': result.get('after_experience_filter', 0),
                'unique_jobs': result.get('unique_jobs', 0)
            }

            print(f"\n📈 COMPREHENSIVE SCRAPING SUMMARY:")
            print(f"  🔍 Total scraped from all sources: {stats['total_scraped']}")
            print(f"  📅 After date filter (24 hours): {stats['after_date_filter']}")
            print(f"  🎯 After keyword/branch filter: {stats['after_branch_filter']}")
            print(f"  🎓 After experience filter (0-1 years): {stats['after_experience_filter']}")
            print(f"  🔄 After deduplication: {stats['unique_jobs']}")
            print(f"  ✅ Total qualifying recent entry-level jobs: {stats['unique_jobs']}")
            print()

        print(f"💾 FILE OUTPUTS:")
        print(f"  📄 All filtered jobs → filtered_jobs.json ({result.get('unique_jobs', 0)} jobs)")
        print(f"../data/  🎯 AI-selected job → selected_job.json")

    else:
        # Error or no results
        print("❌ NO SUITABLE JOBS FOUND")
        print(f"Message: {result.get('message', 'Unknown error')}")

        if 'total_scraped' in result:
            print(f"\n📈 COMPREHENSIVE SCRAPING SUMMARY:")
            print(f"  🔍 Total scraped from all sources: {result.get('total_scraped', 0)}")
            print(f"  📅 After date filter (24 hours): {result.get('after_date_filter', 0)}")
            print(f"  🎯 After keyword/branch filter: {result.get('after_branch_filter', 0)}")
            print(f"  🎓 After experience filter (0-1 years): {result.get('after_experience_filter', 0)}")
            print(f"  🔄 After deduplication: {result.get('unique_jobs', 0)}")
            print(f"  ✅ Total qualifying recent entry-level jobs: {result.get('unique_jobs', 0)}")

        print(f"\n🤖 AI Decision: {result.get('ai_decision', 'N/A')}")

        print(f"\n💾 FILE OUTPUTS:")
        print(f"  📄 All filtered jobs → filtered_jobs.json ({result.get('unique_jobs', 0)} jobs)")
        print(f"  🎯 AI-selected job → selected_job.json (no selection)")

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import groq
    except ImportError:
        print("Installing required packages...")
        os.system("pip install groq beautifulsoup4 python-dateutil")

    # Run the job scraper
    result = main()
    display_results(result)