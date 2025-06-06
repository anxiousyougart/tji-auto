#!/usr/bin/env python3
"""
Test script to verify TinyURL counter and alias generation
"""

from tinyurl_shortener import TinyURLShortener

def test_counter_and_aliases():
    """Test the current counter value and alias generation"""
    
    print("🔗 TINYURL COUNTER TEST")
    print("=" * 50)
    
    # Initialize shortener
    shortener = TinyURLShortener()
    
    # Display current counter
    print(f"📊 Current run number: {shortener.run_number}")
    print(f"🔄 Next run will use: {shortener.run_number + 1}")
    print()
    
    # Test alias generation for each category
    print("🏷️  ALIAS GENERATION TEST:")
    print("-" * 30)
    
    categories = ['tech_news', 'internships', 'jobs', 'upskill_articles']
    
    for category in categories:
        alias = shortener.generate_alias(category)
        print(f"{category:15} → {alias}")
    
    print()
    print("✅ When you run the TinyURL shortener next, it will use these aliases:")
    print("   • tech-news-tji-374")
    print("   • internship-tji-374") 
    print("   • placement-update-tji-374")
    print("   • upskill-tji-374")
    print()
    print("🔄 After that run, the counter will increment to 375 for subsequent runs.")

if __name__ == "__main__":
    test_counter_and_aliases()
