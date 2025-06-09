#!/usr/bin/env python3


import json
import os
from datetime import datetime

def create_sample_digest():
    """Create a sample daily_tech_digest.json for testing."""
    sample_data = {
        "daily_tech_digest": {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "successful_sources": "4/4",
                "source_files": {
                    "tech_news": "../data/ai_selected_article.json",
                    "internships": "../data/selected_internship.json",
                    "jobs": "../data/selected_job.json",
                    "upskill_articles": "../data/ai_selected_upskill_article.json"
                }
            },
            "summary": {
                "tech_news": {"count": 1, "status": "success"},
                "internships": {"count": 1, "status": "success"},
                "jobs": {"count": 1, "status": "success"},
                "upskill_articles": {"count": 1, "status": "success"}
            },
            "content": {
                "tech_news": {
                    "title": "Revolutionary AI Framework Released by OpenAI",
                    "url": "https://openai.com/blog/revolutionary-ai-framework-released-with-advanced-capabilities-for-developers"
                },
                "internships": {
                    "title": "Software Engineer Intern - Machine Learning",
                    "company": "TechCorp",
                    "url": "https://www.linkedin.com/jobs/view/software-engineer-intern-machine-learning-at-techcorp-3847291056"
                },
                "jobs": {
                    "title": "Junior Full Stack Developer",
                    "company": "StartupXYZ",
                    "url": "https://www.linkedin.com/jobs/view/junior-full-stack-developer-at-startupxyz-3847291057"
                },
                "upskill_articles": {
                    "title": "Complete Guide to React Hooks and Modern JavaScript",
                    "url": "https://dev.to/techwriter/complete-guide-to-react-hooks-and-modern-javascript-best-practices-2024"
                }
            }
        }
    }

    try:
        with open('../data/daily_tech_digest.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Created sample daily_tech_digest.json for testing")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample digest: {e}")
        return False

def check_existing_digest():
    """Check if daily_tech_digest.json exists and show its contents."""
    if os.path.exists('../data/daily_tech_digest.json'):
        try:
            with open('../data/daily_tech_digest.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("../data/✅ Found existing daily_tech_digest.json")
            
            # Show content summary
            if 'daily_tech_digest' in data and 'content' in data['daily_tech_digest']:
                content = data['daily_tech_digest']['content']
                print(f"\n📊 Content Summary:")
                for category, category_data in content.items():
                    if category_data and category_data != "No suitable content found":
                        if isinstance(category_data, dict):
                            title = category_data.get('title', 'Unknown')[:50] + "..." if len(category_data.get('title', '')) > 50 else category_data.get('title', 'Unknown')
                            print(f"  • {category.replace('_', ' ').title()}: {title}")
                        else:
                            print(f"  • {category.replace('_', ' ').title()}: Available")
                    else:
                        print(f"  • {category.replace('_', ' ').title()}: No content")
            
            return True
        except Exception as e:
            print(f"❌ Error reading existing digest: {e}")
            return False
    else:
        print("⚠️  No daily_tech_digest.json found")
        return False

def show_expected_output():
    """Show what the expected output will look like."""
    print(f"\n🎯 EXPECTED OUTPUT:")
    print("-" * 40)
    print("After running the TinyURL shortener, you'll get:")
    print()
    print("📁 shortened_urls_digest.json - Complete results with:")
    print("  • Original and shortened URLs")
    print("  • Category-specific aliases (Tech_news_TJI_1, etc.)")
    print("  • Processing statistics and metadata")
    print("  • Success/failure status for each URL")
    print()
    print("📁 tinyurl_shortener.log - Detailed processing logs")
    print()
    print("🔗 Example shortened URLs:")
    print("  • Tech News: https://tinyurl.com/26cmrmmx")
    print("  • Internships: https://tinyurl.com/24svpwup")
    print("  • Jobs: https://tinyurl.com/28nskp9u")
    print("  • Upskill: https://tinyurl.com/24uxeqfm")

def show_api_info():
    """Show information about the TinyURL API integration."""
    print(f"\n🔧 TINYURL API INTEGRATION:")
    print("-" * 40)
    print("• API Endpoint: http://tinyurl.com/api-create.php")
    print("• Authentication: None required (free API)")
    print("• Request Type: Simple GET request")
    print("• Alias tracking: Internal category-based organization")
    print("• Rate limiting: Built-in delays and retry logic")
    print("• Error handling: Comprehensive logging and fallbacks")

def main():
    """Main demo function."""
    print("🔗 TINYURL SHORTENER DEMO")
    print("=" * 50)
    print("This demo shows how the TinyURL shortening automation works.")
    print()
    
    # Check for existing digest
    has_digest = check_existing_digest()
    
    if not has_digest:
        print("\n🔧 Would you like to create a sample digest for testing? (y/n): ", end="")
        response = input().lower().strip()
        if response in ['y', 'yes']:
            create_sample_digest()
            has_digest = True
        else:
            print("⚠️  No digest file available. Please run the scrapers first or create a sample.")
            return
    
    if has_digest:
        show_expected_output()
        show_api_info()
        
        print("\n🚀 Ready to run TinyURL shortening!")
        print("\nTo run the TinyURL shortener:")
        print("  python tinyurl_shortener.py")
        print("\nOr integrate it into your workflow:")
        print("  python master_scraper.py  # Run all scrapers")
        print("  python tinyurl_shortener.py  # Then shorten URLs")
        
        print("\n⚠️  IMPORTANT NOTES:")
        print("  • TinyURL free API - no authentication required")
        print("  • Internal alias tracking follows TJI naming convention")
        print("  • Rate limiting is built-in (1 second delays)")
        print("  • Failed URLs will be logged and skipped")
        print("  • Output includes both original and shortened URLs")
        
        print("\n📊 ALIAS FORMATS:")
        print("  • Tech News: Tech_news_TJI_1, Tech_news_TJI_2, ...")
        print("  • Internships: Internship_TJI_1, Internship_TJI_2, ...")
        print("  • Jobs: Placement_update_TJI_1, Placement_update_TJI_2, ...")
        print("  • Upskill: Upskill_TJI_1, Upskill_TJI_2, ...")

if __name__ == "__main__":
    main()
