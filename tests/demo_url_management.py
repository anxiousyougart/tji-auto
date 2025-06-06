#!/usr/bin/env python3
"""
Demonstration of URL management for the upskill scraper.
"""

from upskill_scraper import load_urls_from_config, add_url_to_config, save_urls_to_config
import json

def main():
    """Demonstrate URL management capabilities."""
    
    print("🔧 UPSKILL SCRAPER URL MANAGEMENT DEMO")
    print("=" * 50)
    
    # Load current URLs
    print("\n📚 Loading current URL configuration...")
    urls = load_urls_from_config()
    
    # Display current URLs
    print(f"\n📊 Current URL Statistics:")
    total_urls = 0
    for category, url_list in urls.items():
        count = len(url_list)
        total_urls += count
        print(f"  • {category.replace('_', ' ').title()}: {count} URLs")
    
    print(f"\n🎯 Total URLs: {total_urls}")
    
    # Show sample URLs from each category
    print(f"\n📋 Sample URLs by Category:")
    print("-" * 40)
    
    for category, url_list in urls.items():
        print(f"\n🔗 {category.replace('_', ' ').title()}:")
        for i, url in enumerate(url_list[:3], 1):  # Show first 3 URLs
            print(f"  {i}. {url}")
        if len(url_list) > 3:
            print(f"  ... and {len(url_list) - 3} more")
    
    # Demonstrate adding a new URL
    print(f"\n➕ DEMONSTRATION: Adding a new URL")
    print("-" * 40)
    
    # Example: Add a new tech education site
    new_url = "https://www.codecademy.com/resources/blog"
    category = "tech_education"
    
    print(f"Adding: {new_url}")
    print(f"To category: {category}")
    
    success = add_url_to_config(category, new_url)
    if success:
        print("✅ URL added successfully!")
        
        # Reload and show updated count
        updated_urls = load_urls_from_config()
        new_count = len(updated_urls[category])
        print(f"📊 Updated {category} count: {new_count} URLs")
    else:
        print("❌ Failed to add URL")
    
    # Show how to add URLs to different categories
    print(f"\n📝 HOW TO ADD MORE URLs:")
    print("-" * 30)
    print("1. Edit upskill_urls_config.json directly")
    print("2. Use the add_url_to_config() function:")
    print("   add_url_to_config('category_name', 'https://example.com')")
    print("3. Use the interactive manage_upskill_urls.py script")
    
    # Show available categories
    print(f"\n📂 Available Categories:")
    for category in urls.keys():
        print(f"  • {category}")
    
    print(f"\n💡 Tips for Adding URLs:")
    print("  • Use descriptive category names")
    print("  • Group similar sites together")
    print("  • Test new URLs before adding them")
    print("  • The scraper will automatically use new URLs")
    
    print(f"\n🚀 Ready to scrape with {sum(len(url_list) for url_list in updated_urls.values())} URLs!")
    print("=" * 50)

if __name__ == "__main__":
    main()
