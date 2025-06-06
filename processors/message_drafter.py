#!/usr/bin/env python3
"""
TJI Message Drafter

Creates professional, engaging messages using tech news, internships, jobs, and upskill content
with AI-enhanced formatting and daily pro tips.

Author: Augment Agent
Date: 2025-01-25
"""

import json
import logging
import os
import re
from typing import Dict, Optional, Any
from groq import Groq

# Import configuration
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.config import get_groq_api_key
    GROQ_API_KEY = get_groq_api_key()
except ImportError:
    GROQ_API_KEY = "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"

# Configuration
INPUT_FILE = "../data/shortened_urls_digest.json"
COUNTER_FILE = "../data/tinyurl_run_counter.json"
OUTPUT_FILE = "../data/tji_daily_message.json"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_title(title: str) -> str:
    """Clean title by removing timestamps and extra formatting."""
    if not title:
        return ""
    
    # Remove common timestamp patterns
    title = re.sub(r'\n.*?\d+\s+(minutes?|hours?|days?)\s+ago.*$', '', title, flags=re.DOTALL)
    title = re.sub(r'\n.*?Read now.*$', '', title, flags=re.DOTALL)
    title = re.sub(r'\n.*?\w{3}\s+\d{1,2},\s+\d{4}.*$', '', title, flags=re.DOTALL)
    title = re.sub(r'\n.*?Learn.*$', '', title, flags=re.DOTALL)
    
    # Clean up extra whitespace and newlines
    title = re.sub(r'\n+', ' ', title)
    title = re.sub(r'\s+', ' ', title)
    title = title.strip()
    
    return title

def extract_run_number_from_urls(content: Dict) -> int:
    """Extract the run number from the actual URLs in the content."""
    # Look for any URL with tji-{number} pattern
    for category_data in content.values():
        if category_data and 'url' in category_data:
            url = category_data['url']
            # Extract number from patterns like tech-news-tji-3, internship-tji-3, etc.
            match = re.search(r'tji-(\d+)', url)
            if match:
                return int(match.group(1))

    # Fallback to counter file if no URLs found
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
                return data.get('current_run', 1)
    except Exception as e:
        logging.warning(f"Could not read counter file: {e}")

    return 1

def load_shortened_urls_data() -> Dict:
    """Load data from shortened URLs digest file."""
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {INPUT_FILE}: {e}")
        return {}

def extract_content_by_category(data: Dict) -> Dict:
    """Extract content organized by category."""
    content = {
        'tech_news': None,
        'internship': None,
        'placement': None,
        'upskill': None
    }
    
    if not data or 'shortened_urls_digest' not in data:
        return content
    
    items = data['shortened_urls_digest'].get('content', [])
    
    for item in items:
        url = item.get('shortened_url', '')
        title = clean_title(item.get('title', ''))
        company = item.get('company', '')
        
        if 'tech-news-tji' in url:
            content['tech_news'] = {'title': title, 'url': url}
        elif 'internship-tji' in url:
            content['internship'] = {'title': title, 'company': company, 'url': url}
        elif 'placement-update-tji' in url:
            content['placement'] = {'title': title, 'company': company, 'url': url}
        elif 'upskill-tji' in url:
            content['upskill'] = {'title': title, 'url': url}
    
    return content

def get_pro_tip_from_groq() -> str:
    """Get a daily pro tip using Groq API."""
    try:
        api_key = os.getenv('GROQ_API_KEY', GROQ_API_KEY)
        if not api_key:
            return "Focus on building one small coding habit daily - consistency beats intensity in skill development."

        client = Groq(api_key=api_key)

        prompt = """You are TJI Pro Tip Assistant, a wise, concise, and inspiring mentor for engineering students. Every day, you share one small but powerful tip that helps them become better at coding, learning, career preparation, interviews, resume building, habit development, networking, and navigating college life.

Your tone is professional, clear, and motivational — like a senior who has seen the struggles and wants to guide juniors with no fluff, just real actionable advice.

Focus on these topics:
- Smart ways to learn DSA and programming
- Productivity hacks and study techniques
- Resume & LinkedIn optimization
- Interview preparation advice (tech + behavioral)
- Personal branding, networking, and soft skills
- College project, internship, and career strategy
- Mental health, burnout, and habit building

The tip should:
- Be 1–3 sentences max
- Give a fresh perspective or lesser-known insight
- Be immediately useful or mindset-shifting
- Avoid clichés like "work hard", "stay focused"
- Do not include introductory phrases like "Here is your daily tip:" or "Pro tip:"

Provide only the tip content, no extra text or formatting."""

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            max_tokens=100,
            temperature=0.8
        )

        tip = response.choices[0].message.content.strip()

        # Clean up any introductory phrases that might slip through
        tip = tip.replace("Here is your daily tip:", "").strip()
        tip = tip.replace("Pro tip:", "").strip()
        tip = tip.replace("Daily tip:", "").strip()
        tip = tip.replace("Tip:", "").strip()

        return tip

    except Exception as e:
        logging.warning(f"Failed to get pro tip from Groq: {e}")
        return "Focus on building one small coding habit daily - consistency beats intensity in skill development."

def enhance_message_with_groq(content: Dict, run_number: int, pro_tip: str) -> str:
    """Use Groq to enhance and format the complete message."""
    try:
        api_key = os.getenv('GROQ_API_KEY', GROQ_API_KEY)
        if not api_key:
            return create_fallback_message(content, run_number, pro_tip)
        
        client = Groq(api_key=api_key)

        # Build the exact content with real URLs in the required format
        sections = []
        sections.append(f"*#TJI {run_number}*")
        sections.append("")

        if content['tech_news']:
            sections.extend([
                "*TECH NEWS:*",
                "",
                content['tech_news']['title'],
                f"Read more at:\n{content['tech_news']['url']}",
                ""
            ])

        if content['internship']:
            sections.extend([
                "*INTERNSHIP UPDATE:*",
                "",
                f"{content['internship']['title']} at {content['internship']['company']}",
                f"Apply now at:\n{content['internship']['url']}",
                ""
            ])

        if content['placement']:
            sections.extend([
                "*PLACEMENT UPDATE:*",
                "",
                f"{content['placement']['title']} at {content['placement']['company']}",
                f"Apply now at:\n{content['placement']['url']}",
                ""
            ])

        sections.extend([
            "*PRO TIP:*",
            "",
            pro_tip,
            ""
        ])

        if content['upskill']:
            sections.extend([
                "*UPSKILL:*",
                "",
                content['upskill']['title'],
                f"\n{content['upskill']['url']}"
            ])

        base_message = "\n".join(sections)

        prompt = f"""Enhance this daily tech digest message to make it more engaging and professional while following the EXACT format:

{base_message}

CRITICAL FORMATTING REQUIREMENTS:
- Keep the exact same format: section header, blank line, description line, call-to-action with URL on next line
- Keep ALL URLs exactly as they are - DO NOT change any URLs
- Make descriptions CONCISE, TO-THE-POINT, and engaging (maximum 1-2 sentences, no fluff)
- Keep titles SHORT and PUNCHY - avoid long explanatory text
- For TECH NEWS: Keep "Read more at:" then URL on the NEXT line
- For INTERNSHIP/PLACEMENT: Keep "Apply now at:" then URL on the NEXT line
- For UPSKILL: Put URL directly on the next line after title (no call-to-action)
- For PRO TIP: Do not add introductory phrases like "Here is your daily tip:" - just provide the tip content directly
- URLs must always be on the line immediately after the call-to-action (separated by \\n)
- DO NOT repeat any sentences or content
- Keep it professional, no emojis
- PRIORITIZE BREVITY - the message should be quick to read
- Return only the enhanced message starting with "*#TJI {run_number}*"
- Use \\n for line breaks exactly as shown with blank line after each section header
- Can add extra introductory text or concluding remarks. but keep it short and concise.
- Ensure each piece of content appears only once"""

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            max_tokens=500,
            temperature=0.7
        )

        result = response.choices[0].message.content.strip()

        # Remove any introductory text that Groq might add
        if result.startswith("Here is"):
            lines = result.split('\n')
            # Find the line that starts with *#TJI
            for i, line in enumerate(lines):
                if line.strip().startswith("*#TJI"):
                    result = '\n'.join(lines[i:])
                    break

        # Clean up any extra \n characters that Groq might add
        result = result.replace('\\n\n', '\n')
        result = result.replace('\\n', '')

        # Split into lines for processing
        lines = result.split('\n')
        cleaned_lines = []
        seen_content = set()  # Track content to avoid duplicates

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines with just ** or similar artifacts
            if line in ['**', '*', '***', '']:
                i += 1
                continue

            # Handle section headers
            if line.startswith('*') and line.endswith('*') and line.count('*') == 2:
                cleaned_lines.append(line)
                cleaned_lines.append('')  # Add blank line after header
                i += 1
                continue

            # Clean up introductory phrases
            if line.startswith("Here is your daily tip:") or line.startswith("Daily tip:") or line.startswith("Pro tip:"):
                line = line.replace("Here is your daily tip:", "").replace("Daily tip:", "").replace("Pro tip:", "").strip()

            # Check for duplicates (ignore very short lines and URLs)
            if len(line) > 20 and not line.startswith('http') and line in seen_content:
                i += 1
                continue

            # Add content to seen set if it's substantial
            if len(line) > 20 and not line.startswith('http'):
                seen_content.add(line)

            # Add the line
            if line:
                cleaned_lines.append(line)

            i += 1

        # Ensure proper formatting: \n\n after headers, \n before URLs
        final_lines = []
        for i, line in enumerate(cleaned_lines):
            final_lines.append(line)

            # If current line is a URL and previous line is not empty, ensure single line break
            if line.startswith('http') and i > 0 and cleaned_lines[i-1].strip():
                # URL is already properly positioned
                pass
            # If next line is a URL, ensure single line break
            elif i + 1 < len(cleaned_lines) and cleaned_lines[i + 1].startswith('http'):
                # Don't add extra line break before URL
                pass
            # If current line is section header, blank line is already added
            elif line.startswith('*') and line.endswith('*') and line.count('*') == 2:
                pass
            # Add line break between sections
            elif i + 1 < len(cleaned_lines) and cleaned_lines[i + 1].startswith('*') and cleaned_lines[i + 1].endswith('*'):
                final_lines.append('')

        result = '\n'.join(final_lines)

        return result
        
    except Exception as e:
        logging.warning(f"Failed to enhance message with Groq: {e}")
        return create_fallback_message(content, run_number, pro_tip)

def create_fallback_message(content: Dict, run_number: int, pro_tip: str) -> str:
    """Create a fallback message without AI enhancement."""
    message_parts = [f"*#TJI {run_number}*", ""]

    # Tech News
    if content['tech_news']:
        # Keep title concise - take first part if too long
        title = content['tech_news']['title']
        if len(title) > 80:
            title = title.split('.')[0] if '.' in title else title[:80] + "..."

        message_parts.extend([
            "*TECH NEWS:*",
            "",
            title,
            f"Read more at:\n{content['tech_news']['url']}",
            ""
        ])

    # Internship
    if content['internship']:
        message_parts.extend([
            "*INTERNSHIP UPDATE:*",
            "",
            f"{content['internship']['title']} at {content['internship']['company']}",
            f"Apply now at:\n{content['internship']['url']}",
            ""
        ])

    # Placement
    if content['placement']:
        message_parts.extend([
            "*PLACEMENT UPDATE:*",
            "",
            f"{content['placement']['title']} at {content['placement']['company']}",
            f"Apply now at:\n{content['placement']['url']}",
            ""
        ])

    # Pro Tip
    message_parts.extend([
        "*PRO TIP:*",
        "",
        pro_tip,
        ""
    ])

    # Upskill
    if content['upskill']:
        message_parts.extend([
            "*UPSKILL:*",
            "",
            content['upskill']['title'],
            f"\n{content['upskill']['url']}"
        ])

    return "\n".join(message_parts)

def main():
    """Main function to draft the TJI message."""
    logging.info("Starting TJI message drafting...")

    # Load shortened URLs data
    data = load_shortened_urls_data()
    if not data:
        logging.error("No data available to draft message")
        return

    # Extract content by category
    content = extract_content_by_category(data)
    logging.info(f"Extracted content: {sum(1 for v in content.values() if v)} categories available")

    # Get run number from actual URLs (this ensures consistency)
    run_number = extract_run_number_from_urls(content)
    logging.info(f"Using run number from URLs: {run_number}")

    # Get pro tip
    pro_tip = get_pro_tip_from_groq()
    logging.info("Generated pro tip")

    # Create enhanced message
    message = enhance_message_with_groq(content, run_number, pro_tip)
    
    # Save to JSON file
    output_data = {"drafted_message": message}
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Message saved to {OUTPUT_FILE}")
        
        # Also print to console
        print("\n" + "="*60)
        print("TJI DAILY MESSAGE DRAFT")
        print("="*60)
        print(message)
        print("="*60)
        print(f"\nMessage saved to: {OUTPUT_FILE}")
        
    except Exception as e:
        logging.error(f"Failed to save message: {e}")
        print("\nGenerated Message:")
        print(message)

if __name__ == "__main__":
    main()
