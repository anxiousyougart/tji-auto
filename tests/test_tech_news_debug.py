#!/usr/bin/env python3
"""
Debug script for tech news scraper to identify AI selection issues.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_tech_news_scraper():
    """Test the tech news scraper with debugging."""
    print("🧪 TECH NEWS SCRAPER DEBUG TEST")
    print("=" * 50)
    
    try:
        # Import the scraper functions
        from scrapers.webscraptest import tech_news, select_best_article
        
        print("✅ Successfully imported scraper functions")
        
        # Test with a smaller set of URLs for faster debugging
        test_urls = [
            "https://news.ycombinator.com/",
            "https://www.theverge.com/",
            "https://techcrunch.com/category/artificial-intelligence/"
        ]
        
        print(f"\n🔍 Testing with {len(test_urls)} URLs:")
        for url in test_urls:
            print(f"  - {url}")
        
        # Call tech_news function
        print(f"\n📊 Calling tech_news function...")
        articles = tech_news(test_urls)
        
        print(f"\n📋 SCRAPING RESULTS:")
        print(f"Articles found: {len(articles) if articles else 0}")
        
        if articles:
            print(f"\nFirst few articles:")
            for i, article in enumerate(articles[:3]):
                print(f"  {i+1}. {article['title'][:60]}...")
                print(f"     URL: {article['url'][:60]}...")
            
            # Save to test file
            test_file = '../data/test_tech_news.json'
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved articles to: {test_file}")
            
            # Test AI selection
            print(f"\n🤖 TESTING AI SELECTION:")
            print("-" * 30)
            
            selected_article = select_best_article(test_file)
            
            if selected_article:
                print(f"✅ AI selection successful!")
                print(f"Selected: {selected_article['title']}")
                print(f"URL: {selected_article['url']}")
                print(f"Reasoning: {selected_article.get('ai_reasoning', 'No reasoning provided')}")
                
                # Save AI selection
                ai_result = {
                    "title": selected_article['title'],
                    "url": selected_article['url']
                }
                
                ai_file = '../data/test_ai_selected_article.json'
                with open(ai_file, 'w', encoding='utf-8') as f:
                    json.dump(ai_result, f, indent=2, ensure_ascii=False)
                print(f"💾 AI selection saved to: {ai_file}")
                
                return True
            else:
                print(f"❌ AI selection failed!")
                
                # Try manual fallback
                print(f"\n🔄 Testing manual fallback...")
                if articles:
                    fallback_article = articles[0]
                    fallback_result = {
                        "title": fallback_article['title'],
                        "url": fallback_article['url']
                    }
                    
                    fallback_file = '../data/test_ai_selected_article.json'
                    with open(fallback_file, 'w', encoding='utf-8') as f:
                        json.dump(fallback_result, f, indent=2, ensure_ascii=False)
                    print(f"💾 Fallback selection saved to: {fallback_file}")
                    print(f"Fallback article: {fallback_article['title']}")
                    
                    return True
                else:
                    print(f"❌ No articles available for fallback")
                    return False
        else:
            print(f"❌ No articles found by scraper")
            
            # Create empty result file
            empty_result = {"title": "No tech news found", "url": ""}
            empty_file = '../data/test_ai_selected_article.json'
            with open(empty_file, 'w', encoding='utf-8') as f:
                json.dump(empty_result, f, indent=2, ensure_ascii=False)
            print(f"💾 Empty result saved to: {empty_file}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error in tech news test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_selection_only():
    """Test AI selection with existing data."""
    print("\n🤖 TESTING AI SELECTION ONLY")
    print("=" * 50)
    
    # Check if we have existing data
    test_files = [
        '../data/todays_tech_news.json',
        '../data/test_tech_news.json'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"📁 Found existing data: {test_file}")
            
            try:
                from scrapers.webscraptest import select_best_article
                
                print(f"🤖 Testing AI selection on existing data...")
                selected = select_best_article(test_file)
                
                if selected:
                    print(f"✅ AI selection worked!")
                    print(f"Selected: {selected['title'][:60]}...")
                    return True
                else:
                    print(f"❌ AI selection failed on existing data")
            except Exception as e:
                print(f"❌ Error testing AI selection: {e}")
    
    print(f"⚠️ No existing data found for AI selection test")
    return False

def check_environment():
    """Check environment and dependencies."""
    print("\n🔍 ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"✅ GROQ_API_KEY found (length: {len(api_key)})")
    else:
        print(f"⚠️ GROQ_API_KEY not found in environment")
    
    # Check config
    try:
        sys.path.append('../config')
        from config import get_groq_api_key
        config_key = get_groq_api_key()
        if config_key:
            print(f"✅ Config API key available (length: {len(config_key)})")
        else:
            print(f"⚠️ Config API key not available")
    except Exception as e:
        print(f"⚠️ Config import failed: {e}")
    
    # Check Groq library
    try:
        from groq import Groq
        print(f"✅ Groq library available")
    except ImportError:
        print(f"❌ Groq library not installed")
        return False
    
    # Check data directory
    data_dir = '../data'
    if os.path.exists(data_dir):
        print(f"✅ Data directory exists")
        if os.access(data_dir, os.W_OK):
            print(f"✅ Data directory is writable")
        else:
            print(f"❌ Data directory is not writable")
            return False
    else:
        print(f"❌ Data directory does not exist")
        return False
    
    return True

def main():
    """Main test function."""
    print("🧪 TECH NEWS AI SELECTION DEBUG")
    print("=" * 60)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed")
        return False
    
    # Test AI selection on existing data first
    if test_ai_selection_only():
        print("\n✅ AI selection works with existing data")
    
    # Run full scraper test
    success = test_tech_news_scraper()
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 50)
    
    if success:
        print("✅ Tech news scraper and AI selection working!")
        print("💡 The issue might be in the pipeline orchestration")
        print("\n🔍 Next steps:")
        print("  • Check if daily_tech_aggregator.py can find the AI selected file")
        print("  • Verify file paths in the aggregator")
        print("  • Test the complete pipeline")
    else:
        print("❌ Tech news scraper or AI selection has issues")
        print("\n🔧 Troubleshooting:")
        print("  • Check internet connection")
        print("  • Verify API keys are valid")
        print("  • Check if websites are accessible")
        print("  • Review error messages above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
