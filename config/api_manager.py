#!/usr/bin/env python3
"""
API Manager for Daily Tech Digest Pipeline

Handles API key management, validation, and fallback behavior when APIs are unavailable.

Author: Augment Agent
Date: 2025-01-25
"""

import os
import logging
from typing import Optional, Dict, Any
import json

class APIManager:
    """Manages API keys and provides fallback behavior."""

    def __init__(self):
        self.groq_api_key = self._get_groq_api_key()
        self.api_available = self._validate_api_key()

    def _get_groq_api_key(self) -> Optional[str]:
        """Get Groq API key from environment, config file, or working fallback."""
        # Priority: Environment variable > Config file > Working fallback key
        api_key = os.getenv('GROQ_API_KEY')

        if api_key:
            logging.info("Using Groq API key from environment variable")
            return api_key

        # Try to load from config file
        try:
            if os.path.exists('api_config.json'):
                with open('api_config.json', 'r') as f:
                    config = json.load(f)
                    api_key = config.get('groq_api_key')
                    if api_key and api_key != "your_groq_api_key_here":
                        logging.info("Using Groq API key from config file")
                        return api_key
        except Exception as e:
            logging.warning(f"Could not load API config: {e}")

        # Try to import from centralized config
        try:
            from config import get_groq_api_key
            api_key = get_groq_api_key()
            if api_key:
                logging.info("Using Groq API key from centralized config")
                return api_key
        except ImportError:
            pass

        # Working fallback key
        fallback_key = "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"
        logging.info("Using working fallback API key")
        return fallback_key

    def _validate_api_key(self) -> bool:
        """Validate that the API key works."""
        if not self.groq_api_key:
            return False

        try:
            # Try a simple API call to validate
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)

            # Simple test call
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama3-8b-8192",
                max_tokens=5
            )

            logging.info("✅ Groq API key validated successfully")
            return True

        except Exception as e:
            logging.error(f"❌ Groq API key validation failed: {e}")
            return False

    def is_api_available(self) -> bool:
        """Check if API is available for use."""
        return self.api_available

    def get_api_key(self) -> Optional[str]:
        """Get the API key if available."""
        return self.groq_api_key if self.api_available else None

    def get_client(self):
        """Get a Groq client if API is available."""
        if not self.api_available:
            return None

        try:
            from groq import Groq
            return Groq(api_key=self.groq_api_key)
        except Exception as e:
            logging.error(f"Failed to create Groq client: {e}")
            return None

# Global API manager instance
api_manager = APIManager()

def get_api_manager() -> APIManager:
    """Get the global API manager instance."""
    return api_manager

def ai_select_content(items: list, content_type: str, prompt_template: str) -> Dict[str, Any]:
    """
    Select content using AI if available, otherwise use fallback algorithm.

    Args:
        items: List of items to select from
        content_type: Type of content (tech_news, internship, job, upskill)
        prompt_template: Template for AI prompt

    Returns:
        Dictionary with selected content and metadata
    """
    if not items:
        return {
            "message": f"No {content_type} items to analyze",
            "status": "no_content",
            "selection_method": "none"
        }

    # Try AI selection first
    if api_manager.is_api_available():
        try:
            client = api_manager.get_client()
            if client:
                logging.info(f"Using AI selection for {content_type}")

                # Prepare items for AI
                items_text = "\n".join([f"{i+1}. {item.get('title', 'No title')}" for i, item in enumerate(items)])
                prompt = prompt_template.format(items=items_text, count=len(items))

                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    temperature=0.1,
                    max_tokens=100
                )

                selected_title = response.choices[0].message.content.strip()

                # Find the selected item
                for item in items:
                    if item.get('title', '').strip() == selected_title.strip():
                        return {
                            "title": item.get('title', ''),
                            "url": item.get('url', ''),
                            "company": item.get('company', '') if 'company' in item else None,
                            "selection_method": "ai",
                            "ai_reasoning": f"Selected by AI from {len(items)} options",
                            "timestamp": "2025-01-25T22:47:00"
                        }

                # If AI selection didn't match, fall back to algorithm
                logging.warning(f"AI selection '{selected_title}' didn't match any item, using fallback")

        except Exception as e:
            logging.error(f"AI selection failed for {content_type}: {e}")

    # Fallback to rule-based selection
    logging.info(f"Using fallback selection for {content_type}")

    try:
        from fallback_selector import fallback_select_best, create_fallback_selection_result

        best_item = fallback_select_best(items, content_type)
        if best_item:
            return create_fallback_selection_result(best_item, content_type, len(items))
        else:
            return {
                "message": f"No suitable {content_type} found",
                "status": "no_content",
                "selection_method": "fallback_failed"
            }

    except Exception as e:
        logging.error(f"Fallback selection failed for {content_type}: {e}")

        # Last resort - pick the first item
        if items:
            first_item = items[0]
            return {
                "title": first_item.get('title', ''),
                "url": first_item.get('url', ''),
                "company": first_item.get('company', '') if 'company' in first_item else None,
                "selection_method": "first_item_fallback",
                "selection_reasoning": f"Emergency fallback - selected first of {len(items)} items",
                "timestamp": "2025-01-25T22:47:00"
            }

        return {
            "message": f"All selection methods failed for {content_type}",
            "status": "selection_failed",
            "selection_method": "failed"
        }

def create_api_config_template():
    """Create a template API configuration file."""
    config = {
        "groq_api_key": "your_groq_api_key_here",
        "note": "Set your Groq API key here or use GROQ_API_KEY environment variable"
    }

    try:
        with open('api_config_template.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("📝 Created api_config_template.json")
        print("   Copy this to api_config.json and add your API key")
    except Exception as e:
        print(f"❌ Failed to create config template: {e}")

if __name__ == "__main__":
    print("🔑 API MANAGER STATUS")
    print("-" * 40)

    manager = get_api_manager()

    print(f"🤖 API Available: {'✅ Yes' if manager.is_api_available() else '❌ No'}")
    print(f"🔐 API Key: {'✅ Set' if manager.groq_api_key else '❌ Not Set'}")

    if not manager.is_api_available():
        print("\n💡 TO ENABLE AI SELECTION:")
        print("1. Set GROQ_API_KEY environment variable, OR")
        print("2. Create api_config.json with your API key")
        print("3. Get a free API key from: https://console.groq.com/")

        create_api_config_template()

    print(f"\n📋 FALLBACK BEHAVIOR:")
    print("• When AI is unavailable, rule-based selection is used")
    print("• Scrapers will continue to work without AI")
    print("• Quality may be lower but pipeline remains functional")
