#!/usr/bin/env python3
"""
Daily Tech Digest Aggregator

This script consolidates AI-selected content from all four existing scrapers:
1. Tech News (ai_selected_article.json)
2. Internships (selected_internship.json)
3. Jobs/Placements (selected_job.json)
4. Upskill Articles (ai_selected_upskill_article.json)

Creates a unified daily_tech_digest.json with organized content and metadata.

Author: Augment Agent
Date: 2025-01-25
"""

import json
import logging
import os
import datetime
from typing import Dict, List, Optional, Any
from groq import Groq

# Import configuration
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.config import get_groq_api_key, OUTPUT_FILES
    GROQ_API_KEY = get_groq_api_key()
    OUTPUT_FILE = OUTPUT_FILES['daily_digest']
except ImportError:
    # Fallback configuration if config.py is not available
    GROQ_API_KEY = "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"
    OUTPUT_FILE = "../data/daily_tech_digest.json"

# Input file mappings
INPUT_FILES = {
    "tech_news": {
        "file": "../data/ai_selected_article.json",
        "display_name": "Tech News",
        "description": "AI-selected tech news article of the day"
    },
    "internships": {
        "file": "../data/selected_internship.json",
        "display_name": "Internships",
        "description": "AI-selected best internship opportunity"
    },
    "jobs": {
        "file": "../data/selected_job.json",
        "display_name": "Jobs/Placements",
        "description": "AI-selected best job opportunity for fresh graduates"
    },
    "upskill_articles": {
        "file": "../data/ai_selected_upskill_article.json",
        "display_name": "Upskill Articles",
        "description": "AI-selected best learning resource for skill development"
    }
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/daily_tech_aggregator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_json_file(file_path: str) -> Optional[Dict]:
    """
    Load and parse a JSON file with error handling.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the JSON data, or None if failed
    """
    try:
        if not os.path.exists(file_path):
            logging.warning(f"File not found: {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logging.info(f"Successfully loaded: {file_path}")
        return data

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return None

def validate_content(data: Dict, content_type: str) -> bool:
    """
    Validate that the loaded content has the expected structure.

    Args:
        data: The loaded JSON data
        content_type: Type of content (tech_news, internships, etc.)

    Returns:
        True if valid, False otherwise
    """
    if not data:
        return False

    # Flexible validation - check for any meaningful content
    if content_type == "tech_news":
        # Accept either full AI structure or simple article structure
        return ("selected_article" in data and "ai_reasoning" in data) or ("title" in data and "url" in data)
    elif content_type == "internships":
        # Accept either full AI structure or simple internship structure
        return ("selected_internship" in data and "ai_reasoning" in data) or ("title" in data and ("company" in data or "url" in data))
    elif content_type == "jobs":
        # Accept either full AI structure or simple job structure
        return ("selected_job" in data and "ai_reasoning" in data) or ("title" in data and ("company" in data or "url" in data))
    elif content_type == "upskill_articles":
        # Accept either full AI structure or simple article structure
        return ("selected_article" in data and "ai_reasoning" in data) or ("title" in data and "url" in data)

    return True

def get_content_summary(data: Dict, content_type: str) -> Dict:
    """
    Extract summary information from the content.

    Args:
        data: The loaded JSON data
        content_type: Type of content

    Returns:
        Dictionary with summary information
    """
    summary = {
        "status": "success",
        "has_content": True,
        "title": "Unknown",
        "source": "Unknown"
    }

    try:
        if content_type == "tech_news":
            if "selected_article" in data:
                article = data["selected_article"]
                summary["title"] = article.get("title", "Unknown")
            else:
                # Simple format
                summary["title"] = data.get("title", "Unknown")
            summary["source"] = "Tech News Scraper"

        elif content_type == "internships":
            if "selected_internship" in data:
                internship = data["selected_internship"]
                summary["title"] = internship.get("title", "Unknown")
            else:
                # Simple format
                summary["title"] = data.get("title", "Unknown")
            summary["source"] = "Internship Scraper"

        elif content_type == "jobs":
            if "selected_job" in data:
                job = data["selected_job"]
                summary["title"] = job.get("title", "Unknown")
            else:
                # Simple format
                summary["title"] = data.get("title", "Unknown")
            summary["source"] = "Job Scraper"

        elif content_type == "upskill_articles":
            if "selected_article" in data:
                article = data["selected_article"]
                summary["title"] = article.get("title", "Unknown")
            else:
                # Simple format
                summary["title"] = data.get("title", "Unknown")
            summary["source"] = "Upskill Articles Scraper"

    except Exception as e:
        logging.warning(f"Error extracting summary for {content_type}: {e}")
        summary["status"] = "error"

    return summary

def create_daily_digest() -> Dict:
    """
    Create the unified daily tech digest by aggregating all scraper outputs.

    Returns:
        Dictionary containing the clean daily digest with only essential fields
    """
    logging.info("Starting daily tech digest aggregation...")

    # Initialize the clean digest structure
    digest = {
        "tech_news": None,
        "internships": None,
        "jobs": None,
        "upskill_articles": None
    }

    # Process each input file
    for content_type, file_info in INPUT_FILES.items():
        file_path = file_info["file"]
        display_name = file_info["display_name"]

        logging.info(f"Processing {display_name} from {file_path}...")

        # Load the file
        data = load_json_file(file_path)

        # Validate and process content
        if data and validate_content(data, content_type):
            # Check if this is a fallback/no-content file
            if data.get("status") == "no_content" or data.get("message", "").startswith("No suitable content found"):
                digest[content_type] = "No suitable content found"
                logging.info(f"⚠️  {display_name}: No content available")
            else:
                # Extract only essential fields based on content type
                clean_content = extract_essential_fields(data, content_type)

                if clean_content:
                    digest[content_type] = clean_content
                    logging.info(f"✅ Successfully processed {display_name}")
                else:
                    digest[content_type] = "No suitable content found"
                    logging.warning(f"❌ Could not extract essential fields from {display_name}")
        else:
            digest[content_type] = "No suitable content found"
            logging.warning(f"❌ Failed to process {display_name}")

    # Count successful sources (excluding "No suitable content found" messages)
    successful_count = sum(1 for content in digest.values() if content is not None and content != "No suitable content found")
    logging.info(f"Aggregation completed: {successful_count}/{len(INPUT_FILES)} sources successful")

    # Create the final structured digest
    final_digest = {
        "daily_tech_digest": {
            "metadata": {
                "generated_at": datetime.datetime.now().isoformat(),
                "successful_sources": f"{successful_count}/{len(INPUT_FILES)}",
                "source_files": {
                    "tech_news": INPUT_FILES["tech_news"]["file"],
                    "internships": INPUT_FILES["internships"]["file"],
                    "jobs": INPUT_FILES["jobs"]["file"],
                    "upskill_articles": INPUT_FILES["upskill_articles"]["file"]
                }
            },
            "summary": {
                content_type: {
                    "count": 1 if content != "No suitable content found" and content is not None else 0,
                    "status": "success" if content != "No suitable content found" and content is not None else "no_content"
                }
                for content_type, content in digest.items()
            },
            "content": digest
        }
    }

    return final_digest

def extract_essential_fields(data: Dict, content_type: str) -> Optional[Dict]:
    """
    Extract only the essential fields for each content type.

    Args:
        data: The loaded JSON data
        content_type: Type of content (tech_news, internships, etc.)

    Returns:
        Dictionary with only essential fields, or None if extraction failed
    """
    try:
        if content_type == "tech_news":
            if "selected_article" in data:
                article = data["selected_article"]
                return {
                    "title": article.get("title", ""),
                    "url": article.get("url", "")
                }
            else:
                # Simple format
                return {
                    "title": data.get("title", ""),
                    "url": data.get("url", "")
                }

        elif content_type == "internships":
            if "selected_internship" in data:
                internship = data["selected_internship"]
                return {
                    "title": internship.get("title", ""),
                    "company": internship.get("company", ""),
                    "url": internship.get("url", "")
                }
            else:
                # Simple format
                return {
                    "title": data.get("title", ""),
                    "company": data.get("company", ""),
                    "url": data.get("url", "")
                }

        elif content_type == "jobs":
            if "selected_job" in data:
                job = data["selected_job"]
                return {
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "url": job.get("url", "")
                }
            else:
                # Simple format
                return {
                    "title": data.get("title", ""),
                    "company": data.get("company", ""),
                    "url": data.get("url", "")
                }

        elif content_type == "upskill_articles":
            if "selected_article" in data:
                article = data["selected_article"]
                return {
                    "title": article.get("title", ""),
                    "url": article.get("url", "")
                }
            else:
                # Simple format
                return {
                    "title": data.get("title", ""),
                    "url": data.get("url", "")
                }

    except Exception as e:
        logging.error(f"Error extracting essential fields for {content_type}: {e}")
        return None

    return None

def save_daily_digest(digest: Dict) -> bool:
    """
    Save the daily digest to the output file.

    Args:
        digest: The complete daily digest dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(digest, f, indent=2, ensure_ascii=False)

        logging.info(f"✅ Daily digest saved to: {OUTPUT_FILE}")
        return True

    except Exception as e:
        logging.error(f"❌ Failed to save daily digest: {e}")
        return False

def generate_digest_summary(digest: Dict) -> str:
    """
    Generate a human-readable summary of the clean daily digest.

    Args:
        digest: The complete daily digest dictionary (with metadata structure)

    Returns:
        Formatted summary string
    """
    # Extract the actual content from the structured digest
    if "daily_tech_digest" in digest:
        content_digest = digest["daily_tech_digest"]["content"]
        metadata = digest["daily_tech_digest"]["metadata"]
        current_time = metadata["generated_at"][:19]
        successful_sources = metadata["successful_sources"]
    else:
        # Fallback for old format
        content_digest = digest
        current_time = datetime.datetime.now().isoformat()[:19]
        successful_count = sum(1 for content in digest.values() if content is not None and content != "No suitable content found")
        successful_sources = f"{successful_count}/{len(digest)}"

    summary_text = f"""
📅 DAILY TECH DIGEST SUMMARY
Generated: {current_time}
═══════════════════════════════════════════════════════════

📊 AGGREGATION STATUS:
✅ Successful: {successful_sources} sources

📋 CONTENT OVERVIEW:
"""

    content_order = ["tech_news", "internships", "jobs", "upskill_articles"]
    display_names = {
        "tech_news": "Tech News",
        "internships": "Internships",
        "jobs": "Jobs/Placements",
        "upskill_articles": "Upskill Articles"
    }

    for content_type in content_order:
        content = content_digest.get(content_type)
        status_icon = "✅" if content and content != "No suitable content found" else "❌"
        display_name = display_names[content_type]

        summary_text += f"\n{status_icon} {display_name}: "

        if content and content != "No suitable content found":
            if isinstance(content, dict):
                title = content.get('title', 'Unknown')[:60] + "..." if len(content.get('title', '')) > 60 else content.get('title', 'Unknown')
                summary_text += f"Available\n   📰 {title}"
            else:
                summary_text += "Available"
        else:
            summary_text += "No suitable content found"

    summary_text += f"\n\n💾 Clean digest saved to: {OUTPUT_FILE}"
    summary_text += "\n═══════════════════════════════════════════════════════════"

    return summary_text

def main():
    """
    Main function to create and save the daily tech digest.
    """
    print("🔄 DAILY TECH DIGEST AGGREGATOR")
    print("=" * 50)
    print("Consolidating AI-selected content from all scrapers...")

    try:
        # Create the digest
        digest = create_daily_digest()

        # Save to file
        if save_daily_digest(digest):
            # Generate and display summary
            summary = generate_digest_summary(digest)
            print(summary)

            return digest
        else:
            print("❌ Failed to save daily digest")
            return None

    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        print(f"❌ Fatal error: {e}")
        return None

if __name__ == "__main__":
    main()
