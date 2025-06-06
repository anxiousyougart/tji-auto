#!/usr/bin/env python3


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
from urllib.parse import urljoin, urlparse
from groq import Groq

# Import centralized configuration
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.config import get_groq_api_key, REQUEST_TIMEOUT, MAX_RETRIES as CONFIG_MAX_RETRIES
    GROQ_API_KEY = get_groq_api_key()
    MAX_RETRIES = CONFIG_MAX_RETRIES
except ImportError:
    # Fallback configuration if config.py is not available
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MAX_RETRIES = 3

# Configuration
REQUEST_DELAY = 1  # seconds between requests

# Deduplication system configuration
UPSKILL_HISTORY_FILE = "../data/upskill_articles_history.json"
HISTORY_DAYS = 30  # Keep 30 days of history

# URL Configuration - Easy to modify and extend
UPSKILL_URLS = {
    "dev_to": [
        "https://dev.to/t/tutorial"
    ],
    "kdnuggets": [
        "https://www.kdnuggets.com/"
    ],
    "medium": [
        "https://medium.com/tag/programming",
        "https://medium.com/tag/tutorial",
        "https://medium.com/tag/web-development"
    ],
    "company_blogs": [
        "https://github.blog/category/engineering/",
        "https://engineering.fb.com/",
        "https://netflixtechblog.com/",
        "https://blog.google/technology/",
        "https://aws.amazon.com/blogs/aws/",
        "https://devblogs.microsoft.com/",
        "https://blog.twitter.com/engineering/en_us",
        "https://engineering.linkedin.com/blog",
        "https://stackoverflow.blog/",
        "https://blog.jetbrains.com/",
        "https://blog.docker.com/",
        "https://kubernetes.io/blog/"
    ],
    "tech_education": [
        "https://www.freecodecamp.org/news/",
        "https://css-tricks.com/",
        "https://www.smashingmagazine.com/",
        "https://hackernoon.com/",
        "https://www.digitalocean.com/community/tutorials"
    ],
    "thenewstack": [
        "https://thenewstack.io/webassembly/",
        "https://thenewstack.io/software-development/",
        "https://thenewstack.io/security/",
        "https://thenewstack.io/llm/",
        "https://thenewstack.io/frontend-development/",
        "https://thenewstack.io/data/",
        "https://thenewstack.io/backend-development/",
        "https://thenewstack.io/api-management/",
        "https://thenewstack.io/ai/"
    ],
    "additional_tech": [
        "https://www.xda-developers.com/"
    ]
}

def load_urls_from_config(config_file: str = "../data/upskill_urls_config.json") -> Dict:
    """
    Load URLs from configuration file. Falls back to hardcoded URLs if file doesn't exist.

    Args:
        config_file: Path to the JSON configuration file

    Returns:
        Dictionary containing URL configurations
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                urls = json.load(f)
            logging.info(f"Loaded URLs from configuration file: {config_file}")
            return urls
        else:
            logging.info(f"Configuration file {config_file} not found, using hardcoded URLs")
            return UPSKILL_URLS
    except Exception as e:
        logging.warning(f"Error loading configuration file {config_file}: {e}. Using hardcoded URLs.")
        return UPSKILL_URLS

def save_urls_to_config(urls: Dict, config_file: str = "../data/upskill_urls_config.json") -> bool:
    """
    Save URLs to configuration file for easy management.

    Args:
        urls: Dictionary containing URL configurations
        config_file: Path to the JSON configuration file

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=2, ensure_ascii=False)
        logging.info(f"URLs saved to configuration file: {config_file}")
        return True
    except Exception as e:
        logging.error(f"Error saving URLs to configuration file {config_file}: {e}")
        return False

def add_url_to_config(category: str, url: str, config_file: str = "../data/upskill_urls_config.json") -> bool:
    """
    Add a new URL to a specific category in the configuration.

    Args:
        category: Category name (e.g., 'tech_education', 'company_blogs')
        url: URL to add
        config_file: Path to the JSON configuration file

    Returns:
        True if successful, False otherwise
    """
    try:
        urls = load_urls_from_config(config_file)

        if category not in urls:
            urls[category] = []

        if url not in urls[category]:
            urls[category].append(url)
            save_urls_to_config(urls, config_file)
            logging.info(f"Added URL {url} to category {category}")
            return True
        else:
            logging.info(f"URL {url} already exists in category {category}")
            return True
    except Exception as e:
        logging.error(f"Error adding URL to configuration: {e}")
        return False

# Load URLs from configuration file
UPSKILL_URLS = load_urls_from_config()

# Headers for web requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/upskill_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Keywords for filtering upskill/educational content
UPSKILL_INCLUDE_KEYWORDS = [
    # Tutorial and learning content
    "tutorial", "guide", "how to", "step by step", "walkthrough", "learn", "learning",
    "beginner", "getting started", "introduction to", "intro to", "basics", "fundamentals",
    "course", "lesson", "workshop", "training", "bootcamp", "masterclass",

    # Implementation and project content
    "build", "create", "implement", "develop", "project", "hands-on", "practical",
    "example", "demo", "sample", "code", "coding", "programming", "development",
    "from scratch", "complete guide", "full tutorial", "end-to-end",

    # Best practices and recommendations
    "best practices", "best practice", "tips", "tricks", "optimization", "performance",
    "architecture", "design patterns", "clean code", "code quality", "testing",
    "deployment", "devops", "ci/cd", "security", "scalability",

    # Technology and tools
    "framework", "library", "tool", "stack", "technology", "tech stack", "setup",
    "configuration", "installation", "environment", "workflow", "productivity",

    # Specific technologies (popular among CS students)
    "python", "javascript", "react", "node.js", "django", "flask", "express",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "api",
    "database", "sql", "mongodb", "postgresql", "machine learning", "ai",
    "data science", "web development", "mobile development", "android", "ios",
    "flutter", "react native", "vue", "angular", "typescript", "java", "spring",
    "microservices", "rest api", "graphql", "redis", "elasticsearch", "kafka"
]

# Keywords to exclude non-educational content
UPSKILL_EXCLUDE_KEYWORDS = [
    # Business and corporate news
    "funding", "acquisition", "merger", "ipo", "stock", "valuation", "investment",
    "ceo", "executive", "layoffs", "hiring", "company news", "earnings", "revenue",

    # Opinion and editorial content
    "opinion", "editorial", "commentary", "thoughts on", "my take", "perspective",
    "rant", "controversial", "debate", "argument", "criticism", "review",

    # Event and promotional content
    "conference", "event", "webinar", "meetup", "summit", "announcement",
    "launch", "release", "unveiling", "keynote", "presentation",

    # Non-technical content
    "career advice", "job interview", "resume", "salary", "workplace", "remote work",
    "productivity tips", "time management", "soft skills", "communication",

    # Outdated or deprecated content indicators
    "deprecated", "legacy", "old version", "outdated", "no longer supported"
]

def make_request_with_retry(url: str, max_retries: int = MAX_RETRIES) -> Optional[requests.Response]:
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

def is_upskill_relevant(article: Dict) -> bool:
    """
    Determine if an article is relevant for upskilling based on keyword matching.

    Args:
        article: Article dictionary containing title and other fields

    Returns:
        True if the article is relevant for upskilling, False otherwise
    """
    title = article.get('title', '').lower()

    # Skip empty titles or placeholder titles
    if not title or title == "no title found" or len(title.strip()) < 10:
        return False

    # Check for include keywords
    include_matches = []
    for keyword in UPSKILL_INCLUDE_KEYWORDS:
        if keyword.lower() in title:
            include_matches.append(keyword)

    # Check for exclude keywords
    exclude_match = False
    for keyword in UPSKILL_EXCLUDE_KEYWORDS:
        if keyword.lower() in title:
            exclude_match = True
            break

    # Require at least 1 include keyword and no exclude keywords
    is_relevant = len(include_matches) >= 1 and not exclude_match

    if is_relevant:
        logging.debug(f"Relevant upskill article: {title[:50]}... (matched: {include_matches[:3]})")

    return is_relevant

def extract_date_from_article(article_element, url: str = None) -> Optional[datetime.datetime]:
    """
    Extract publication date from an article element with site-specific handling.

    Args:
        article_element: BeautifulSoup element containing the article
        url: Source URL for site-specific date extraction

    Returns:
        datetime object if date found, None otherwise
    """
    # Common date selectors
    date_selectors = [
        'time', '.date', '.time', '.datetime', '.published', '.pubdate',
        '[datetime]', '[pubdate]', '.timestamp', '.post-date', '.entry-date',
        'meta[property="article:published_time"]', 'meta[itemprop="datePublished"]',
        '.published-date', '.article-date', '.post-meta time'
    ]

    # Try each selector
    for selector in date_selectors:
        date_elem = article_element.select_one(selector)
        if date_elem:
            # Try datetime attribute first
            date_str = date_elem.get('datetime') or date_elem.get('content') or date_elem.get_text().strip()
            if date_str:
                try:
                    return parser.parse(date_str)
                except (ValueError, TypeError):
                    continue

    # Site-specific date extraction
    if url:
        if 'dev.to' in url:
            # Dev.to specific date extraction
            date_elem = article_element.select_one('.crayons-story__meta time, .crayons-article__meta time')
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text().strip()
                try:
                    return parser.parse(date_str)
                except (ValueError, TypeError):
                    pass

        elif 'kdnuggets.com' in url:
            # KDnuggets specific date extraction
            date_elem = article_element.select_one('.post-date, .entry-date, .published')
            if date_elem:
                date_str = date_elem.get_text().strip()
                try:
                    return parser.parse(date_str)
                except (ValueError, TypeError):
                    pass

    # Try to find date patterns in article text
    article_text = article_element.get_text()
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # ISO format
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}',
        r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
        r'(\d+)\s+(day|week|month)s?\s+ago'  # Relative time
    ]

    for pattern in date_patterns:
        match = re.search(pattern, article_text)
        if match:
            try:
                date_str = match.group(0)
                if 'ago' in date_str:
                    # Handle relative dates
                    num_match = re.search(r'(\d+)', date_str)
                    if num_match:
                        num = int(num_match.group(1))
                        if 'day' in date_str:
                            return datetime.datetime.now() - datetime.timedelta(days=num)
                        elif 'week' in date_str:
                            return datetime.datetime.now() - datetime.timedelta(weeks=num)
                        elif 'month' in date_str:
                            return datetime.datetime.now() - datetime.timedelta(days=num*30)
                else:
                    return parser.parse(date_str)
            except (ValueError, TypeError):
                continue

    return None

def is_recent_7days(pub_date: Optional[datetime.datetime]) -> bool:
    """
    Check if article was published within the last 7 days.
    Uses 7-day window for educational content discovery.

    Args:
        pub_date: Publication date

    Returns:
        True if within 7 days or date unknown (lenient), False otherwise
    """
    if pub_date is None:
        # Be lenient with missing dates for educational content
        return True

    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(days=7)

    return pub_date >= seven_days_ago

def scrape_dev_to() -> List[Dict]:
    """
    Scrape tutorial articles from Dev.to using configured URLs.

    Returns:
        List of article dictionaries with title and url
    """
    articles = []
    urls = UPSKILL_URLS["dev_to"]

    logging.info("Scraping Dev.to tutorials...")

    for url in urls:
        try:
            response = make_request_with_retry(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Dev.to uses crayons-story class for articles
            article_elements = soup.select('.crayons-story, .crayons-card')

            if not article_elements:
                # Fallback to generic article selectors
                article_elements = soup.select('article, .story, .post')

            base_url = "https://dev.to"

            for article in article_elements:
                try:
                    # Extract title
                    title_elem = article.select_one('.crayons-story__title a, h2 a, h3 a, .title a')
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # Extract URL
                    link = title_elem.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = urljoin(base_url, link)
                    else:
                        continue

                    # Extract date
                    pub_date = extract_date_from_article(article, url)

                    # Apply 7-day date filter
                    if is_recent_7days(pub_date):
                        article_dict = {'title': title, 'url': link}
                        if is_upskill_relevant(article_dict):
                            articles.append(article_dict)
                            logging.info(f"Found relevant Dev.to article: {title[:50]}...")

                except Exception as e:
                    logging.debug(f"Error parsing Dev.to article: {e}")
                    continue

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logging.error(f"Failed to scrape Dev.to URL {url}: {e}")
            continue

    logging.info(f"Dev.to results: {len(articles)} articles")
    return articles

def scrape_kdnuggets() -> List[Dict]:
    """
    Scrape data science and ML articles from KDnuggets using configured URLs.

    Returns:
        List of article dictionaries with title and url
    """
    articles = []
    urls = UPSKILL_URLS["kdnuggets"]

    logging.info("Scraping KDnuggets...")

    for url in urls:
        try:
            response = make_request_with_retry(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # KDnuggets uses various selectors for articles
            article_elements = soup.select('article, .post, .entry, .news-item, .article-item')

            if not article_elements:
                # Try to find articles by looking for title links
                for elem in soup.find_all(['div', 'section']):
                    if elem.find(['h1', 'h2', 'h3']) and elem.find('a'):
                        article_elements.append(elem)

            base_url = urlparse(url)
            base_domain = f"{base_url.scheme}://{base_url.netloc}"

            for article in article_elements:
                try:
                    # Extract title
                    title_elem = article.select_one('h1 a, h2 a, h3 a, .title a, .entry-title a')
                    if not title_elem:
                        # Try to find any link with substantial text
                        links = article.find_all('a')
                        for link in links:
                            text = link.get_text().strip()
                            if len(text) > 20 and not any(skip in text.lower() for skip in ['read more', 'continue', 'comments']):
                                title_elem = link
                                break

                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # Extract URL
                    link = title_elem.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = urljoin(base_domain, link)
                    else:
                        continue

                    # Extract date
                    pub_date = extract_date_from_article(article, url)

                    # Apply 7-day date filter
                    if is_recent_7days(pub_date):
                        article_dict = {'title': title, 'url': link}
                        if is_upskill_relevant(article_dict):
                            articles.append(article_dict)
                            logging.info(f"Found relevant KDnuggets article: {title[:50]}...")

                except Exception as e:
                    logging.debug(f"Error parsing KDnuggets article: {e}")
                    continue

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logging.error(f"Failed to scrape KDnuggets URL {url}: {e}")
            continue

    logging.info(f"KDnuggets results: {len(articles)} articles")
    return articles

def scrape_medium_tech() -> List[Dict]:
    """
    Scrape tech tutorials from Medium's programming and technology tags using configured URLs.

    Returns:
        List of article dictionaries with title and url
    """
    articles = []
    urls = UPSKILL_URLS["medium"]

    logging.info("Scraping Medium tech articles...")

    for url in urls:
        try:
            response = make_request_with_retry(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Medium uses various selectors for articles
            article_elements = soup.select('article, .postArticle, .streamItem, .post')

            for article in article_elements:
                try:
                    # Extract title
                    title_elem = article.select_one('h1 a, h2 a, h3 a, .graf--title a, [data-testid="post-preview-title"]')
                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # Extract URL
                    link = title_elem.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = urljoin("https://medium.com", link)
                    else:
                        continue

                    # Extract date
                    pub_date = extract_date_from_article(article, url)

                    # Apply 7-day date filter
                    if is_recent_7days(pub_date):
                        article_dict = {'title': title, 'url': link}
                        if is_upskill_relevant(article_dict):
                            articles.append(article_dict)
                            logging.info(f"Found relevant Medium article: {title[:50]}...")

                except Exception as e:
                    logging.debug(f"Error parsing Medium article: {e}")
                    continue

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logging.error(f"Failed to scrape Medium URL {url}: {e}")
            continue

    logging.info(f"Medium results: {len(articles)} articles")
    return articles

def scrape_thenewstack() -> List[Dict]:
    """
    Scrape articles from The New Stack's various technology categories.

    Returns:
        List of article dictionaries with title and url
    """
    articles = []
    urls = UPSKILL_URLS["thenewstack"]

    logging.info("Scraping The New Stack articles...")

    for url in urls:
        try:
            response = make_request_with_retry(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # The New Stack uses various selectors for articles
            article_elements = soup.select('article, .post, .entry, .story, .article-item')

            if not article_elements:
                # Try to find articles by looking for title links
                for elem in soup.find_all(['div', 'section']):
                    if elem.find(['h1', 'h2', 'h3']) and elem.find('a'):
                        article_elements.append(elem)

            base_url = urlparse(url)
            base_domain = f"{base_url.scheme}://{base_url.netloc}"

            for article in article_elements:
                try:
                    # Extract title
                    title_elem = article.select_one('h1 a, h2 a, h3 a, .title a, .entry-title a, .post-title a')
                    if not title_elem:
                        # Try to find any link with substantial text
                        links = article.find_all('a')
                        for link in links:
                            text = link.get_text().strip()
                            if len(text) > 20 and not any(skip in text.lower() for skip in ['read more', 'continue', 'comments']):
                                title_elem = link
                                break

                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # Extract URL
                    link = title_elem.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = urljoin(base_domain, link)
                    else:
                        continue

                    # Extract date
                    pub_date = extract_date_from_article(article, url)

                    # Apply 7-day date filter
                    if is_recent_7days(pub_date):
                        article_dict = {'title': title, 'url': link}
                        if is_upskill_relevant(article_dict):
                            articles.append(article_dict)
                            logging.info(f"Found relevant The New Stack article: {title[:50]}...")

                except Exception as e:
                    logging.debug(f"Error parsing The New Stack article from {url}: {e}")
                    continue

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logging.error(f"Failed to scrape The New Stack URL {url}: {e}")
            continue

    logging.info(f"The New Stack results: {len(articles)} articles")
    return articles

def scrape_company_blogs() -> List[Dict]:
    """
    Scrape engineering blogs from major tech companies using configured URLs.

    Returns:
        List of article dictionaries with title and url
    """
    articles = []
    urls = UPSKILL_URLS["company_blogs"]

    logging.info("Scraping company engineering blogs...")

    for url in urls:
        try:
            response = make_request_with_retry(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Generic selectors for blog articles
            article_elements = soup.select('article, .post, .entry, .blog-post, .article-item')

            if not article_elements:
                # Try to find articles by looking for title links
                for elem in soup.find_all(['div', 'section']):
                    if elem.find(['h1', 'h2', 'h3']) and elem.find('a'):
                        article_elements.append(elem)

            base_url = urlparse(url)
            base_domain = f"{base_url.scheme}://{base_url.netloc}"

            for article in article_elements:
                try:
                    # Extract title
                    title_elem = article.select_one('h1 a, h2 a, h3 a, .title a, .entry-title a, .post-title a')
                    if not title_elem:
                        # Try to find any link with substantial text
                        links = article.find_all('a')
                        for link in links:
                            text = link.get_text().strip()
                            if len(text) > 20 and not any(skip in text.lower() for skip in ['read more', 'continue', 'comments']):
                                title_elem = link
                                break

                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # Extract URL
                    link = title_elem.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = urljoin(base_domain, link)
                    else:
                        continue

                    # Extract date
                    pub_date = extract_date_from_article(article, url)

                    # Apply 7-day date filter
                    if is_recent_7days(pub_date):
                        article_dict = {'title': title, 'url': link}
                        if is_upskill_relevant(article_dict):
                            articles.append(article_dict)
                            logging.info(f"Found relevant company blog article: {title[:50]}...")

                except Exception as e:
                    logging.debug(f"Error parsing company blog article from {url}: {e}")
                    continue

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logging.error(f"Failed to scrape company blog {url}: {e}")
            continue

    logging.info(f"Company blogs results: {len(articles)} articles")
    return articles

def scrape_additional_tech_sites() -> List[Dict]:
    """
    Scrape additional educational tech sites for tutorials and guides using configured URLs.

    Returns:
        List of article dictionaries with title and url
    """
    articles = []
    urls = UPSKILL_URLS["tech_education"]

    logging.info("Scraping additional tech education sites...")

    for url in urls:
        try:
            response = make_request_with_retry(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Generic selectors for articles
            article_elements = soup.select('article, .post, .entry, .tutorial, .guide')

            if not article_elements:
                # Try to find articles by looking for title links
                for elem in soup.find_all(['div', 'section']):
                    if elem.find(['h1', 'h2', 'h3']) and elem.find('a'):
                        article_elements.append(elem)

            base_url = urlparse(url)
            base_domain = f"{base_url.scheme}://{base_url.netloc}"

            for article in article_elements:
                try:
                    # Extract title
                    title_elem = article.select_one('h1 a, h2 a, h3 a, .title a, .entry-title a, .post-title a')
                    if not title_elem:
                        # Try to find any link with substantial text
                        links = article.find_all('a')
                        for link in links:
                            text = link.get_text().strip()
                            if len(text) > 20 and not any(skip in text.lower() for skip in ['read more', 'continue', 'comments']):
                                title_elem = link
                                break

                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # Extract URL
                    link = title_elem.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = urljoin(base_domain, link)
                    else:
                        continue

                    # Extract date
                    pub_date = extract_date_from_article(article, url)

                    # Apply 7-day date filter
                    if is_recent_7days(pub_date):
                        article_dict = {'title': title, 'url': link}
                        if is_upskill_relevant(article_dict):
                            articles.append(article_dict)
                            logging.info(f"Found relevant tech site article: {title[:50]}...")

                except Exception as e:
                    logging.debug(f"Error parsing tech site article from {url}: {e}")
                    continue

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logging.error(f"Failed to scrape tech site {url}: {e}")
            continue

    logging.info(f"Additional tech sites results: {len(articles)} articles")
    return articles

def scrape_xda_developers() -> List[Dict]:
    """
    Scrape tech articles from XDA Developers and other additional tech sites.

    Returns:
        List of article dictionaries with title and url
    """
    articles = []
    urls = UPSKILL_URLS["additional_tech"]

    logging.info("Scraping XDA Developers and additional tech sites...")

    for url in urls:
        try:
            response = make_request_with_retry(url)
            if not response:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # Generic selectors for articles
            article_elements = soup.select('article, .post, .entry, .news-item, .article-item')

            if not article_elements:
                # Try to find articles by looking for title links
                for elem in soup.find_all(['div', 'section']):
                    if elem.find(['h1', 'h2', 'h3']) and elem.find('a'):
                        article_elements.append(elem)

            base_url = urlparse(url)
            base_domain = f"{base_url.scheme}://{base_url.netloc}"

            for article in article_elements:
                try:
                    # Extract title
                    title_elem = article.select_one('h1 a, h2 a, h3 a, .title a, .entry-title a, .post-title a')
                    if not title_elem:
                        # Try to find any link with substantial text
                        links = article.find_all('a')
                        for link in links:
                            text = link.get_text().strip()
                            if len(text) > 20 and not any(skip in text.lower() for skip in ['read more', 'continue', 'comments']):
                                title_elem = link
                                break

                    if not title_elem:
                        continue

                    title = title_elem.get_text().strip()
                    if not title:
                        continue

                    # Extract URL
                    link = title_elem.get('href')
                    if link:
                        if not link.startswith('http'):
                            link = urljoin(base_domain, link)
                    else:
                        continue

                    # Extract date
                    pub_date = extract_date_from_article(article, url)

                    # Apply 7-day date filter
                    if is_recent_7days(pub_date):
                        article_dict = {'title': title, 'url': link}
                        if is_upskill_relevant(article_dict):
                            articles.append(article_dict)
                            logging.info(f"Found relevant XDA/additional tech article: {title[:50]}...")

                except Exception as e:
                    logging.debug(f"Error parsing XDA/additional tech article from {url}: {e}")
                    continue

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            logging.error(f"Failed to scrape XDA/additional tech URL {url}: {e}")
            continue

    logging.info(f"XDA Developers and additional tech sites results: {len(articles)} articles")
    return articles

def load_upskill_history():
    """
    Load the history of previously selected upskill articles.

    Returns:
        dict: Dictionary with article titles and URLs as keys, and selection dates as values
    """
    try:
        if os.path.exists(UPSKILL_HISTORY_FILE):
            with open(UPSKILL_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # Clean old entries (older than HISTORY_DAYS)
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=HISTORY_DAYS)
            cleaned_history = {}

            for key, date_str in history.items():
                try:
                    entry_date = datetime.datetime.fromisoformat(date_str)
                    if entry_date >= cutoff_date:
                        cleaned_history[key] = date_str
                except (ValueError, TypeError):
                    # Skip invalid date entries
                    continue

            # Save cleaned history back
            if len(cleaned_history) != len(history):
                save_upskill_history(cleaned_history)

            logging.info(f"Loaded {len(cleaned_history)} upskill articles from history (cleaned from {len(history)})")
            return cleaned_history
        else:
            logging.info("No upskill history file found, starting fresh")
            return {}
    except Exception as e:
        logging.error(f"Error loading upskill article history: {e}")
        return {}

def save_upskill_history(history):
    """
    Save the upskill article history to file.

    Args:
        history (dict): Dictionary with article titles/URLs and selection dates
    """
    try:
        with open(UPSKILL_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logging.debug(f"Saved {len(history)} upskill articles to history")
    except Exception as e:
        logging.error(f"Error saving upskill article history: {e}")

def add_to_upskill_history(article):
    """
    Add an upskill article to the selection history.

    Args:
        article (dict): Article with 'title' and 'url' keys
    """
    try:
        history = load_upskill_history()
        current_time = datetime.datetime.now().isoformat()

        # Use both title and URL as keys for duplicate detection
        title_key = f"title:{article['title'].lower().strip()}"
        url_key = f"url:{article['url'].lower().strip()}"

        history[title_key] = current_time
        history[url_key] = current_time

        save_upskill_history(history)
        logging.info(f"Added upskill article to history: {article['title'][:50]}...")
    except Exception as e:
        logging.error(f"Error adding upskill article to history: {e}")

def filter_previously_selected(articles):
    """
    Filter out articles that have been previously selected.

    Args:
        articles (list): List of article dictionaries

    Returns:
        list: Filtered list of articles that haven't been selected before
    """
    try:
        history = load_upskill_history()
        if not history:
            logging.info("No history found, all articles are new")
            return articles

        filtered_articles = []
        filtered_count = 0

        for article in articles:
            title_key = f"title:{article['title'].lower().strip()}"
            url_key = f"url:{article['url'].lower().strip()}"

            # Check if either title or URL has been seen before
            if title_key in history or url_key in history:
                filtered_count += 1
                logging.debug(f"Filtered duplicate upskill article: {article['title'][:50]}...")
            else:
                filtered_articles.append(article)

        logging.info(f"Deduplication: {filtered_count} previously selected articles filtered out, {len(filtered_articles)} new articles remain")
        return filtered_articles

    except Exception as e:
        logging.error(f"Error filtering previously selected articles: {e}")
        return articles  # Return original list if filtering fails

def upskill_articles(urls: List[str] = None) -> List[Dict]:
    """
    Scrape upskill articles from various educational tech platforms with 7-day date filtering.

    This function scrapes tutorial and educational content from multiple sources,
    focusing on articles that help CS students learn new technologies and best practices.
    Uses 7-day date filtering for broader educational content discovery.

    Args:
        urls: Optional list of additional URLs to scrape (not implemented yet)

    Returns:
        List of dictionaries with 'title' and 'url' keys containing upskill articles
    """
    all_articles = []

    logging.info("Starting upskill articles scraping...")

    # Scrape from different sources
    scrapers = [
        ("Dev.to", scrape_dev_to),
        ("KDnuggets", scrape_kdnuggets),
        ("Medium", scrape_medium_tech),
        ("Company Blogs", scrape_company_blogs),
        ("Tech Education Sites", scrape_additional_tech_sites),
        ("The New Stack", scrape_thenewstack),
        ("XDA Developers & Additional", scrape_xda_developers)
    ]

    for source_name, scraper_func in scrapers:
        try:
            articles = scraper_func()
            all_articles.extend(articles)
            logging.info(f"SUCCESS {source_name}: {len(articles)} articles")
        except Exception as e:
            logging.error(f"FAILED {source_name}: {e}")
            continue

    # Remove duplicates based on URL (within current session)
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)

    logging.info(f"Session deduplication: Found {len(unique_articles)} unique articles from {len(scrapers)} sources")

    # Filter out previously selected articles (across multiple runs)
    new_articles = filter_previously_selected(unique_articles)

    logging.info(f"Scraping completed. Found {len(new_articles)} new upskill articles (filtered {len(unique_articles) - len(new_articles)} previously selected)")
    return new_articles

def select_best_upskill_article(json_file_path: str = "../data/upskill_articles.json",
                               api_key: str = None) -> Dict:
    """
    Use Groq's AI to select the most valuable upskill article from the scraped results.

    Args:
        json_file_path: Path to the JSON file containing scraped articles
        api_key: Groq API key (uses default if not provided)

    Returns:
        Dictionary containing the AI-selected article and reasoning
    """
    try:
        # Get API key with robust fallback
        if not api_key:
            api_key = os.getenv('GROQ_API_KEY', GROQ_API_KEY)

        if not api_key:
            logging.warning("No API key available, using fallback selection")
            return select_best_upskill_fallback(json_file_path)

        # Validate API key before creating client
        try:
            client = Groq(api_key=api_key)
        except Exception as e:
            logging.error(f"Failed to create Groq client: {e}")
            return select_best_upskill_fallback(json_file_path)

        # Load articles from JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        if not articles:
            return {"error": "No articles found in the JSON file"}

        # Apply deduplication filter to articles before AI selection
        filtered_articles = filter_previously_selected(articles)

        if not filtered_articles:
            logging.warning("All articles have been previously selected")
            return {
                "error": "All articles have been previously selected",
                "total_articles_found": len(articles),
                "previously_selected": len(articles),
                "suggestion": "Try running the scraper again later for new content"
            }

        # Use filtered articles for AI analysis
        articles_to_analyze = filtered_articles
        logging.info(f"AI analyzing {len(articles_to_analyze)} new upskill articles (filtered {len(articles) - len(articles_to_analyze)} previously selected)...")

        # Prepare articles for AI analysis
        articles_text = "\n".join([f"{i+1}. {article['title']}" for i, article in enumerate(articles_to_analyze)])

        prompt = f"""You are an expert computer science educator helping students find the most valuable learning resources.

Analyze these {len(articles_to_analyze)} upskill articles and select the ONE most valuable article for computer science engineering students to learn from:

{articles_text}

Selection Criteria (in order of priority):
1. **Practical Learning Value**: Tutorials, hands-on guides, implementation examples
2. **Technology Relevance**: Modern, in-demand technologies (React, Python, AI/ML, cloud, etc.)
3. **Skill Building**: Articles that teach concrete, applicable skills
4. **Best Practices**: Architecture, design patterns, optimization techniques
5. **Career Impact**: Technologies and skills that enhance job prospects

Focus on articles that:
- Provide step-by-step tutorials or implementation guides
- Teach modern, industry-relevant technologies
- Offer practical coding examples and projects
- Share best practices and professional development techniques
- Help students build portfolio-worthy skills

Avoid articles that are:
- Too theoretical without practical application
- About outdated technologies
- Opinion pieces without actionable content
- Basic introductions to well-known concepts

Respond with ONLY the number (1-{len(articles_to_analyze)}) of your selected article, followed by a brief explanation of why this article is most valuable for CS student upskilling."""

        # Get AI response
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=500
        )

        ai_response = chat_completion.choices[0].message.content.strip()

        # Extract the selected article number with improved parsing
        import re

        # Try multiple patterns to extract the number
        patterns = [
            r'^(\d+)',  # Number at start
            r'(\d+)\.',  # Number followed by period
            r'article\s+(\d+)',  # "article 3"
            r'number\s+(\d+)',  # "number 3"
            r'#(\d+)',  # "#3"
        ]

        selected_index = None
        for pattern in patterns:
            number_match = re.search(pattern, ai_response, re.IGNORECASE)
            if number_match:
                try:
                    selected_index = int(number_match.group(1)) - 1
                    if 0 <= selected_index < len(articles_to_analyze):
                        break
                except (ValueError, IndexError):
                    continue

        if selected_index is not None and 0 <= selected_index < len(articles_to_analyze):
            selected_article = articles_to_analyze[selected_index]

            # Add selected article to history to prevent future duplicates
            add_to_upskill_history(selected_article)

            result = {
                "selected_article": selected_article,
                "ai_reasoning": ai_response,
                "total_articles_scraped": len(articles),
                "total_articles_analyzed": len(articles_to_analyze),
                "previously_selected_filtered": len(articles) - len(articles_to_analyze),
                "selection_criteria": "Practical learning value, technology relevance, skill building potential",
                "deduplication_enabled": True
            }

            # Save the AI-selected article
            with open("../data/ai_selected_upskill_article.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logging.info(f"AI selected article: {selected_article['title'][:50]}...")
            return result

        # If parsing failed, return error with more details
        return {
            "error": "Could not parse AI response to extract article number",
            "ai_response": ai_response,
            "total_articles_scraped": len(articles),
            "total_articles_analyzed": len(articles_to_analyze),
            "debug_info": "AI response did not contain a recognizable article number (1-{})".format(len(articles_to_analyze))
        }

    except Exception as e:
        logging.error(f"Error in AI article selection: {e}")
        logging.info("Falling back to rule-based selection")
        return select_best_upskill_fallback(json_file_path)

def select_best_upskill_fallback(json_file_path: str = "../data/upskill_articles.json") -> Dict:
    """
    Fallback selection method using rule-based scoring when AI is unavailable.

    Args:
        json_file_path: Path to the JSON file containing scraped articles

    Returns:
        Dictionary containing the selected article and reasoning
    """
    try:
        # Load articles from JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        if not articles:
            return {"error": "No articles found in the JSON file"}

        # Apply deduplication filter to articles before fallback selection
        filtered_articles = filter_previously_selected(articles)

        if not filtered_articles:
            logging.warning("All articles have been previously selected (fallback)")
            return {
                "error": "All articles have been previously selected",
                "total_articles_found": len(articles),
                "previously_selected": len(articles),
                "selection_method": "fallback_algorithm",
                "suggestion": "Try running the scraper again later for new content"
            }

        # Score articles based on keywords
        scored_articles = []

        for article in filtered_articles:
            score = 0
            title = article['title'].lower()

            # High-value keywords (worth 3 points each)
            high_value_keywords = ['tutorial', 'guide', 'how to', 'step by step', 'complete', 'build', 'create']
            for keyword in high_value_keywords:
                if keyword in title:
                    score += 3

            # Technology keywords (worth 2 points each)
            tech_keywords = ['python', 'javascript', 'react', 'node.js', 'ai', 'machine learning', 'docker', 'kubernetes']
            for keyword in tech_keywords:
                if keyword in title:
                    score += 2

            # Learning keywords (worth 1 point each)
            learning_keywords = ['learn', 'beginner', 'introduction', 'basics', 'fundamentals']
            for keyword in learning_keywords:
                if keyword in title:
                    score += 1

            scored_articles.append((article, score))

        # Sort by score and select the highest
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        best_article = scored_articles[0][0]

        # Add selected article to history to prevent future duplicates
        add_to_upskill_history(best_article)

        result = {
            "selected_article": best_article,
            "ai_reasoning": "Selected using rule-based fallback algorithm based on educational value keywords",
            "total_articles_scraped": len(articles),
            "total_articles_analyzed": len(filtered_articles),
            "previously_selected_filtered": len(articles) - len(filtered_articles),
            "selection_criteria": "Rule-based scoring: tutorial keywords, technology relevance, learning value",
            "selection_method": "fallback_algorithm",
            "deduplication_enabled": True
        }

        # Save the selected article
        with open("../data/ai_selected_upskill_article.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logging.info(f"Fallback selected article: {best_article['title'][:50]}...")
        return result

    except Exception as e:
        logging.error(f"Fallback selection failed: {e}")
        return {"error": f"Both AI and fallback selection failed: {str(e)}"}

def main():
    """
    Main function to demonstrate the upskill articles scraper.
    """
    print("=== Upskill Articles Scraper for CS Students ===")
    print("Scraping educational content from Dev.to, KDnuggets, Medium, and company blogs...")
    print("Focus: Tutorials, guides, best practices, and implementation examples")
    print("Date filter: Last 7 days for broader educational content discovery\n")

    try:
        # Scrape articles
        articles = upskill_articles()

        if articles:
            print(f"Found {len(articles)} relevant upskill articles:\n")

            # Save all articles to JSON
            with open("../data/upskill_articles.json", 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)

            # Display first few articles
            for i, article in enumerate(articles[:5], 1):
                print(f"{i}. {article['title']}")
                print(f"   URL: {article['url']}\n")

            if len(articles) > 5:
                print(f"... and {len(articles) - 5} more articles")

            print(f"../data/\n💾 All articles saved to: upskill_articles.json")

            # AI selection
            print("\n🤖 AI selecting the most valuable learning article...")
            ai_result = select_best_upskill_article()

            if "selected_article" in ai_result:
                print(f"\n⭐ AI SELECTED BEST UPSKILL ARTICLE:")
                print(f"Title: {ai_result['selected_article']['title']}")
                print(f"URL: {ai_result['selected_article']['url']}")
                print(f"\n🧠 AI Reasoning: {ai_result['ai_reasoning']}")

                # Display deduplication statistics
                if ai_result.get('deduplication_enabled'):
                    print(f"\n📊 DEDUPLICATION STATS:")
                    print(f"  • Total articles scraped: {ai_result.get('total_articles_scraped', 'N/A')}")
                    print(f"  • Previously selected (filtered): {ai_result.get('previously_selected_filtered', 0)}")
                    print(f"  • New articles analyzed: {ai_result.get('total_articles_analyzed', 'N/A')}")
                    print(f"  • Selection method: {ai_result.get('selection_method', 'AI')}")

                print(f"../data/\n💾 AI selection saved to: ai_selected_upskill_article.json")
            else:
                print(f"\n❌ AI selection failed: {ai_result.get('error', 'Unknown error')}")

                # Show additional info for deduplication-related failures
                if "previously selected" in ai_result.get('error', '').lower():
                    print(f"  • Total articles found: {ai_result.get('total_articles_found', 'N/A')}")
                    print(f"  • All articles were previously selected")
                    print(f"  • Suggestion: {ai_result.get('suggestion', 'Try again later')}")

        else:
            print("No upskill articles found matching the criteria.")
            print("This could mean:")
            print("  - No educational articles were published in the last 7 days")
            print("  - Articles don't match the upskill keyword filters")
            print("  - Date extraction failed for the articles")

    except Exception as e:
        print(f"Error occurred: {e}")

    # Show deduplication history statistics if available
    if os.path.exists(UPSKILL_HISTORY_FILE):
        try:
            with open(UPSKILL_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            print(f"\n📊 DEDUPLICATION HISTORY STATUS:")
            print(f"  • History entries: {len(history)}")
            print(f"  • Rolling window: {HISTORY_DAYS} days")
            print(f"  • Tracks both titles and URLs")
            print(f"  • History file: {UPSKILL_HISTORY_FILE}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
