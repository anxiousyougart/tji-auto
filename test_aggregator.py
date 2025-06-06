#!/usr/bin/env python3
"""
Test script to run the daily tech aggregator and verify it picks up the AI-selected article.
"""

import sys
import os
import json

# Add processors to path
sys.path.append('processors')

def test_aggregator():
    """Test the daily tech aggregator."""
    print("🧪 TESTING DAILY TECH AGGREGATOR")
    print("=" * 50)
    
    # Check if AI selected article exists
    ai_article_file = 'data/ai_selected_article.json'
    if os.path.exists(ai_article_file):
        with open(ai_article_file, 'r', encoding='utf-8') as f:
            ai_article = json.load(f)
        print(f"✅ AI selected article found:")
        print(f"   Title: {ai_article['title']}")
        print(f"   URL: {ai_article['url']}")
    else:
        print(f"❌ AI selected article not found: {ai_article_file}")
        return False
    
    # Import and run the aggregator
    try:
        from daily_tech_aggregator import main
        print(f"\n🔄 Running daily tech aggregator...")
        
        result = main()
        
        if result:
            print(f"\n✅ Aggregator completed successfully!")
            
            # Check if output file was created
            output_file = 'data/daily_tech_digest.json'
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    digest = json.load(f)
                
                print(f"\n📊 DIGEST CONTENT:")
                if 'daily_tech_digest' in digest:
                    content = digest['daily_tech_digest']['content']
                    tech_news = content.get('tech_news')
                    
                    if tech_news and tech_news != "No suitable content found":
                        print(f"✅ Tech News: {tech_news['title']}")
                        print(f"   URL: {tech_news['url']}")
                        return True
                    else:
                        print(f"❌ Tech News: No content found")
                        return False
                else:
                    print(f"❌ Invalid digest structure")
                    return False
            else:
                print(f"❌ Output file not created: {output_file}")
                return False
        else:
            print(f"❌ Aggregator failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running aggregator: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_aggregator()
    if success:
        print(f"\n🎉 SUCCESS: AI-selected tech news is working end-to-end!")
    else:
        print(f"\n❌ FAILURE: There are still issues with the pipeline")
    
    sys.exit(0 if success else 1)
