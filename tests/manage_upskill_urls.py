#!/usr/bin/env python3
"""
URL Management Tool for Upskill Articles Scraper

This script provides an easy way to manage URLs for the upskill articles scraper.
You can add new URLs, view current URLs, and manage categories.

Usage:
    python manage_upskill_urls.py
"""

import json
import os
from typing import Dict, List

CONFIG_FILE = "../data/upskill_urls_config.json"

def load_urls() -> Dict:
    """Load URLs from configuration file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Configuration file {CONFIG_FILE} not found. Creating new one...")
            return {}
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

def save_urls(urls: Dict) -> bool:
    """Save URLs to configuration file."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=2, ensure_ascii=False)
        print(f"✅ URLs saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error saving URLs: {e}")
        return False

def display_urls(urls: Dict):
    """Display all URLs organized by category."""
    print("\n📚 CURRENT UPSKILL URLS:")
    print("=" * 60)
    
    for category, url_list in urls.items():
        print(f"\n🔗 {category.upper().replace('_', ' ')} ({len(url_list)} URLs):")
        for i, url in enumerate(url_list, 1):
            print(f"  {i}. {url}")
    
    total_urls = sum(len(url_list) for url_list in urls.values())
    print(f"\n📊 Total: {total_urls} URLs across {len(urls)} categories")
    print("=" * 60)

def add_url(urls: Dict) -> Dict:
    """Add a new URL to a category."""
    print("\n➕ ADD NEW URL")
    print("-" * 30)
    
    # Show available categories
    print("Available categories:")
    categories = list(urls.keys())
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category}")
    print(f"  {len(categories) + 1}. Create new category")
    
    try:
        choice = input(f"\nSelect category (1-{len(categories) + 1}): ").strip()
        
        if choice == str(len(categories) + 1):
            # Create new category
            new_category = input("Enter new category name: ").strip().lower().replace(' ', '_')
            if new_category and new_category not in urls:
                urls[new_category] = []
                category = new_category
                print(f"✅ Created new category: {category}")
            else:
                print("❌ Invalid category name or category already exists")
                return urls
        else:
            # Use existing category
            category_index = int(choice) - 1
            if 0 <= category_index < len(categories):
                category = categories[category_index]
            else:
                print("❌ Invalid category selection")
                return urls
        
        # Add URL
        new_url = input("Enter URL to add: ").strip()
        if new_url:
            if new_url not in urls[category]:
                urls[category].append(new_url)
                print(f"✅ Added URL to {category}: {new_url}")
            else:
                print(f"⚠️  URL already exists in {category}")
        else:
            print("❌ Invalid URL")
    
    except (ValueError, IndexError):
        print("❌ Invalid input")
    
    return urls

def remove_url(urls: Dict) -> Dict:
    """Remove a URL from a category."""
    print("\n➖ REMOVE URL")
    print("-" * 30)
    
    # Show categories
    categories = list(urls.keys())
    if not categories:
        print("No categories available")
        return urls
    
    print("Select category:")
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category} ({len(urls[category])} URLs)")
    
    try:
        choice = input(f"Select category (1-{len(categories)}): ").strip()
        category_index = int(choice) - 1
        
        if 0 <= category_index < len(categories):
            category = categories[category_index]
            url_list = urls[category]
            
            if not url_list:
                print(f"No URLs in category {category}")
                return urls
            
            print(f"\nURLs in {category}:")
            for i, url in enumerate(url_list, 1):
                print(f"  {i}. {url}")
            
            url_choice = input(f"Select URL to remove (1-{len(url_list)}): ").strip()
            url_index = int(url_choice) - 1
            
            if 0 <= url_index < len(url_list):
                removed_url = url_list.pop(url_index)
                print(f"✅ Removed URL: {removed_url}")
            else:
                print("❌ Invalid URL selection")
        else:
            print("❌ Invalid category selection")
    
    except (ValueError, IndexError):
        print("❌ Invalid input")
    
    return urls

def main():
    """Main function for URL management."""
    print("🔧 UPSKILL URLS MANAGEMENT TOOL")
    print("=" * 50)
    
    urls = load_urls()
    
    while True:
        print("\n📋 MENU:")
        print("1. View all URLs")
        print("2. Add new URL")
        print("3. Remove URL")
        print("4. Save and exit")
        print("5. Exit without saving")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            display_urls(urls)
        
        elif choice == "2":
            urls = add_url(urls)
        
        elif choice == "3":
            urls = remove_url(urls)
        
        elif choice == "4":
            if save_urls(urls):
                print("👋 Goodbye! URLs saved successfully.")
                break
            else:
                print("❌ Error saving URLs. Try again.")
        
        elif choice == "5":
            confirm = input("Are you sure you want to exit without saving? (y/N): ").strip().lower()
            if confirm == 'y':
                print("👋 Goodbye! Changes not saved.")
                break
        
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
