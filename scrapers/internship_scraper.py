#!/usr/bin/env python3
"""
Intelligent Internship Scraper for Engineering Students in Hyderabad

This script scrapes internship postings from multiple sources, applies multi-stage filtering,
and uses Groq's AI to select the single most relevant, legitimate internship opportunity.

Author: AI Assistant
Date: 2025-05-25
"""

import requests
from bs4 import BeautifulSoup
import json
import datetime
import logging
import time
import random
import re
import os
from typing import List, Dict, Set, Optional
from dateutil import parser as date_parser
from groq import Groq

# Import centralized configuration
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.config import get_groq_api_key, REQUEST_TIMEOUT, MAX_RETRIES
    GROQ_API_KEY = get_groq_api_key()
    REQUEST_TIMEOUT = REQUEST_TIMEOUT
    MAX_RETRIES = MAX_RETRIES
except ImportError:
    # Fallback configuration if config.py is not available
    GROQ_API_KEY = "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"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3

# Configuration Constants
SEEN_INTERNSHIPS_FILE = "../data/seen_internships.json"
DELAY_RANGE = (1, 3)  # seconds

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
    "fresher cloud engineer", "cloud", "aws", "azure", "gcp",

    # Cybersecurity & Systems - High priority
    "cybersecurity", "security analyst", "penetration tester", "network security",
    "information security", "cyber security", "ethical hacker", "security engineer",

    # UI/UX & Design - Medium priority
    "ui developer", "ui development", "ux designer", "ux development", "ui/ux designer",
    "ui/ux development", "frontend designer", "web designer", "graphic designer",
    "product designer", "interaction designer",

    # General Development Terms
    "developer", "development", "programmer", "programming", "coding", "engineer", "engineering",

    # Intern/Fresher specific terms
    "intern", "internship", "fresher", "trainee", "graduate trainee", "entry level",
    "software engineer intern", "software developer intern", "cloud engineer intern",
    "fresher software engineer", "fresher developer", "fresher programmer",
    "junior developer", "junior engineer", "associate developer", "associate engineer"
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

# Configure logging with UTF-8 encoding - Enable DEBUG for better troubleshooting
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG to see date extraction details
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/internship_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_user_agent() -> str:
    """Return a realistic User-Agent string."""
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def make_request_with_retry(url: str, max_retries: int = MAX_RETRIES) -> Optional[requests.Response]:
    """
    Make HTTP request with retry logic and proper error handling.

    Args:
        url: URL to request
        max_retries: Maximum number of retry attempts

    Returns:
        Response object or None if all attempts failed
    """
    headers = {'User-Agent': get_user_agent()}

    for attempt in range(max_retries):
        try:
            # Add random delay to avoid rate limiting
            if attempt > 0:
                delay = random.uniform(*DELAY_RANGE)
                time.sleep(delay)

            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout for {url} (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.ConnectionError:
            logging.warning(f"Connection error for {url} (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.HTTPError as e:
            logging.warning(f"HTTP error {e.response.status_code} for {url} (attempt {attempt + 1}/{max_retries})")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request error for {url}: {e} (attempt {attempt + 1}/{max_retries})")

    logging.error(f"Failed to fetch {url} after {max_retries} attempts")
    return None

def parse_posting_date(date_text: str) -> Optional[datetime.datetime]:
    """
    Parse various date formats into datetime object.

    Args:
        date_text: Date string in various formats

    Returns:
        Parsed datetime or None if parsing failed
    """
    if not date_text:
        return None

    date_text = date_text.strip().lower()
    now = datetime.datetime.now()

    try:
        # Handle "X days ago" format
        days_ago_match = re.search(r'(\d+)\s+days?\s+ago', date_text)
        if days_ago_match:
            days = int(days_ago_match.group(1))
            return now - datetime.timedelta(days=days)

        # Handle "X hours ago" format
        hours_ago_match = re.search(r'(\d+)\s+hours?\s+ago', date_text)
        if hours_ago_match:
            hours = int(hours_ago_match.group(1))
            return now - datetime.timedelta(hours=hours)

        # Handle "today" and "yesterday"
        if 'today' in date_text:
            return now
        elif 'yesterday' in date_text:
            return now - datetime.timedelta(days=1)

        # Try to parse standard date formats
        return date_parser.parse(date_text)

    except (ValueError, TypeError) as e:
        logging.debug(f"Failed to parse date '{date_text}': {e}")
        return None

def load_seen_internships() -> Set[str]:
    """
    Load previously seen internship IDs from file.

    Returns:
        Set of internship IDs that have been processed before
    """
    try:
        if os.path.exists(SEEN_INTERNSHIPS_FILE):
            with open(SEEN_INTERNSHIPS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('seen_ids', []))
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Failed to load seen internships: {e}")

    return set()

def save_seen_internship(internship: Dict) -> None:
    """
    Save internship ID to seen internships file.

    Args:
        internship: Internship dictionary containing title, company, and url
    """
    try:
        seen_ids = load_seen_internships()

        # Create unique ID from title + company + url
        internship_id = f"{internship.get('title', '')}-{internship.get('company', '')}-{internship.get('url', '')}"
        seen_ids.add(internship_id)

        # Save back to file
        with open(SEEN_INTERNSHIPS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'seen_ids': list(seen_ids)}, f, indent=2)

    except IOError as e:
        logging.error(f"Failed to save seen internship: {e}")

def parse_internshala_posting_date(date_text: str) -> datetime.datetime:
    """
    Parse Internshala posting date text into datetime object.

    Args:
        date_text: Text like "3 days ago", "Few hours ago", "1 week ago"

    Returns:
        datetime object representing the posting date
    """
    if not date_text:
        return None

    date_text = date_text.lower().strip()
    now = datetime.datetime.now()

    try:
        if 'hour' in date_text:
            if 'few' in date_text:
                hours = 2  # Assume "few hours" means 2 hours
            else:
                # Extract number from text like "5 hours ago"
                match = re.search(r'(\d+)', date_text)
                hours = int(match.group(1)) if match else 1
            return now - datetime.timedelta(hours=hours)

        elif 'day' in date_text:
            if 'few' in date_text:
                days = 2  # Assume "few days" means 2 days
            else:
                # Extract number from text like "3 days ago"
                match = re.search(r'(\d+)', date_text)
                days = int(match.group(1)) if match else 1
            return now - datetime.timedelta(days=days)

        elif 'week' in date_text:
            # Extract number from text like "1 week ago"
            match = re.search(r'(\d+)', date_text)
            weeks = int(match.group(1)) if match else 1
            return now - datetime.timedelta(weeks=weeks)

        elif 'month' in date_text:
            # Extract number from text like "1 month ago"
            match = re.search(r'(\d+)', date_text)
            months = int(match.group(1)) if match else 1
            return now - datetime.timedelta(days=months * 30)  # Approximate

        else:
            # If we can't parse it, assume it's recent
            return now

    except Exception as e:
        logging.debug(f"Error parsing date '{date_text}': {e}")
        return now  # Default to current time if parsing fails

def is_within_48_hours(posting_date: datetime.datetime) -> bool:
    """
    Check if posting date is within the last 48 hours.

    Args:
        posting_date: datetime object of when internship was posted

    Returns:
        True if within 48 hours, False otherwise
    """
    if not posting_date:
        return False

    cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=48)
    return posting_date >= cutoff_time

def is_posting_date_text(text: str) -> bool:
    """
    Check if text contains posting date information (not internship duration).

    Args:
        text: Text to analyze

    Returns:
        True if text contains posting date indicators, False otherwise
    """
    if not text:
        return False

    text = text.lower().strip()

    # Posting date indicators - these suggest when the internship was posted
    posting_indicators = [
        'posted', 'ago', 'updated', 'published', 'listed', 'added',
        'hours ago', 'days ago', 'weeks ago', 'months ago',
        'yesterday', 'today', 'recently posted'
    ]

    # Duration indicators - these refer to internship length, NOT posting date
    duration_indicators = [
        'duration', 'months internship', 'weeks internship', 'month internship',
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

def is_recent_posting(date_text: str) -> bool:
    """
    Check if a posting is recent (within 48 hours) based on POSTING DATE text only.
    Strict 48-hour filtering for very recent internships.

    Args:
        date_text: Text like "posted 2 hours ago", "1 day ago", etc.

    Returns:
        True if within 48 hours, False otherwise
    """
    if not date_text:
        return False

    date_text = date_text.lower().strip()

    # Parse hours - within 48 hours
    if 'hour' in date_text and 'ago' in date_text:
        match = re.search(r'(\d+)\s*hour', date_text)
        if match:
            hours = int(match.group(1))
            return hours <= 48
        elif 'few' in date_text:
            return True  # "few hours ago" is definitely recent

    # Parse days - within 2 days (48 hours)
    elif 'day' in date_text and 'ago' in date_text:
        match = re.search(r'(\d+)\s*day', date_text)
        if match:
            days = int(match.group(1))
            return days <= 2  # 2 days = 48 hours
        elif 'yesterday' in date_text:
            return True
        elif 'today' in date_text:
            return True

    # Special cases for very recent postings
    elif any(word in date_text for word in ['today', 'yesterday', 'recently posted']):
        return True

    # Anything with weeks, months is definitely old
    elif any(term in date_text for term in ['week', 'month', 'year']) and 'ago' in date_text:
        return False

    # If we can't parse it clearly, be strict and exclude it
    return False

def scrape_internshala() -> List[Dict]:
    """
    Scrape internship postings from Internshala with STRICT 48-hour date filtering.
    Only looks for posting dates, ignores internship duration.
    Returns simplified format with only title, company, and url for very recent internships.

    Returns:
        List of internship dictionaries with simplified format (filtered by 48-hour window)
    """
    internships = []
    base_url = "https://internshala.com"
    search_url = "https://internshala.com/internships/computer-science-internship-in-hyderabad/"

    logging.info("Scraping Internshala with STRICT 48-hour posting date filtering...")

    try:
        response = make_request_with_retry(search_url)
        if not response:
            logging.warning("Failed to get response from Internshala")
            return internships

        soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully fetched Internshala page")

        # Find internship containers - look for h3 elements with internship links
        internship_headings = soup.find_all('h3')
        logging.info(f"Found {len(internship_headings)} h3 headings to analyze")

        total_found = 0
        date_filtered_count = 0

        for heading in internship_headings:
            try:
                # Look for links within headings
                link_elem = heading.find('a')
                if not link_elem or not link_elem.get('href') or '/internship/detail/' not in link_elem.get('href'):
                    continue

                total_found += 1

                # Extract title
                title = link_elem.get_text().strip()
                if not title:
                    continue

                # Extract URL
                href = link_elem.get('href')
                if href.startswith('/'):
                    url = base_url + href
                else:
                    url = href

                # Extract posting date - ONLY look for posting date text, NOT duration
                posting_date_text = ""
                duration_text = ""

                # Look for date information in the parent container and siblings
                container = heading.parent
                all_text_candidates = []

                # Collect all text from multiple sources
                for _ in range(5):  # Check up to 5 parent levels
                    if container:
                        # Get all text from this container
                        date_candidates = container.find_all(string=True)
                        all_text_candidates.extend(date_candidates)
                        container = container.parent
                    else:
                        break

                # Also check siblings of the heading
                if heading.parent:
                    for sibling in heading.parent.find_all():
                        sibling_text = sibling.find_all(string=True)
                        all_text_candidates.extend(sibling_text)

                # Process all text candidates to find POSTING DATE (not duration)
                for text in all_text_candidates:
                    text_clean = text.strip()
                    if not text_clean:
                        continue

                    # Check if this is posting date text (not duration)
                    if is_posting_date_text(text_clean):
                        posting_date_text = text_clean
                        logging.debug(f"✅ POSTING DATE found for '{title}': '{text_clean}'")
                        break
                    elif any(duration_word in text_clean.lower() for duration_word in ['months', 'weeks', 'duration', 'full time', 'part time']):
                        duration_text = text_clean
                        logging.debug(f"⏱️ DURATION (ignored) for '{title}': '{text_clean}'")

                # Apply STRICT 48-hour filtering based on posting date ONLY
                if posting_date_text:
                    is_recent = is_recent_posting(posting_date_text)
                    if is_recent:
                        logging.debug(f"✅ KEEPING '{title}' - posted {posting_date_text} (within 48 hours)")
                    else:
                        logging.debug(f"❌ FILTERED OUT '{title}' - posted {posting_date_text} (outside 48-hour window)")
                        continue
                else:
                    # No posting date found - be STRICT and exclude
                    logging.debug(f"❌ FILTERED OUT '{title}' - no posting date found (duration found: {duration_text or 'none'})")
                    continue

                date_filtered_count += 1

                # Extract company - look for company name near the link
                company = "Unknown Company"

                # Try to find company in parent elements
                parent = heading.parent
                for _ in range(3):  # Check up to 3 parent levels
                    if parent:
                        # Look for company name patterns
                        company_candidates = parent.find_all(string=True)
                        for text in company_candidates:
                            text = text.strip()
                            # Skip empty text, titles, and common words
                            if (text and text != title and
                                len(text) > 2 and len(text) < 50 and
                                not text.lower().startswith(('hyderabad', 'months', '₹', 'actively', 'few', 'days', 'weeks', 'ago'))):
                                company = text
                                break
                        if company != "Unknown Company":
                            break
                        parent = parent.parent
                    else:
                        break

                # Create simplified internship entry
                internship = {
                    'title': title,
                    'company': company,
                    'url': url
                }

                internships.append(internship)
                logging.debug(f"Added recent internship: {title} at {company} (posted {posting_date_text})")

            except Exception as e:
                logging.debug(f"Error processing internship heading: {e}")
                continue

        # Remove duplicates based on URL
        seen_urls = set()
        unique_internships = []
        for internship in internships:
            if internship['url'] not in seen_urls:
                seen_urls.add(internship['url'])
                unique_internships.append(internship)

        logging.info(f"Internshala 48-hour STRICT filter results:")
        logging.info(f"  Total internships found: {total_found}")
        logging.info(f"  After 48-hour filter: {len(unique_internships)}")
        logging.info(f"  Filtered out: {total_found - len(unique_internships)} internships (older than 48 hours or no posting date)")

        # Log first few internships for debugging
        for i, internship in enumerate(unique_internships[:3]):
            logging.info(f"Sample {i+1}: {internship['title']} at {internship['company']}")

    except Exception as e:
        logging.error(f"Error scraping Internshala: {e}")

    return unique_internships

def parse_linkedin_posting_date(date_text: str) -> datetime.datetime:
    """
    Parse LinkedIn posting date text into datetime object.

    Args:
        date_text: Text like "8 hours ago", "2 days ago", "1 week ago"

    Returns:
        datetime object representing the posting date
    """
    if not date_text:
        return None

    date_text = date_text.lower().strip()
    now = datetime.datetime.now()

    try:
        if 'hour' in date_text:
            # Extract number from text like "8 hours ago"
            match = re.search(r'(\d+)', date_text)
            hours = int(match.group(1)) if match else 1
            return now - datetime.timedelta(hours=hours)

        elif 'day' in date_text:
            # Extract number from text like "2 days ago"
            match = re.search(r'(\d+)', date_text)
            days = int(match.group(1)) if match else 1
            return now - datetime.timedelta(days=days)

        elif 'week' in date_text:
            # Extract number from text like "1 week ago"
            match = re.search(r'(\d+)', date_text)
            weeks = int(match.group(1)) if match else 1
            return now - datetime.timedelta(weeks=weeks)

        elif 'month' in date_text:
            # Extract number from text like "1 month ago"
            match = re.search(r'(\d+)', date_text)
            months = int(match.group(1)) if match else 1
            return now - datetime.timedelta(days=months * 30)  # Approximate

        else:
            # If we can't parse it, assume it's recent
            return now

    except Exception as e:
        logging.debug(f"Error parsing LinkedIn date '{date_text}': {e}")
        return now  # Default to current time if parsing fails

def scrape_linkedin() -> List[Dict]:
    """
    Scrape internship postings from LinkedIn Jobs with LENIENT date filtering.
    LinkedIn URL already filters for last 24 hours (f_TPR=r86400), so we skip additional date filtering.
    Returns simplified format with only title, company, and url for recent internships.

    Returns:
        List of internship dictionaries with simplified format (pre-filtered by LinkedIn's 24h filter)
    """
    internships = []
    search_url = "https://www.linkedin.com/jobs/search/?currentJobId=4234163468&distance=25&f_E=1&f_TPR=r86400&geoId=105556991&keywords=computer%20science&origin=JOB_SEARCH_PAGE_JOB_FILTER"

    logging.info("Scraping LinkedIn with LENIENT filtering (URL pre-filtered for 24h)...")

    try:
        response = make_request_with_retry(search_url)
        if not response:
            logging.warning("Failed to get response from LinkedIn")
            return internships

        soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully fetched LinkedIn page")

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
                    logging.debug(f"Found {len(cards)} cards with selector: '{selector}'")
            except Exception as e:
                logging.debug(f"Error with selector '{selector}': {e}")

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
        logging.info(f"Found {len(job_cards)} total unique job cards to analyze")

        # Debug: Log some sample card structures
        if job_cards:
            for i, card in enumerate(job_cards[:3]):  # Log first 3 cards for debugging
                logging.debug(f"Sample card {i+1} structure: tag={card.name}, classes={card.get('class', [])}, data-attrs={[k for k in card.attrs.keys() if k.startswith('data-')]}")
        else:
            logging.warning("No job cards found with any selector - page structure may have changed")

        total_found = 0
        date_filtered_count = 0

        for card_index, card in enumerate(job_cards):
            try:
                logging.debug(f"Processing card {card_index + 1}/{len(job_cards)}")

                # First, check if this card contains "promoted" anywhere
                card_html = str(card)
                has_promoted_text = 'promoted' in card_html.lower()
                logging.debug(f"Card {card_index + 1} contains 'promoted': {has_promoted_text}")

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
                        logging.debug(f"Found title with selector: '{selector}'")
                        break

                if not title_elem:
                    logging.debug(f"❌ No title found for card {card_index + 1} with classes: {card.get('class', [])} - SKIPPING")
                    # Log the card structure for debugging
                    logging.debug(f"Card {card_index + 1} HTML snippet: {str(card)[:200]}...")
                    continue

                title = title_elem.get_text().strip()
                if not title:
                    logging.debug(f"❌ Empty title found for card {card_index + 1} - SKIPPING")
                    continue

                total_found += 1
                logging.debug(f"✅ Card {card_index + 1} title extracted: '{title}'")

                # Extract posting date for debugging - but don't use for filtering
                # LinkedIn URL already filters for last 24 hours (f_TPR=r86400)
                posting_date_text = ""
                is_promoted = False

                # Look for date information or promoted status in the card (for debugging only)
                # Check for promoted cards using specific HTML structure
                promoted_spans = card.find_all('span', {'dir': 'ltr'})
                for span in promoted_spans:
                    span_text = span.get_text().strip().lower()
                    if 'promoted' in span_text:
                        is_promoted = True
                        logging.debug(f"🎯 PROMOTED card found for LinkedIn '{title}': span with dir='ltr' containing '{span_text}'")
                        break

                # If not promoted, look for regular posting date information
                if not is_promoted:
                    date_candidates = card.find_all(string=True)
                    for text in date_candidates:
                        text_clean = text.strip()
                        if not text_clean:
                            continue

                        # Check if this is a promoted card (fallback detection)
                        if 'promoted' in text_clean.lower():
                            is_promoted = True
                            logging.debug(f"🎯 PROMOTED card found for LinkedIn '{title}': '{text_clean}' (fallback detection)")
                            break
                        # Check if this is posting date text (not duration) - for logging only
                        elif is_posting_date_text(text_clean):
                            posting_date_text = text_clean
                            logging.debug(f"📅 POSTING DATE found for LinkedIn '{title}': '{text_clean}' (info only - not filtering)")
                            break

                # SKIP date filtering for LinkedIn - URL already filters for 24 hours
                # Keep ALL internships that LinkedIn returns (including promoted ones)
                if is_promoted:
                    logging.debug(f"✅ KEEPING LinkedIn '{title}' - PROMOTED card (no date filtering needed)")
                elif posting_date_text:
                    logging.debug(f"✅ KEEPING LinkedIn '{title}' - posted {posting_date_text} (date filtering skipped)")
                else:
                    logging.debug(f"✅ KEEPING LinkedIn '{title}' - no date info found (date filtering skipped)")

                date_filtered_count += 1

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
                        logging.debug(f"Found company with selector: '{selector}'")
                        break

                company = company_elem.get_text().strip() if company_elem else "Unknown Company"
                logging.debug(f"✅ Card {card_index + 1} company extracted: '{company}'")

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
                        logging.debug(f"Found URL with selector: '{selector}'")
                        break

                if link_elem and link_elem.get('href'):
                    url = link_elem['href']
                    # Ensure URL is absolute
                    if not url.startswith('http'):
                        url = "https://www.linkedin.com" + url
                    logging.debug(f"✅ Card {card_index + 1} URL extracted: '{url}'")
                else:
                    logging.debug(f"❌ No URL found for card {card_index + 1} '{title}' - SKIPPING")
                    continue

                # Create simplified internship entry
                internship = {
                    'title': title,
                    'company': company,
                    'url': url
                }

                internships.append(internship)
                logging.debug(f"🎉 Card {card_index + 1} SUCCESSFULLY ADDED: '{title}' at '{company}'")

                # Enhanced logging for promoted vs regular cards
                if is_promoted:
                    logging.debug(f"Added LinkedIn internship: {title} at {company} (PROMOTED)")
                elif posting_date_text:
                    logging.debug(f"Added LinkedIn internship: {title} at {company} (posted {posting_date_text})")
                else:
                    logging.debug(f"Added LinkedIn internship: {title} at {company} (no date info)")

            except Exception as e:
                logging.debug(f"❌ ERROR parsing card {card_index + 1}: {e}")
                logging.debug(f"Card {card_index + 1} HTML snippet: {str(card)[:300]}...")
                continue

        # Remove duplicates based on URL
        seen_urls = set()
        unique_internships = []
        for internship in internships:
            if internship['url'] not in seen_urls:
                seen_urls.add(internship['url'])
                unique_internships.append(internship)

        logging.info(f"LinkedIn LENIENT filter results (URL pre-filtered for 24h):")
        logging.info(f"  Total internships found: {total_found}")
        logging.info(f"  After lenient processing: {len(unique_internships)}")
        logging.info(f"  Date filtering: SKIPPED (LinkedIn URL already filters for 24 hours)")

        # Log first few internships for debugging
        for i, internship in enumerate(unique_internships[:3]):
            logging.info(f"Sample {i+1}: {internship['title']} at {internship['company']}")

    except Exception as e:
        logging.error(f"Error scraping LinkedIn: {e}")

    return unique_internships

def scrape_letsintern() -> List[Dict]:
    """
    Scrape internship postings from LetsIntern.
    Returns simplified format with only title, company, and url.

    Returns:
        List of internship dictionaries with simplified format
    """
    internships = []
    search_url = "https://letsintern.com/internships/in/hyderabad"

    logging.info("Scraping LetsIntern...")

    try:
        response = make_request_with_retry(search_url)
        if not response:
            return internships

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find internship cards
        internship_cards = soup.find_all('div', class_='internship-card') or soup.find_all('div', class_='job-card')

        for card in internship_cards:
            try:
                # Extract title
                title_elem = card.find('h3') or card.find('h2') or card.find('a', class_='title')
                if not title_elem:
                    continue
                title = title_elem.get_text().strip()

                # Extract company
                company_elem = card.find('p', class_='company') or card.find('span', class_='company')
                company = company_elem.get_text().strip() if company_elem else "Unknown Company"

                # Extract URL
                link_elem = card.find('a')
                if link_elem and link_elem.get('href'):
                    url = link_elem['href']
                    if not url.startswith('http'):
                        url = "https://letsintern.com" + url
                else:
                    continue

                # Create simplified internship entry
                internship = {
                    'title': title,
                    'company': company,
                    'url': url
                }

                internships.append(internship)

            except Exception as e:
                logging.debug(f"Error parsing LetsIntern internship card: {e}")
                continue

        logging.info(f"Scraped {len(internships)} internships from LetsIntern")

    except Exception as e:
        logging.error(f"Error scraping LetsIntern: {e}")

    return internships

def scrape_simplify() -> List[Dict]:
    """
    Scrape internship postings from Simplify.jobs.
    Returns simplified format with only title, company, and url.

    Returns:
        List of internship dictionaries with simplified format
    """
    internships = []
    search_url = "https://simplify.jobs/internships"

    logging.info("Scraping Simplify.jobs...")

    try:
        response = make_request_with_retry(search_url)
        if not response:
            return internships

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find internship rows in table
        internship_rows = soup.find_all('tr', class_='job-row') or soup.find_all('div', class_='job-listing')

        for row in internship_rows:
            try:
                # Extract title
                title_elem = row.find('td', class_='job-title') or row.find('h3') or row.find('a', class_='job-link')
                if not title_elem:
                    continue
                title = title_elem.get_text().strip()

                # Extract company
                company_elem = row.find('td', class_='company') or row.find('span', class_='company')
                company = company_elem.get_text().strip() if company_elem else "Unknown Company"

                # Extract URL
                link_elem = row.find('a')
                if link_elem and link_elem.get('href'):
                    url = link_elem['href']
                    if not url.startswith('http'):
                        url = "https://simplify.jobs" + url
                else:
                    continue

                # Create simplified internship entry
                internship = {
                    'title': title,
                    'company': company,
                    'url': url
                }

                internships.append(internship)

            except Exception as e:
                logging.debug(f"Error parsing Simplify internship row: {e}")
                continue

        logging.info(f"Scraped {len(internships)} internships from Simplify.jobs")

    except Exception as e:
        logging.error(f"Error scraping Simplify.jobs: {e}")

    return internships

def filter_by_date(internships: List[Dict], hours: int = 24) -> List[Dict]:
    """
    Skip date filtering for simplified format (assume all are recent).

    Args:
        internships: List of internship dictionaries
        hours: Maximum age in hours (default: 24) - ignored in simplified format

    Returns:
        All internships (no date filtering applied)
    """
    # Since we don't have posting dates in simplified format, return all internships
    logging.info(f"Date filter: {len(internships)}/{len(internships)} internships (date filtering skipped in simplified format)")
    return internships

def filter_by_branch(internships: List[Dict]) -> List[Dict]:
    """
    Filter internships by branch/field relevance using enhanced keyword matching.
    Priority: CSE/IT (score 3) > EEE/ECE (score 2) > MECH (score 1)

    Args:
        internships: List of internship dictionaries

    Returns:
        Filtered list of internships with priority scoring
    """
    filtered = []

    for internship in internships:
        title = internship.get('title', '').lower()
        company = internship.get('company', '').lower()
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
            internship['priority_score'] = 3
            internship['field_category'] = 'CSE/IT'
            filtered.append(internship)
            logging.debug(f"✅ CSE/IT match: '{title}' - matched keywords: {cse_it_matches}")
        elif eee_ece_matches:
            internship['priority_score'] = 2
            internship['field_category'] = 'EEE/ECE'
            filtered.append(internship)
            logging.debug(f"✅ EEE/ECE match: '{title}' - matched keywords: {eee_ece_matches}")
        elif mech_matches:
            internship['priority_score'] = 1
            internship['field_category'] = 'MECH'
            filtered.append(internship)
            logging.debug(f"✅ MECH match: '{title}' - matched keywords: {mech_matches}")
        else:
            logging.debug(f"❌ No field match: '{title}' - combined text: '{combined_text}'")

    # Sort by priority score (higher first)
    filtered.sort(key=lambda x: x.get('priority_score', 0), reverse=True)

    # Log filtering statistics by category
    cse_it_count = len([i for i in filtered if i.get('field_category') == 'CSE/IT'])
    eee_ece_count = len([i for i in filtered if i.get('field_category') == 'EEE/ECE'])
    mech_count = len([i for i in filtered if i.get('field_category') == 'MECH'])

    logging.info(f"Branch filter results: {len(filtered)}/{len(internships)} internships match field criteria")
    logging.info(f"  CSE/IT: {cse_it_count} internships")
    logging.info(f"  EEE/ECE: {eee_ece_count} internships")
    logging.info(f"  MECH: {mech_count} internships")

    return filtered

def filter_by_location(internships: List[Dict], location: str = "Hyderabad") -> List[Dict]:
    """
    Skip location filtering for simplified format (assume all are from target location).

    Args:
        internships: List of internship dictionaries
        location: Required location (default: "Hyderabad") - ignored in simplified format

    Returns:
        All internships (no location filtering applied)
    """
    # Since we're scraping location-specific URLs, assume all are from target location
    logging.info(f"Location filter: {len(internships)}/{len(internships)} internships (location filtering skipped - using location-specific URLs)")
    return internships

def remove_duplicates(internships: List[Dict]) -> List[Dict]:
    """
    Remove duplicate internships based on title + company + URL.

    Args:
        internships: List of internship dictionaries

    Returns:
        Deduplicated list of internships
    """
    seen = set()
    unique_internships = []
    seen_internships = load_seen_internships()

    for internship in internships:
        # Create unique identifier
        identifier = f"{internship.get('title', '')}-{internship.get('company', '')}-{internship.get('url', '')}"

        # Check if we've seen this before (in current run or previous runs)
        if identifier not in seen and identifier not in seen_internships:
            seen.add(identifier)
            unique_internships.append(internship)

    logging.info(f"Deduplication: {len(unique_internships)}/{len(internships)} unique internships")
    return unique_internships

def select_best_with_ai(internships: List[Dict]) -> Dict:
    """
    Use Groq's AI to select the best internship from filtered results.

    Args:
        internships: List of filtered internship dictionaries

    Returns:
        Selected internship dictionary or error response
    """
    if not internships:
        return {
            "message": "No internships to analyze",
            "total_scraped": 0,
            "ai_decision": "No internships provided for analysis"
        }

    try:
        # Get API key with robust fallback
        api_key = os.getenv('GROQ_API_KEY', GROQ_API_KEY)

        if not api_key:
            logging.warning("No API key available, using fallback selection")
            return select_best_internship_fallback(internships)

        # Validate API key before creating client
        try:
            client = Groq(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to create Groq client: {e}")
            return select_best_internship_fallback(internships)

        logging.info(f"AI analyzing {len(internships)} internships...")

        # Prepare internships for AI analysis
        internships_for_ai = []
        for i, internship in enumerate(internships, 1):
            internship_summary = {
                "number": i,
                "title": internship.get('title', ''),
                "company": internship.get('company', ''),
                "location": internship.get('location', ''),
                "description": internship.get('description', '')[:200] + "..." if len(internship.get('description', '')) > 200 else internship.get('description', ''),
                "source": internship.get('source', '')
            }
            internships_for_ai.append(internship_summary)

        # Create AI prompt
        prompt = f"""You are a career advisor for engineering students. Analyze these internship opportunities and select the SINGLE most valuable and legitimate one.

Evaluation Criteria:
1. Relevance to engineering students (especially CSE/IT/AI/ML)
2. Company legitimacy (avoid fake companies, MLM schemes, unpaid "opportunities")
3. Professional posting quality (detailed description, clear requirements)
4. Learning potential and career value
5. Realistic compensation and expectations

Internships to evaluate:
{json.dumps(internships_for_ai, indent=2)}

Return only the exact title of the selected internship. If all seem suspicious or low-quality, return "NONE"."""

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
                "message": "No suitable internships found matching criteria",
                "total_scraped": len(internships),
                "ai_decision": "All internships flagged as low-quality or suspicious"
            }

        # Find the selected internship
        for internship in internships:
            if selected_title.lower() in internship.get('title', '').lower() or internship.get('title', '').lower() in selected_title.lower():
                selected = internship.copy()
                selected['ai_reasoning'] = "Selected by AI as most valuable and legitimate opportunity"
                save_seen_internship(selected)
                return selected

        # If exact match not found, return first internship as fallback
        logging.warning(f"AI selection '{selected_title}' not found, using first internship")
        fallback = internships[0].copy()
        fallback['ai_reasoning'] = "Fallback selection (AI choice not found)"
        save_seen_internship(fallback)
        return fallback

    except Exception as e:
        logging.error(f"AI selection failed: {e}")
        if internships:
            fallback = internships[0].copy()
            fallback['ai_reasoning'] = "Fallback selection (AI failed)"
            save_seen_internship(fallback)
            return fallback
        else:
            return {
                "message": "AI selection failed and no fallback available",
                "error": str(e)
            }

def select_best_internship_fallback(internships: List[Dict]) -> Dict:
    """
    Fallback selection method using rule-based scoring when AI is unavailable.

    Args:
        internships: List of internship dictionaries

    Returns:
        Selected internship dictionary
    """
    if not internships:
        return {
            "message": "No internships to analyze",
            "total_scraped": 0,
            "selection_method": "fallback_failed"
        }

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from processors.fallback_selector import fallback_select_best

        best_internship = fallback_select_best(internships, 'internship')
        if best_internship:
            result = best_internship.copy()
            result['ai_reasoning'] = "Selected using rule-based fallback algorithm"
            result['selection_method'] = "fallback_algorithm"
            save_seen_internship(result)
            return result
    except ImportError:
        logging.warning("Fallback selector not available, using simple selection")
    except Exception as e:
        logging.error(f"Fallback selection failed: {e}")

    # Simple fallback - select first internship with highest priority score
    best_internship = max(internships, key=lambda x: x.get('priority_score', 0))
    result = best_internship.copy()
    result['ai_reasoning'] = "Selected using simple priority-based fallback"
    result['selection_method'] = "simple_fallback"
    save_seen_internship(result)
    return result

def main() -> Dict:
    """
    Main function to orchestrate the internship scraping and filtering process.

    Returns:
        Final result dictionary with selected internship or error message
    """
    logging.info("=== Starting Intelligent Internship Scraper ===")

    try:
        # Stage 1: Scrape from all sources
        logging.info("Stage 1: Scraping internships from all sources...")
        all_internships = []

        # Scrape from each source
        scrapers = [
            ("Internshala", scrape_internshala),
            ("LinkedIn", scrape_linkedin),
            ("LetsIntern", scrape_letsintern),
            ("Simplify.jobs", scrape_simplify)
        ]

        for source_name, scraper_func in scrapers:
            try:
                internships = scraper_func()
                all_internships.extend(internships)
                logging.info(f"SUCCESS {source_name}: {len(internships)} internships")
            except Exception as e:
                logging.error(f"FAILED {source_name}: {e}")
                continue

        total_scraped = len(all_internships)
        logging.info(f"Total scraped: {total_scraped} internships")

        if not all_internships:
            return {
                "message": "No internships found from any source",
                "total_scraped": 0,
                "after_date_filter": 0,
                "after_branch_filter": 0,
                "after_location_filter": 0,
                "ai_decision": "No internships to analyze"
            }

        # Stage 2: Apply filters
        logging.info("Stage 2: Applying multi-stage filtering...")

        # Date filtering (48 hours) - Note: Already applied in scraping functions
        filtered_by_date = filter_by_date(all_internships, hours=48)  # STRICT 48-hour filtering

        # Branch/field filtering
        filtered_by_branch = filter_by_branch(filtered_by_date)

        # Location filtering
        filtered_by_location = filter_by_location(filtered_by_branch, "Hyderabad")

        # Remove duplicates
        unique_internships = remove_duplicates(filtered_by_location)

        # Log filtering results
        logging.info(f"Filtering results:")
        logging.info(f"  Total scraped: {total_scraped}")
        logging.info(f"  After date filter: {len(filtered_by_date)}")
        logging.info(f"  After branch filter: {len(filtered_by_branch)}")
        logging.info(f"  After location filter: {len(filtered_by_location)}")
        logging.info(f"  After deduplication: {len(unique_internships)}")

        if not unique_internships:
            return {
                "message": "No suitable internships found matching criteria",
                "total_scraped": total_scraped,
                "after_date_filter": len(filtered_by_date),
                "after_branch_filter": len(filtered_by_branch),
                "after_location_filter": len(filtered_by_location),
                "ai_decision": "No internships passed all filters"
            }

        # Save all filtered internships to JSON file
        filtered_output_file = "../data/filtered_internships.json"
        with open(filtered_output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_internships, f, indent=2, ensure_ascii=False)
        logging.info(f"All filtered internships saved to: {filtered_output_file}")

        # Stage 3: AI selection
        logging.info("Stage 3: AI-powered selection...")
        result = select_best_with_ai(unique_internships)

        # Add filtering statistics and all filtered internships to result
        filtering_stats = {
            "total_scraped": total_scraped,
            "after_date_filter": len(filtered_by_date),
            "after_branch_filter": len(filtered_by_branch),
            "after_location_filter": len(filtered_by_location),
            "unique_internships": len(unique_internships)
        }

        if 'title' in result:  # Success case
            result['filtering_stats'] = filtering_stats
            result['all_filtered_internships'] = unique_internships
        else:  # No results case
            result.update(filtering_stats)

        logging.info("=== Internship Scraping Completed ===")
        return result

    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
        return {"message": "Scraping interrupted by user"}
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        return {"message": f"Unexpected error: {str(e)}"}

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import groq
    except ImportError:
        print("Installing required packages...")
        os.system("pip install groq beautifulsoup4 python-dateutil")
        import groq

    # Run the scraper
    result = main()

    # Display results
    print("\n" + "="*60)
    print("🎯 INTELLIGENT INTERNSHIP SCRAPER RESULTS")
    print("="*60)

    if 'title' in result:
        # Display comprehensive filtering statistics first
        if 'filtering_stats' in result:
            stats = result['filtering_stats']
            print(f"📈 MULTI-STAGE FILTERING SUMMARY:")
            print(f"  🔍 Total scraped from all sources: {stats['total_scraped']}")
            print(f"  📅 After date filter (48 hours STRICT): {stats['after_date_filter']}")
            print(f"  🎯 After keyword/branch filter: {stats['after_branch_filter']}")
            print(f"  📍 After location filter (Hyderabad): {stats['after_location_filter']}")
            print(f"  🔄 After deduplication: {stats['unique_internships']}")
            print(f"  ✅ Total qualifying internships: {stats['unique_internships']}")
            print()

        # Display all filtered internships section
        if 'all_filtered_internships' in result and result['all_filtered_internships']:
            print("📋 ALL FILTERED INTERNSHIPS")
            print("=" * 60)
            print(f"Complete list of {len(result['all_filtered_internships'])} internships that passed all filtering criteria:")
            print("-" * 60)
            for i, internship in enumerate(result['all_filtered_internships'], 1):
                priority_score = internship.get('priority_score', 0)
                field_category = internship.get('field_category', 'Unknown')

                if priority_score == 3:
                    priority_text = "🔥 HIGHEST (CSE/IT)"
                elif priority_score == 2:
                    priority_text = "⭐ HIGH (EEE/ECE)"
                elif priority_score == 1:
                    priority_text = "📌 MEDIUM (MECH)"
                else:
                    priority_text = "❓ LOW"

                print(f"{i}. {internship['title']}")
                print(f"   🏢 Company: {internship['company']}")
                print(f"   🎯 Priority: {priority_text} (Score: {priority_score})")
                print(f"   📚 Field: {field_category}")
                print(f"   🔗 URL: {internship['url']}")
                print()

        # Display AI-selected internship prominently
        print("🤖 AI-SELECTED INTERNSHIP")
        print("=" * 60)
        print("🏆 TOP RECOMMENDATION (Selected by AI from filtered results):")
        print("-" * 60)
        print(f"🏆 Title: {result['title']}")
        print(f"🏢 Company: {result['company']}")
        print(f"🔗 URL: {result['url']}")
        print(f"🤖 AI Reasoning: {result.get('ai_reasoning', 'N/A')}")
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

        # Save AI-selected result to JSON file (clean format)
        output_file = "../data/selected_internship.json"
        clean_result = {
            "title": result['title'],
            "company": result['company'],
            "url": result['url'],
            "priority_score": result.get('priority_score', 0),
            "field_category": result.get('field_category', 'Unknown'),
            "ai_reasoning": result.get('ai_reasoning', '')
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clean_result, f, indent=2, ensure_ascii=False)

        print(f"\n💾 FILE OUTPUTS:")
        print(f"  📄 All filtered internships → filtered_internships.json ({len(result['all_filtered_internships'])} internships)")
        print(f"  🎯 AI-selected internship → selected_internship.json (1 internship)")

    else:
        # No results or error
        print("❌ NO SUITABLE INTERNSHIPS FOUND")
        print(f"Message: {result.get('message', 'Unknown error')}")

        # Display filtering statistics even when no results
        if 'total_scraped' in result:
            print(f"\n📈 MULTI-STAGE FILTERING SUMMARY:")
            print(f"  🔍 Total scraped from all sources: {result.get('total_scraped', 0)}")
            print(f"  📅 After date filter (48 hours STRICT): {result.get('after_date_filter', 0)}")
            print(f"  🎯 After keyword/branch filter: {result.get('after_branch_filter', 0)}")
            print(f"  📍 After location filter (Hyderabad): {result.get('after_location_filter', 0)}")
            print(f"  🔄 After deduplication: {result.get('unique_internships', 0)}")
            print(f"  ✅ Total qualifying internships: {result.get('unique_internships', 0)}")

        if 'ai_decision' in result:
            print(f"\n🤖 AI Decision: {result['ai_decision']}")

        # Create empty files for consistency
        with open('../data/filtered_internships.json', 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
        with open('../data/selected_internship.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)

        print(f"\n💾 FILE OUTPUTS:")
        print(f"  📄 All filtered internships → filtered_internships.json (0 internships)")
        print(f"  🎯 AI-selected internship → selected_internship.json (no selection)")

    print("\n" + "="*60)