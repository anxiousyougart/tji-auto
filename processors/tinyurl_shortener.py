#!/usr/bin/env python3


import json
import logging
import time
import datetime
import os
import sys
import requests
from typing import Dict, List, Optional

# Import configuration
try:
    from ..config.config import TINYURL_CONFIG, URL_ALIAS_FORMATS
except ImportError:
    # Fallback configuration if config.py is not available
    TINYURL_CONFIG = {
        'api_key': os.getenv("TINYURL_API_KEY"),
        'api_endpoint': 'https://api.tinyurl.com/create',
        'domain': 'tinyurl.com',
        'input_file': '../data/daily_tech_digest.json',
        'output_file': '../data/shortened_urls_digest.json',
        'log_file': '../data/tinyurl_shortener.log',
        'request_timeout': 30,
        'max_retries_per_url': 3,
        'delay_between_requests': 1,
        'rate_limit_delay': 5,
        'counter_file': '../data/tinyurl_run_counter.json'
    }
    URL_ALIAS_FORMATS = {
        'tech_news': 'tech-news-tji-{}',
        'internships': 'internship-tji-{}',
        'jobs': 'placement-update-tji-{}',
        'upskill_articles': 'upskill-tji-{}'
    }

    TINYURL_COUNTER_FILE = '../data/tinyurl_run_counter.json'

# Configure logging with UTF-8 encoding to handle emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(TINYURL_CONFIG['log_file'], encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TinyURLShortener:
    """
    TinyURL shortening automation class using TinyURL API.
    """

    def __init__(self):
        """Initialize the TinyURL shortener with configuration."""
        self.config = TINYURL_CONFIG
        self.alias_formats = URL_ALIAS_FORMATS
        # Load or initialize the global run counter
        self.run_number = self.load_run_counter()

        # Initialize statistics
        self.stats = {
            'total_urls': 0,
            'successful_shortenings': 0,
            'failed_shortenings': 0,
            'skipped_urls': 0
        }

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['log_file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def load_run_counter(self) -> int:
        """
        Load the persistent run counter from file.

        Returns:
            Current run number (starts from 1)
        """
        counter_file = self.config['counter_file']

        try:
            if os.path.exists(counter_file):
                with open(counter_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    current_run = data.get('current_run', 1)
                    logging.info(f"Loaded run counter: {current_run}")
                    return current_run
            else:
                logging.info("No counter file found, starting with run 1")
                return 1

        except Exception as e:
            logging.warning(f"Error loading run counter: {e}, starting with run 1")
            return 1

    def save_run_counter(self, run_number: int):
        """
        Save the current run counter to file.

        Args:
            run_number: Current run number to save
        """
        counter_file = self.config['counter_file']

        try:
            counter_data = {
                'current_run': run_number,
                'last_updated': datetime.datetime.now().isoformat(),
                'total_runs': run_number
            }

            with open(counter_file, 'w', encoding='utf-8') as f:
                json.dump(counter_data, f, indent=2, ensure_ascii=False)

            logging.info(f"Saved run counter: {run_number}")

        except Exception as e:
            logging.error(f"Error saving run counter: {e}")

    def increment_run_counter(self):
        """
        Increment the run counter for the next execution.
        """
        next_run = self.run_number + 1
        self.save_run_counter(next_run)
        logging.info(f"Incremented run counter from {self.run_number} to {next_run}")

    def load_input_data(self) -> Optional[Dict]:
        """
        Load and parse the daily_tech_digest.json file.

        Returns:
            Dict: Parsed JSON data or None if failed
        """
        input_file = self.config['input_file']

        if not os.path.exists(input_file):
            logging.error(f"Input file not found: {input_file}")
            return None

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logging.info(f"Successfully loaded input data from {input_file}")
            return data

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {input_file}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error reading {input_file}: {e}")
            return None

    def extract_urls_from_data(self, data: Dict) -> List[Dict]:
        """
        Extract URLs from the daily tech digest data structure.

        Args:
            data: Parsed JSON data from daily_tech_digest.json

        Returns:
            List of dictionaries containing URL info
        """
        urls_to_process = []

        # Handle nested structure (daily_tech_digest.content)
        if 'daily_tech_digest' in data and 'content' in data['daily_tech_digest']:
            content = data['daily_tech_digest']['content']
        else:
            # Fallback for flat structure
            content = data

        for category, category_data in content.items():
            if category not in self.alias_formats:
                logging.warning(f"Unknown category: {category}, skipping")
                continue

            if not category_data or category_data == "No suitable content found":
                logging.info(f"No content found for category: {category}")
                continue

            # Extract URL from category data
            url = None
            title = "Unknown"
            company = None
            
            if isinstance(category_data, dict):
                url = category_data.get('url')
                title = category_data.get('title', 'Unknown')
                company = category_data.get('company')
            elif isinstance(category_data, str):
                # Handle case where category_data is just a URL string
                url = category_data

            if url and url.startswith(('http://', 'https://')):
                urls_to_process.append({
                    'category': category,
                    'original_url': url,
                    'title': title,
                    'company': company
                })
                logging.info(f"Found URL for {category}: {url[:50]}...")
            else:
                logging.warning(f"No valid URL found for category: {category}")
                self.stats['skipped_urls'] += 1

        self.stats['total_urls'] = len(urls_to_process)
        logging.info(f"Extracted {len(urls_to_process)} URLs for processing")
        return urls_to_process

    def generate_alias(self, category: str) -> str:
        """
        Generate a category-specific alias using the consistent run number.

        Args:
            category: Category name (tech_news, internships, etc.)

        Returns:
            Generated alias string (e.g., tech-news-tji-1)
        """
        if category not in self.alias_formats:
            return f"tji-{category}-{self.run_number}"

        alias_format = self.alias_formats[category]
        alias = alias_format.format(self.run_number)

        return alias

    def shorten_single_url(self, url: str, alias: str, max_retries: int = None) -> Optional[str]:
        """
        Shorten a single URL using TinyURL API with custom alias.

        Args:
            url: The URL to shorten
            alias: Custom alias for the shortened URL
            max_retries: Maximum number of retry attempts

        Returns:
            Shortened URL with custom alias or None if failed
        """
        if max_retries is None:
            max_retries = self.config['max_retries_per_url']

        headers = {
            'Authorization': f"Bearer {self.config['api_key']}",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        payload = {
            'url': url,
            'domain': self.config['domain'],
            'alias': alias
        }

        for attempt in range(max_retries + 1):
            try:
                logging.info(f"Shortening URL (attempt {attempt + 1}/{max_retries + 1}): {url[:50]}...")
                logging.info(f"Using alias: {alias}")

                response = requests.post(
                    self.config['api_endpoint'],
                    headers=headers,
                    json=payload,
                    timeout=self.config['request_timeout']
                )

                if response.status_code == 200:
                    result = response.json()
                    shortened_url = result.get('data', {}).get('tiny_url')

                    if shortened_url:
                        logging.info(f"Successfully shortened URL: {shortened_url}")
                        return shortened_url
                    else:
                        logging.error(f"No shortened URL in response: {result}")

                elif response.status_code == 422:
                    # Alias might already exist, try with a modified alias
                    timestamp = int(time.time()) % 10000
                    modified_alias = f"{alias}_{timestamp}"
                    logging.warning(f"Alias '{alias}' already exists, trying with '{modified_alias}'")
                    payload['alias'] = modified_alias
                    alias = modified_alias  # Update the alias variable for next attempts
                    continue

                elif response.status_code == 429:
                    # Rate limited
                    logging.warning(f"Rate limited, waiting {self.config['rate_limit_delay']} seconds")
                    time.sleep(self.config['rate_limit_delay'])
                    continue

                else:
                    logging.error(f"HTTP error {response.status_code}: {response.text}")
                    # Log the full response for debugging
                    try:
                        error_data = response.json()
                        logging.error(f"API error details: {error_data}")
                    except:
                        logging.error(f"Raw response: {response.text}")

            except requests.exceptions.Timeout:
                logging.warning(f"Timeout for {url} (attempt {attempt + 1}/{max_retries + 1})")
            except requests.exceptions.ConnectionError:
                logging.warning(f"Connection error for {url} (attempt {attempt + 1}/{max_retries + 1})")
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request error for {url}: {e} (attempt {attempt + 1}/{max_retries + 1})")
            except Exception as e:
                logging.error(f"Unexpected error shortening {url}: {e}")

            if attempt < max_retries:
                time.sleep(2 ** attempt)  # Exponential backoff

        logging.error(f"Failed to shorten {url} after {max_retries + 1} attempts")
        return None

    def process_urls(self, urls_to_process: List[Dict]) -> List[Dict]:
        """
        Process all URLs and shorten them.

        Args:
            urls_to_process: List of URL dictionaries to process

        Returns:
            List of processed URL dictionaries with shortened URLs
        """
        processed_urls = []

        for i, url_info in enumerate(urls_to_process, 1):
            category = url_info['category']
            original_url = url_info['original_url']
            title = url_info['title']
            company = url_info['company']

            logging.info(f"Processing URL {i}/{len(urls_to_process)} ({category})")

            # Generate alias for tracking purposes
            alias = self.generate_alias(category)

            # Shorten URL with custom alias
            shortened_url = self.shorten_single_url(original_url, alias)

            # Create simplified result entry with only essential fields
            if shortened_url:
                result_entry = {
                    'title': title,
                    'shortened_url': shortened_url
                }

                # Add company field for internships and jobs
                if company and category in ['internships', 'jobs']:
                    result_entry['company'] = company

                self.stats['successful_shortenings'] += 1
                logging.info(f"✅ Successfully processed {category}: {shortened_url}")
            else:
                # Still track failed URLs for statistics but don't include in output
                result_entry = None
                self.stats['failed_shortenings'] += 1
                logging.error(f"❌ Failed to process {category}: {original_url}")

            if result_entry:
                processed_urls.append(result_entry)

            # Add delay between requests to avoid rate limiting
            if i < len(urls_to_process):
                time.sleep(self.config['delay_between_requests'])

        return processed_urls

    def create_output_data(self, processed_urls: List[Dict]) -> Dict:
        """
        Create the output data structure with shortened URLs.

        Args:
            processed_urls: List of processed URLs with shortened versions

        Returns:
            Complete output data structure
        """
        # Calculate success rate
        total_processed = self.stats['successful_shortenings'] + self.stats['failed_shortenings']
        success_rate = (self.stats['successful_shortenings'] / total_processed * 100) if total_processed > 0 else 0

        # Create metadata
        metadata = {
            'generated_at': datetime.datetime.now().isoformat(),
            'source_file': self.config['input_file'],
            'total_urls_processed': self.stats['total_urls'],
            'successful_shortenings': self.stats['successful_shortenings'],
            'failed_shortenings': self.stats['failed_shortenings'],
            'skipped_urls': self.stats['skipped_urls'],
            'success_rate': f"{success_rate:.1f}%"
        }

        # Create simplified output structure - just the shortened URLs
        output_data = {
            'shortened_urls_digest': {
                'metadata': metadata,
                'content': processed_urls
            }
        }

        return output_data

    def save_output_data(self, output_data: Dict) -> bool:
        """
        Save the output data to the specified file.

        Args:
            output_data: Complete output data structure

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config['output_file'], 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logging.info(f"✅ Output saved to: {self.config['output_file']}")
            return True

        except Exception as e:
            logging.error(f"❌ Failed to save output: {e}")
            return False

    def generate_summary(self, output_data: Dict) -> str:
        """
        Generate a human-readable summary of the shortening process.

        Args:
            output_data: Complete output data structure

        Returns:
            Formatted summary string
        """
        metadata = output_data['shortened_urls_digest']['metadata']
        content = output_data['shortened_urls_digest']['content']

        summary_text = f"""
🔗 TINYURL SHORTENING SUMMARY - RUN #{self.run_number}
Generated: {metadata['generated_at'][:19]}
═══════════════════════════════════════════════════════════

📊 PROCESSING STATISTICS:
✅ Successful: {metadata['successful_shortenings']}/{metadata['total_urls_processed']} URLs
❌ Failed: {metadata['failed_shortenings']}/{metadata['total_urls_processed']} URLs
⏭️  Skipped: {metadata['skipped_urls']} URLs (no content)
📈 Success Rate: {metadata['success_rate']}

📋 SHORTENED URLS (Run #{self.run_number}):"""

        for i, item in enumerate(content, 1):
            title = item['title'][:50] + "..." if len(item['title']) > 50 else item['title']
            shortened_url = item['shortened_url']

            summary_text += f"\n{i}. {title}"
            if 'company' in item:
                summary_text += f" - {item['company']}"
            summary_text += f"\n   🔗 {shortened_url}"

        summary_text += f"\n\n💾 Output saved to: {self.config['output_file']}"
        summary_text += "\n═══════════════════════════════════════════════════════════"

        return summary_text

    def run(self) -> bool:
        """
        Run the complete URL shortening process.

        Returns:
            True if successful, False otherwise
        """
        logging.info("Starting TinyURL shortening process...")

        # Load input data
        original_data = self.load_input_data()
        if not original_data:
            return False

        # Extract URLs
        urls_to_process = self.extract_urls_from_data(original_data)
        if not urls_to_process:
            logging.warning("No URLs found to process")
            return False

        # Process URLs
        processed_urls = self.process_urls(urls_to_process)

        # Create output data
        output_data = self.create_output_data(processed_urls)

        # Save output
        if not self.save_output_data(output_data):
            return False

        # Generate and display summary
        summary = self.generate_summary(output_data)
        print(summary)

        # Increment run counter for next execution
        self.increment_run_counter()

        return True


def main():
    """
    Main function to run the TinyURL shortening process.
    """
    print("🔗 TINYURL SHORTENING AUTOMATION")
    print("=" * 50)
    print("Shortening URLs from daily_tech_digest.json using TinyURL API...")

    try:
        shortener = TinyURLShortener()
        success = shortener.run()

        if success:
            print(f"\n💡 Next steps:")
            print(f"  • View results: cat {TINYURL_CONFIG['output_file']}")
            print(f"  • Check logs: cat {TINYURL_CONFIG['log_file']}")
            print(f"  • Integration: Use shortened URLs in your applications")
        else:
            print(f"\n🔧 Troubleshooting:")
            print(f"  • Check input file exists: {TINYURL_CONFIG['input_file']}")
            print(f"  • Verify API key is valid")
            print(f"  • Review logs: cat {TINYURL_CONFIG['log_file']}")
            print(f"  • Check internet connection")

        return 0 if success else 1

    except KeyboardInterrupt:
        print(f"\n⏹️  Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Process crashed: {e}")
        logging.error(f"Process crashed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
