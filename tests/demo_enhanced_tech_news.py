#!/usr/bin/env python3
"""
Demo script for the Enhanced Tech News Scraper with 48-hour filtering,
technical innovation focus, and duplicate prevention.
"""

import json
import os
from webscraptest import tech_news, select_best_article

def main():
    """Demonstrate the enhanced tech news scraper."""

    print("🔬 ENHANCED TECH NEWS SCRAPER DEMO")
    print("=" * 60)
    print("Enhanced filtering for technical innovation and advancement")
    print("Features:")
    print("  • Strict 48-hour date filtering")
    print("  • Technical innovation keyword focus")
    print("  • Duplicate prevention (30-day history)")
    print("  • AI selection for best technical advancement")
    print("  • Comprehensive filtering statistics\n")

    # Tech news URLs focused on technical content
    tech_urls = [
        "https://news.ycombinator.com/",
        "https://techcrunch.com/",
        "https://www.theverge.com/tech",
        "https://arstechnica.com/",
        "https://www.scitechdaily.com/",
        "https://devblogs.microsoft.com/",
        "https://www.analyticsinsight.net/",
        "https://www.innovationnewsnetwork.com/",
        "https://techxplore.com/",
        "https://openai.com/blog/",
        "https://www.linkedin.com/blog/engineering"
    ]

    print(f"🔍 SCRAPING SOURCES:")
    for i, url in enumerate(tech_urls, 1):
        print(f"  {i}. {url}")

    print(f"\n🚀 Starting enhanced tech news scraping...")

    try:
        # Scrape articles with enhanced filtering
        articles = tech_news(tech_urls)

        print(f"\n=== SCRAPING RESULTS ===")
        if articles:
            print(f"✅ Found {len(articles)} technical innovation articles")

            # Save articles to JSON
            with open("../data/todays_tech_news.json", 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)

            print(f"../data/💾 Articles saved to: todays_tech_news.json")

            # Display sample articles
            print(f"\n📋 SAMPLE TECHNICAL ARTICLES:")
            for i, article in enumerate(articles[:5], 1):
                print(f"\n{i}. 🔬 {article['title']}")
                print(f"   🔗 {article['url']}")

            if len(articles) > 5:
                print(f"\n... and {len(articles) - 5} more technical articles")

            # AI selection for best technical innovation
            print(f"\n🤖 AI ANALYZING FOR BEST TECHNICAL INNOVATION...")
            selected_article = select_best_article()

            if selected_article:
                print(f"\n⭐ AI SELECTED BEST TECHNICAL INNOVATION:")
                print("=" * 60)
                print(f"📰 Title: {selected_article['title']}")
                print(f"🔗 URL: {selected_article['url']}")
                print(f"\n🧠 AI Technical Analysis:")
                print(f"{selected_article.get('ai_reasoning', 'No reasoning provided')}")
                print("=" * 60)

                # Save AI selection
                with open("../data/ai_selected_article.json", 'w', encoding='utf-8') as f:
                    json.dump(selected_article, f, indent=2, ensure_ascii=False)

                print(f"../data/\n💾 AI selection saved to: ai_selected_article.json")
            else:
                print(f"\n❌ AI selection failed - using fallback selection")
                # Fallback: select the most technical-sounding article
                fallback_article = articles[0]  # First article as fallback
                fallback_selection = {
                    "title": fallback_article["title"],
                    "url": fallback_article["url"]
                }

                with open("../data/ai_selected_article.json", 'w', encoding='utf-8') as f:
                    json.dump(fallback_selection, f, indent=2, ensure_ascii=False)

                print(f"\n⭐ FALLBACK SELECTION:")
                print("=" * 60)
                print(f"📰 Title: {fallback_selection['title']}")
                print(f"🔗 URL: {fallback_selection['url']}")
                print("=" * 60)
                print(f"../data/\n💾 Fallback selection saved to: ai_selected_article.json")

        else:
            print(f"❌ No technical innovation articles found")
            print(f"\nPossible reasons:")
            print(f"  • No articles published in last 48 hours")
            print(f"  • Articles don't match technical innovation keywords")
            print(f"  • All articles were filtered as duplicates")
            print(f"  • Date extraction failed for articles")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

    # Show filtering statistics if available
    if os.path.exists("../data/tech_news_history.json"):
        try:
            with open("../data/tech_news_history.json", 'r', encoding='utf-8') as f:
                history = json.load(f)
            print(f"\n📊 DUPLICATE PREVENTION STATUS:")
            print(f"  • History entries: {len(history)}")
            print(f"  • Rolling window: 30 days")
            print(f"  • Tracks both titles and URLs")
        except Exception:
            pass

    print(f"\n🎯 ENHANCED FILTERING CRITERIA:")
    print(f"  📅 Date Filter: Strict 48-hour window")
    print(f"  🔬 Content Focus: Technical innovation & advancement")
    print(f"  🚫 Excludes: Business news, opinions, marketing")
    print(f"  🔄 Duplicate Prevention: 30-day rolling history")
    print(f"  🤖 AI Selection: Technical significance priority")

    print(f"\n💡 TECHNICAL INNOVATION KEYWORDS:")
    print(f"  • Breakthrough, innovation, advancement")
    print(f"  • AI/ML developments, algorithm improvements")
    print(f"  • Software/hardware releases with technical depth")
    print(f"  • Engineering innovations, research advances")
    print(f"  • Performance improvements, optimization")

    print(f"\n📁 OUTPUT FILES:")
    files_to_check = [
        "../data/todays_tech_news.json",
        "../data/ai_selected_article.json",
        "../data/tech_news_history.json"
    ]

    for file_name in files_to_check:
        if os.path.exists(file_name):
            size = os.path.getsize(file_name)
            print(f"  ✅ {file_name} ({size} bytes)")
        else:
            print(f"  ❌ {file_name} (not found)")

if __name__ == "__main__":
    main()
