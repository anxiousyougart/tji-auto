#!/usr/bin/env python3
"""
Test script to verify upskill article deduplication functionality
"""

import json
from upskill_scraper import (
    load_upskill_history, 
    save_upskill_history, 
    add_to_upskill_history, 
    filter_previously_selected
)

def test_deduplication():
    """Test the deduplication functionality"""
    
    print("=== Testing Upskill Article Deduplication ===\n")
    
    # Test articles (some duplicates of what's in history)
    test_articles = [
        {
            "title": "Building Data Science Projects Using AI: A Vibe Coding Guide",
            "url": "https://www.kdnuggets.com/building-data-science-projects-using-ai-a-vibe-coding-guide"
        },
        {
            "title": "How to Make an AI Chatbot from Scratch using Docker Model Runner",
            "url": "https://www.docker.com/blog/how-to-make-ai-chatbot-from-scratch/"
        },
        {
            "title": "New Article: Python Best Practices",
            "url": "https://example.com/python-best-practices"
        },
        {
            "title": "Another New Article: React Hooks Guide",
            "url": "https://example.com/react-hooks-guide"
        }
    ]
    
    print(f"📝 Test articles: {len(test_articles)}")
    for i, article in enumerate(test_articles, 1):
        print(f"  {i}. {article['title'][:50]}...")
    
    # Load current history
    print(f"\n📚 Loading current history...")
    history = load_upskill_history()
    print(f"  • History entries: {len(history)}")
    
    # Filter articles
    print(f"\n🔍 Filtering previously selected articles...")
    filtered_articles = filter_previously_selected(test_articles)
    
    print(f"\n📊 RESULTS:")
    print(f"  • Original articles: {len(test_articles)}")
    print(f"  • Filtered articles: {len(filtered_articles)}")
    print(f"  • Duplicates removed: {len(test_articles) - len(filtered_articles)}")
    
    print(f"\n✅ NEW ARTICLES (not previously selected):")
    for i, article in enumerate(filtered_articles, 1):
        print(f"  {i}. {article['title']}")
    
    # Test adding a new article to history
    if filtered_articles:
        test_article = filtered_articles[0]
        print(f"\n➕ Testing add to history: {test_article['title'][:50]}...")
        add_to_upskill_history(test_article)
        
        # Verify it was added
        updated_history = load_upskill_history()
        print(f"  • History entries after addition: {len(updated_history)}")
        
        # Test filtering again (should now filter out the added article)
        print(f"\n🔍 Testing filter again after addition...")
        re_filtered = filter_previously_selected(test_articles)
        print(f"  • Articles after re-filtering: {len(re_filtered)}")
        print(f"  • Additional duplicates found: {len(filtered_articles) - len(re_filtered)}")

if __name__ == "__main__":
    test_deduplication()
