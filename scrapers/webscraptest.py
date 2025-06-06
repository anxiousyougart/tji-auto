import requests
from bs4 import BeautifulSoup
import time
import random
import re
import datetime
import logging
import json
import os
from urllib.parse import urljoin, urlparse
from dateutil import parser as date_parser
from groq import Groq

# Configure logging for error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Enhanced keywords for filtering technical innovation and advancement articles
INCLUDE_KEYWORDS = [
    # Technical Innovation and Breakthroughs
    "breakthrough", "innovation", "advancement", "discovery", "invention", "development",
    "new technology", "cutting-edge", "state-of-the-art", "revolutionary", "groundbreaking",
    "first-of-its-kind", "next-generation", "novel approach", "pioneering", "disruptive",

    # AI and Machine Learning Developments
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning", "neural network",
    "gpt", "llm", "large language model", "chatbot", "generative ai", "ai model", "ai tool",
    "ai breakthrough", "new model", "model release", "ai research", "ai system", "ai algorithm",
    "transformer", "diffusion", "computer vision", "nlp", "natural language processing",

    # Software and Hardware Releases
    "launch", "launches", "released", "announces", "unveils", "introduces", "debuts",
    "new product", "product launch", "software release", "hardware announcement",
    "technical preview", "upgrade", "update", "version", "beta release", "alpha release",

    # Engineering and Technical Developments
    "engineering", "algorithm", "software", "hardware", "computing", "processor", "chip",
    "semiconductor", "quantum", "quantum computing", "quantum processor", "quantum algorithm",
    "robotics", "automation", "autonomous", "self-driving", "computer vision", "sensor",
    "architecture", "framework", "platform", "infrastructure", "performance improvement",

    # Scientific and Research Advances
    "research", "science", "scientific", "study", "experiment", "prototype", "proof-of-concept",
    "technical paper", "research paper", "scientific breakthrough", "laboratory", "testing",
    "validation", "benchmark", "efficiency gain", "optimization", "scalability",

    # Developer Tools and Programming
    "programming language", "compiler", "interpreter", "framework", "library", "api", "sdk",
    "development tool", "debugging", "testing framework", "code analysis", "open source",
    "github", "repository", "version control", "continuous integration", "devops"
]

# Enhanced keywords for filtering out non-technical content
EXCLUDE_KEYWORDS = [
    # Business and Financial News
    "stock", "shares", "market", "trading", "investment", "investor", "funding", "valuation",
    "ipo", "acquisition", "merger", "buyout", "revenue", "profit", "earnings", "financial",
    "quarterly results", "annual report", "shareholder", "dividend", "market cap",

    # Personnel and Management Changes
    "ceo", "cfo", "cto", "executive", "leadership", "management", "board", "director",
    "appointment", "resignation", "hiring", "fired", "layoffs", "restructuring", "reorganization",
    "personnel", "staff", "employee", "workforce", "human resources",

    # Opinion and Editorial Content
    "opinion", "editorial", "commentary", "analysis", "perspective", "thoughts", "review",
    "criticism", "critique", "debate", "discussion", "interview", "podcast", "video blog",
    "opinion piece", "editorial board", "guest post", "contributor", "columnist",
    "my take", "what i think", "personal", "diary", "journal", "blog post",

    # Marketing and PR Content
    "marketing", "advertising", "campaign", "promotion", "brand", "branding", "partnership",
    "collaboration", "sponsorship", "deal", "agreement", "contract", "terms", "conditions",
    "press release", "pr", "public relations", "media kit", "announcement only",

    # General Industry Commentary
    "industry trends", "market analysis", "industry report", "survey", "poll", "prediction",
    "forecast", "outlook", "trend", "comparison", "ranking", "list", "top 10", "best of",
    "worst of", "guide", "how-to", "tutorial", "tips", "advice", "recommendation",

    # Legal and Regulatory
    "lawsuit", "litigation", "legal", "court", "judge", "ruling", "regulation", "policy",
    "law", "compliance", "privacy policy", "terms of service", "gdpr", "regulatory",
    "government", "senate", "congress", "bill", "legislation",

    # Speculative and Rumor Content
    "rumor", "leak", "allegedly", "sources say", "reportedly", "speculation", "unconfirmed",
    "insider", "anonymous", "whispers", "gossip", "hearsay", "claims", "suggests",

    # Non-technical content types
    "podcast", "interview", "webinar", "event", "conference", "session", "keynote",
    "roundtable", "panel", "discussion", "q&a", "ama", "workshop", "seminar", "meetup"
]

def is_relevant_article(article, strict=False):
    """
    Determine if an article is relevant based on keyword matching.

    Args:
        article (dict): Article dictionary containing title and other fields
        strict (bool): If True, requires multiple include keywords to match

    Returns:
        bool: True if the article is relevant, False otherwise
    """
    # Extract the title and convert to lowercase for case-insensitive matching
    title = article.get('title', '').lower()

    # Skip empty titles or placeholder titles
    if not title or title == "no title found" or title == "most popular":
        return False

    # Check for include keywords with word boundary handling
    include_matches = []
    for keyword in INCLUDE_KEYWORDS:
        # Use word boundary pattern to avoid partial matches
        # e.g., "ai" should match "ai" but not "paid" or "main"
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, title):
            include_matches.append(keyword)

    # Check for exclude keywords with word boundary handling
    exclude_match = False
    for keyword in EXCLUDE_KEYWORDS:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, title):
            exclude_match = True
            break

    # Determine relevance based on matches and strictness
    if strict:
        # Strict mode: require at least 2 include keywords and no exclude keywords
        is_relevant = len(include_matches) >= 2 and not exclude_match
        return is_relevant
    else:
        # Normal mode: require at least 1 include keyword and no exclude keywords
        is_relevant = len(include_matches) >= 1 and not exclude_match
        return is_relevant

def _extract_date(article, url=None):
    """
    Extract the publication date from an article element.

    Args:
        article (bs4.element.Tag): The article element
        url (str): The source URL for website-specific date extraction

    Returns:
        datetime.datetime or None: The publication date if found, None otherwise
    """
    # Website-specific date selectors
    date_selectors = [
        'time', '.date', '.time', '.datetime', '.published', '.pubdate',
        '[datetime]', '[pubdate]', '.timestamp', '.post-date', '.entry-date',
        'meta[property="article:published_time"]', 'meta[itemprop="datePublished"]'
    ]

    # Add website-specific selectors based on URL
    if url:
        if 'devblogs.microsoft.com' in url:
            date_selectors.extend(['.post-date', '.entry-date', '.published-date'])
        elif 'arstechnica.com' in url:
            date_selectors.extend(['.byline time', '.post-meta time', '.article-date'])
        elif 'analyticsinsight.net' in url:
            date_selectors.extend(['.post-meta .date', '.entry-meta .date'])
        elif 'innovationnewsnetwork.com' in url:
            date_selectors.extend(['.article-meta time', '.post-date'])
        elif 'techxplore.com' in url:
            date_selectors.extend(['.article-byline time', '.news-date'])
        elif 'openai.com' in url:
            date_selectors.extend(['.post-meta time', '.article-date'])
        elif 'linkedin.com' in url:
            date_selectors.extend(['.blog-post-meta time', '.post-date'])

    # Try to find date using selectors
    for selector in date_selectors:
        date_elements = article.select(selector)
        if not date_elements and selector.startswith('meta'):
            # Try to find meta tags in the whole document
            date_elements = article.find_all(selector)

        for date_element in date_elements:
            # Check for datetime attribute
            if date_element.has_attr('datetime'):
                try:
                    return date_parser.parse(date_element['datetime'])
                except (ValueError, TypeError):
                    pass

            # Check for content attribute (meta tags)
            if date_element.has_attr('content'):
                try:
                    return date_parser.parse(date_element['content'])
                except (ValueError, TypeError):
                    pass

            # Try to parse the text content
            try:
                date_text = date_element.get_text().strip()
                if date_text:
                    return date_parser.parse(date_text)
            except (ValueError, TypeError):
                pass

    # Try to find date patterns in the article text
    article_text = article.get_text()

    # Common date patterns
    date_patterns = [
        # ISO format: 2023-05-23
        r'\d{4}-\d{2}-\d{2}',
        # Common formats: May 23, 2023 or 23 May 2023
        r'(?:\d{1,2}\s+)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}',
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}',
        # MM/DD/YYYY or DD/MM/YYYY
        r'\d{1,2}/\d{1,2}/\d{4}',
        # Relative time: "2 hours ago", "yesterday", etc.
        r'(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago',
        r'yesterday|today'
    ]

    for pattern in date_patterns:
        match = re.search(pattern, article_text)
        if match:
            try:
                date_str = match.group(0)

                # Handle relative time
                if 'ago' in date_str:
                    num, unit = re.findall(r'(\d+)\s+(second|minute|hour|day|week|month|year)', date_str)[0]
                    num = int(num)
                    now = datetime.datetime.now()

                    if unit == 'second':
                        return now - datetime.timedelta(seconds=num)
                    elif unit == 'minute':
                        return now - datetime.timedelta(minutes=num)
                    elif unit == 'hour':
                        return now - datetime.timedelta(hours=num)
                    elif unit == 'day':
                        return now - datetime.timedelta(days=num)
                    elif unit == 'week':
                        return now - datetime.timedelta(weeks=num)
                    elif unit == 'month':
                        # Approximate a month as 30 days
                        return now - datetime.timedelta(days=30*num)
                    elif unit == 'year':
                        # Approximate a year as 365 days
                        return now - datetime.timedelta(days=365*num)
                elif date_str == 'yesterday':
                    return datetime.datetime.now() - datetime.timedelta(days=1)
                elif date_str == 'today':
                    return datetime.datetime.now()
                else:
                    return date_parser.parse(date_str)
            except (ValueError, TypeError, IndexError):
                pass

    # If we couldn't find a date, return None
    return None


def _is_today(article_date):
    """
    Check if an article's publication date is today.

    Args:
        article_date (datetime.datetime or None): The article's publication date

    Returns:
        bool: True if the article is from today, False otherwise
    """
    if article_date is None:
        return False

    # Make sure we're comparing naive datetimes
    if article_date.tzinfo is not None:
        article_date = article_date.replace(tzinfo=None)

    # Same day only
    now = datetime.datetime.now()
    return (article_date.year == now.year and
            article_date.month == now.month and
            article_date.day == now.day)


def _is_recent_48hours(article_date):
    """
    Check if an article's publication date is within the last 48 hours (strict filtering).

    This implements strict 48-hour date filtering to ensure only the most recent
    tech news articles are captured. Articles older than 48 hours from current
    execution time are rejected.

    Args:
        article_date (datetime.datetime or None): The article's publication date

    Returns:
        bool: True if the article is from the last 48 hours, False otherwise
    """
    if article_date is None:
        # Reject articles with no date - strict filtering
        return False

    # Make sure we're comparing naive datetimes
    if article_date.tzinfo is not None:
        article_date = article_date.replace(tzinfo=None)

    # Strict 48-hour filtering from current execution time
    now = datetime.datetime.now()
    cutoff_time = now - datetime.timedelta(hours=48)

    # Article must be published within the last 48 hours
    is_recent = article_date >= cutoff_time

    if not is_recent:
        logging.debug(f"Article filtered out - published {article_date}, cutoff {cutoff_time}")

    return is_recent

# Duplicate prevention system
HISTORY_FILE = "../data/tech_news_history.json"
HISTORY_DAYS = 30  # Keep 30 days of history

def load_article_history():
    """
    Load the history of previously selected tech news articles.

    Returns:
        dict: Dictionary with article titles and URLs as keys, and selection dates as values
    """
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
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
                save_article_history(cleaned_history)

            logging.info(f"Loaded {len(cleaned_history)} articles from history (cleaned from {len(history)})")
            return cleaned_history
        else:
            logging.info("No history file found, starting fresh")
            return {}
    except Exception as e:
        logging.error(f"Error loading article history: {e}")
        return {}

def save_article_history(history):
    """
    Save the article history to file.

    Args:
        history (dict): Dictionary with article titles/URLs and selection dates
    """
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        logging.debug(f"Saved {len(history)} articles to history")
    except Exception as e:
        logging.error(f"Error saving article history: {e}")

def add_to_history(article):
    """
    Add an article to the selection history.

    Args:
        article (dict): Article with 'title' and 'url' keys
    """
    try:
        history = load_article_history()
        current_time = datetime.datetime.now().isoformat()

        # Use both title and URL as keys for duplicate detection
        title_key = f"title:{article['title'].lower().strip()}"
        url_key = f"url:{article['url'].lower().strip()}"

        history[title_key] = current_time
        history[url_key] = current_time

        save_article_history(history)
        logging.info(f"Added article to history: {article['title'][:50]}...")
    except Exception as e:
        logging.error(f"Error adding article to history: {e}")

def is_duplicate_article(article):
    """
    Check if an article is a duplicate of a previously selected article.

    Args:
        article (dict): Article with 'title' and 'url' keys

    Returns:
        bool: True if the article is a duplicate, False otherwise
    """
    try:
        history = load_article_history()

        # Check both title and URL for duplicates
        title_key = f"title:{article['title'].lower().strip()}"
        url_key = f"url:{article['url'].lower().strip()}"

        is_duplicate = title_key in history or url_key in history

        if is_duplicate:
            logging.debug(f"Duplicate article detected: {article['title'][:50]}...")

        return is_duplicate
    except Exception as e:
        logging.error(f"Error checking for duplicate article: {e}")
        return False

def filter_duplicate_articles(articles):
    """
    Filter out articles that have been previously selected.

    Args:
        articles (list): List of article dictionaries

    Returns:
        tuple: (filtered_articles, duplicate_count)
    """
    filtered_articles = []
    duplicate_count = 0

    for article in articles:
        if not is_duplicate_article(article):
            filtered_articles.append(article)
        else:
            duplicate_count += 1

    logging.info(f"Filtered out {duplicate_count} duplicate articles, {len(filtered_articles)} remaining")
    return filtered_articles, duplicate_count

def tech_news(urls):
    """
    Scrape tech news articles with enhanced filtering for technical innovation.

    This function implements strict 48-hour date filtering to ensure only the most
    recent tech news articles are captured. Focuses exclusively on technical innovation
    and advancement articles while filtering out business news, opinion pieces, and
    previously selected articles.

    Filtering Pipeline:
    1. 48-hour date filtering (strict - rejects articles without dates)
    2. Technical innovation keyword filtering
    3. Duplicate prevention (30-day rolling history)
    4. AI selection for best technical advancement

    Args:
        urls (list): List of URLs to scrape

    Returns:
        list: JSON-serializable list of dictionaries with 'title' and 'url' keys
              containing technical innovation articles from the last 48 hours
    """
    all_articles = []

    # Initialize filtering statistics
    stats = {
        'total_scraped': 0,
        'date_filtered': 0,
        'keyword_filtered': 0,
        'duplicate_filtered': 0,
        'final_count': 0
    }

    for url in urls:
        try:
            logging.info(f"Scraping: {url}")

            # Add a random delay to avoid overloading the server
            delay = random.uniform(1, 3)
            time.sleep(delay)

            # Fetch the page with enhanced error handling
            try:
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                })
                response.raise_for_status()
            except requests.exceptions.Timeout:
                logging.warning(f"Timeout while fetching {url}")
                continue
            except requests.exceptions.ConnectionError:
                logging.warning(f"Connection error while fetching {url}")
                continue
            except requests.exceptions.HTTPError as e:
                logging.warning(f"HTTP error {e.response.status_code} while fetching {url}")
                continue
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request error while fetching {url}: {e}")
                continue

            # Parse the HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Website-specific article detection
            article_elements = []

            if 'news.ycombinator.com' in url:
                # Hacker News uses .athing class for articles
                article_elements = soup.select('.athing')
            elif 'techcrunch.com' in url:
                # TechCrunch uses .post class for articles
                article_elements = soup.select('.post')
            elif 'theverge.com' in url:
                # The Verge uses content cards
                article_elements = soup.select('.duet--content-cards--content-card')
            elif 'scitechdaily.com' in url:
                # SciTechDaily uses entry class
                article_elements = soup.select('article.entry, .entry, .post')
            elif 'devblogs.microsoft.com' in url:
                # Microsoft DevBlogs uses article tags
                article_elements = soup.select('article, .post-item, .entry')
            elif 'arstechnica.com' in url:
                # Ars Technica uses article tags with specific classes
                article_elements = soup.select('article, .article, .listing-item')
            elif 'analyticsinsight.net' in url:
                # Analytics Insight uses post classes
                article_elements = soup.select('.post, article, .news-item')
            elif 'innovationnewsnetwork.com' in url:
                # Innovation News Network uses article and post classes
                article_elements = soup.select('article, .post, .news-article')
            elif 'techxplore.com' in url:
                # TechXplore uses article tags
                article_elements = soup.select('article, .article-item, .news-item')
            elif 'openai.com' in url:
                # OpenAI news uses article or post classes
                article_elements = soup.select('article, .post, .news-item, .blog-post')
            elif 'linkedin.com' in url:
                # LinkedIn blog uses article tags
                article_elements = soup.select('article, .post, .blog-post')
            else:
                # Generic approach for other sites
                article_elements = soup.select('article')

            # If no articles found with specific selectors, try generic approach
            if not article_elements:
                article_elements = soup.find_all(['article', 'div', 'section'],
                    class_=lambda c: c and any(x in c for x in ['article', 'post', 'entry', 'item']))

                # If still no articles found, try to find divs with links and headers
                if not article_elements:
                    for div in soup.find_all('div'):
                        if div.find(['h1', 'h2', 'h3', 'h4']) and div.find('a'):
                            article_elements.append(div)

            base_url = urlparse(url)
            base_domain = f"{base_url.scheme}://{base_url.netloc}"

            for article in article_elements:
                try:
                    # Website-specific title extraction
                    title_element = None

                    if 'news.ycombinator.com' in url:
                        # Hacker News specific title extraction
                        title_element = article.select_one('.titleline > a, .title a')
                    elif 'techcrunch.com' in url:
                        # TechCrunch specific - uses h3 a for titles
                        title_element = article.select_one('h3 a, h2 a')
                    elif 'theverge.com' in url:
                        # The Verge specific - titles are in links within the card
                        title_element = article.select_one('a[href*="/"]')
                        # Filter out comment links and other non-article links
                        if title_element and ('#comments' in title_element.get('href', '') or
                                            title_element.get_text().strip() in ['', 'Comments', 'Comment Icon Bubble']):
                            # Look for the main article link
                            all_links = article.select('a[href*="/"]')
                            for link in all_links:
                                if '#comments' not in link.get('href', '') and link.get_text().strip():
                                    title_element = link
                                    break
                    elif 'scitechdaily.com' in url:
                        # SciTechDaily specific
                        title_element = article.select_one('h2.entry-title a, h1.entry-title a, .entry-title a')
                    elif 'devblogs.microsoft.com' in url:
                        # Microsoft DevBlogs specific
                        title_element = article.select_one('h2 a, h3 a, .entry-title a, .post-title a')
                    elif 'arstechnica.com' in url:
                        # Ars Technica specific
                        title_element = article.select_one('h2 a, h3 a, .headline a, .article-title a')
                    elif 'analyticsinsight.net' in url:
                        # Analytics Insight specific
                        title_element = article.select_one('h2 a, h3 a, .post-title a, .entry-title a')
                    elif 'innovationnewsnetwork.com' in url:
                        # Innovation News Network specific
                        title_element = article.select_one('h2 a, h3 a, .article-title a, .post-title a')
                    elif 'techxplore.com' in url:
                        # TechXplore specific
                        title_element = article.select_one('h2 a, h3 a, .article-title a, .news-title a')
                    elif 'openai.com' in url:
                        # OpenAI specific
                        title_element = article.select_one('h2 a, h3 a, .post-title a, .article-title a')
                    elif 'linkedin.com' in url:
                        # LinkedIn blog specific
                        title_element = article.select_one('h2 a, h3 a, .post-title a, .article-title a')

                    # Generic fallback
                    if not title_element:
                        title_element = article.select_one('h2 a, h3 a, h1 a, .title a, .headline a')
                    if not title_element:
                        title_element = article.find(['h1', 'h2', 'h3', 'h4'])

                    if not title_element:
                        continue

                    title = title_element.get_text().strip()
                    if not title or title == "No title found":
                        continue

                    # Extract URL with improved logic
                    link = None

                    # Method 1: Try to get URL from the title element if it's a link
                    if title_element.name == 'a' and title_element.has_attr('href'):
                        link = title_element['href']

                    # Method 2: Look for link in title's parent or nearby elements
                    if not link:
                        # Check if title is inside a link
                        parent_link = title_element.find_parent('a')
                        if parent_link and parent_link.has_attr('href'):
                            link = parent_link['href']

                    # Method 3: Website-specific URL extraction
                    if not link:
                        # Hacker News specific
                        if 'news.ycombinator.com' in url:
                            title_link = article.select_one('.titleline > a')
                            if title_link and title_link.has_attr('href'):
                                link = title_link['href']

                        # TechCrunch specific
                        elif 'techcrunch.com' in url:
                            tc_link = article.select_one('h3 a, h2 a')
                            if tc_link and tc_link.has_attr('href'):
                                link = tc_link['href']

                        # The Verge specific
                        elif 'theverge.com' in url:
                            # Find the main article link (not comments)
                            verge_links = article.select('a[href*="/"]')
                            for verge_link in verge_links:
                                if ('#comments' not in verge_link.get('href', '') and
                                    verge_link.get_text().strip() and
                                    verge_link.has_attr('href')):
                                    link = verge_link['href']
                                    break

                        # Microsoft DevBlogs specific
                        elif 'devblogs.microsoft.com' in url:
                            ms_link = article.select_one('h2 a, h3 a, .entry-title a')
                            if ms_link and ms_link.has_attr('href'):
                                link = ms_link['href']

                        # Ars Technica specific
                        elif 'arstechnica.com' in url:
                            ars_link = article.select_one('h2 a, h3 a, .headline a')
                            if ars_link and ars_link.has_attr('href'):
                                link = ars_link['href']

                        # Analytics Insight specific
                        elif 'analyticsinsight.net' in url:
                            ai_link = article.select_one('h2 a, h3 a, .post-title a')
                            if ai_link and ai_link.has_attr('href'):
                                link = ai_link['href']

                        # Innovation News Network specific
                        elif 'innovationnewsnetwork.com' in url:
                            inn_link = article.select_one('h2 a, h3 a, .article-title a')
                            if inn_link and inn_link.has_attr('href'):
                                link = inn_link['href']

                        # TechXplore specific
                        elif 'techxplore.com' in url:
                            tx_link = article.select_one('h2 a, h3 a, .article-title a')
                            if tx_link and tx_link.has_attr('href'):
                                link = tx_link['href']

                        # OpenAI specific
                        elif 'openai.com' in url:
                            oai_link = article.select_one('h2 a, h3 a, .post-title a')
                            if oai_link and oai_link.has_attr('href'):
                                link = oai_link['href']

                        # LinkedIn blog specific
                        elif 'linkedin.com' in url:
                            li_link = article.select_one('h2 a, h3 a, .post-title a')
                            if li_link and li_link.has_attr('href'):
                                link = li_link['href']

                    # Method 4: Generic fallback - find any link that contains title text
                    if not link:
                        all_links = article.find_all('a', href=True)
                        for a_tag in all_links:
                            link_text = a_tag.get_text().strip().lower()
                            if title.lower() in link_text or link_text in title.lower():
                                link = a_tag['href']
                                break

                    # Method 5: Last resort - get the first meaningful link
                    if not link:
                        all_links = article.find_all('a', href=True)
                        for a_tag in all_links:
                            href = a_tag['href']
                            # Skip internal/navigation links
                            if href and not href.startswith('#') and not href.startswith('javascript:'):
                                link = href
                                break

                    if not link:
                        continue

                    # Make sure the link is absolute
                    if not link.startswith(('http://', 'https://')):
                        link = urljoin(base_domain, link)

                    # Extract publication date
                    pub_date = _extract_date(article, url)
                    stats['total_scraped'] += 1

                    # Apply strict 48-hour date filter
                    if _is_recent_48hours(pub_date):
                        # Check if article is relevant for technical innovation
                        article_dict = {'title': title, 'url': link}
                        if is_relevant_article(article_dict, strict=True):
                            all_articles.append({
                                'title': title,
                                'url': link
                            })
                            logging.info(f"Found relevant technical article: {title[:50]}...")
                        else:
                            stats['keyword_filtered'] += 1
                    else:
                        stats['date_filtered'] += 1

                except Exception as e:
                    # Skip articles that cause parsing errors
                    logging.debug(f"Error parsing article from {url}: {e}")
                    continue

            logging.info(f"Completed scraping {url} - found {len([a for a in all_articles if url in a.get('url', '')])} relevant articles")

        except Exception as e:
            # Skip URLs that cause errors
            logging.error(f"Failed to scrape {url}: {e}")
            continue

    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)

    # Apply duplicate prevention filter
    filtered_articles, duplicate_count = filter_duplicate_articles(unique_articles)
    stats['duplicate_filtered'] = duplicate_count
    stats['final_count'] = len(filtered_articles)

    # Log comprehensive filtering statistics
    logging.info("=== TECH NEWS FILTERING STATISTICS ===")
    logging.info(f"Total articles scraped: {stats['total_scraped']}")
    logging.info(f"Filtered by date (48-hour): {stats['date_filtered']}")
    logging.info(f"Filtered by keywords: {stats['keyword_filtered']}")
    logging.info(f"Filtered as duplicates: {stats['duplicate_filtered']}")
    logging.info(f"Final articles count: {stats['final_count']}")
    logging.info(f"Overall filter rate: {((stats['total_scraped'] - stats['final_count']) / max(stats['total_scraped'], 1) * 100):.1f}%")
    logging.info("=====================================")

    return filtered_articles


def select_best_article(json_file_path="../data/todays_tech_news.json", api_key=None):
    """
    Use Groq's AI to select the most significant technical innovation article.

    Enhanced AI selection focusing on concrete technical innovations and technological
    advancements. The AI prioritizes articles about practical technical details over
    high-level announcements and provides explicit reasoning about technical significance.

    Args:
        json_file_path (str): Path to the JSON file containing scraped articles
        api_key (str): Groq API key (can be overridden with environment variable)

    Returns:
        dict: Selected article with title, url, and detailed AI reasoning about
              technical significance, or None if error
    """
    try:
        # Get API key with robust fallback
        groq_api_key = None

        # Priority: Parameter > Environment > Centralized config > Working fallback
        if api_key:
            groq_api_key = api_key
        else:
            groq_api_key = os.getenv('GROQ_API_KEY')

        if not groq_api_key:
            try:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                from config.config import get_groq_api_key
                groq_api_key = get_groq_api_key()
            except ImportError:
                pass

        if not groq_api_key:
            # Working fallback key
            groq_api_key = "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"

        if not groq_api_key:
            logging.error("No API key available for AI selection")
            return None

        # Read articles from JSON file
        if not os.path.exists(json_file_path):
            logging.warning(f"JSON file {json_file_path} not found")
            return None

        with open(json_file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        if not articles:
            logging.warning("No articles found in JSON file")
            return None

        logging.info(f"AI analyzing {len(articles)} articles for best selection...")

        # Initialize Groq client
        client = Groq(api_key=groq_api_key)

        # Prepare article list for AI analysis
        article_list = []
        for i, article in enumerate(articles, 1):
            article_list.append(f"{i}. {article['title']}")

        articles_text = "\n".join(article_list)

        # Enhanced AI prompt for technical innovation focus
        prompt = f"""You are a technical innovation analyst specializing in identifying significant technological advancements. Analyze these tech news articles and select the ONE article that represents the most significant TECHNICAL INNOVATION or TECHNOLOGICAL ADVANCEMENT.

PRIORITIZE articles about:
1. **Concrete Technical Breakthroughs**: New algorithms, architectures, or technical approaches
2. **Engineering Innovations**: Novel hardware designs, software frameworks, or system architectures
3. **Scientific Advances**: Research breakthroughs with practical technical applications
4. **Technical Product Launches**: New tools, platforms, or technologies with technical depth
5. **Performance Improvements**: Significant technical optimizations or efficiency gains

AVOID articles about:
- Business announcements without technical details
- High-level marketing announcements
- Personnel changes or corporate news
- Opinion pieces or industry commentary
- General trend discussions

Articles to analyze:
{articles_text}

Select the article that represents the most significant technical development and explain WHY it represents a major technical advancement. Focus on the concrete technical innovation, not business impact.

Respond in this format:
SELECTED: [exact article title]
REASONING: [2-3 sentences explaining the specific technical innovation and why it's significant]"""

        # Call Groq API
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-8b-8192",  # Using Llama 3 8B model
                temperature=0.1,  # Low temperature for consistent selection
                max_tokens=200
            )

            ai_response = response.choices[0].message.content.strip()
            logging.info(f"AI response received: {ai_response[:100]}...")

            # Parse the enhanced AI response format
            selected_title = None
            ai_reasoning = "Selected by AI as most significant technical innovation"

            if "SELECTED:" in ai_response and "REASONING:" in ai_response:
                # Parse structured response
                lines = ai_response.split('\n')
                for line in lines:
                    if line.startswith("SELECTED:"):
                        selected_title = line.replace("SELECTED:", "").strip()
                    elif line.startswith("REASONING:"):
                        ai_reasoning = line.replace("REASONING:", "").strip()
            else:
                # Fallback to simple parsing
                selected_title = ai_response.split('\n')[0].strip()

            if not selected_title:
                logging.warning("Could not parse AI selection")
                selected_title = articles[0]['title']
                ai_reasoning = "Fallback selection (parsing failed)"

            logging.info(f"AI selected article: {selected_title[:50]}...")

            # Find the matching article
            selected_article = None
            for article in articles:
                if article['title'].strip() == selected_title.strip():
                    selected_article = article.copy()
                    selected_article['ai_reasoning'] = ai_reasoning
                    break

            # If exact match not found, try partial matching
            if not selected_article:
                for article in articles:
                    if selected_title.lower() in article['title'].lower() or article['title'].lower() in selected_title.lower():
                        selected_article = article.copy()
                        selected_article['ai_reasoning'] = ai_reasoning + " (partial match)"
                        logging.info(f"Used partial matching for article selection")
                        break

            if not selected_article:
                logging.warning(f"AI selected title not found in articles: {selected_title}")
                # Fallback: return first article
                selected_article = articles[0].copy()
                selected_article['ai_reasoning'] = "Fallback selection (AI choice not found)"

            # Add selected article to history to prevent future duplicates
            add_to_history(selected_article)

            return selected_article

        except Exception as api_error:
            logging.error(f"Groq API error: {api_error}")
            return None

    except Exception as e:
        logging.error(f"Error in AI article selection: {e}")
        return None

