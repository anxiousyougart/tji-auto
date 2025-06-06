#!/usr/bin/env python3
"""
Demonstration of the simplified tech_news function.
"""

from webscraptest import tech_news, select_best_article
import json

def main():
    """Demonstrate the tech_news function."""

    print("=== AI-Powered Tech News Scraper Demo ===")
    print("This function scrapes tech news articles from 16 major tech news sources,")
    print("filters for technical content from the last 2 days, and uses AI to select")
    print("the most important article of the day.\n")

    # Comprehensive list of tech news URLs to scrape
    urls = [
        # Original sources
        "https://news.ycombinator.com/",
        "https://www.theverge.com/",
        "https://techcrunch.com/category/artificial-intelligence/",
        "https://scitechdaily.com/news/technology/",

        # New comprehensive sources
        "https://devblogs.microsoft.com/engineering-at-microsoft/",
        "https://www.theverge.com/ai-artificial-intelligence",
        "https://arstechnica.com/ai/",
        "https://arstechnica.com/gadgets/",
        "https://www.analyticsinsight.net/news",
        "https://www.innovationnewsnetwork.com/artificial-intelligence/",
        "https://www.innovationnewsnetwork.com/computer-science/",
        "https://www.innovationnewsnetwork.com/cybersecurity/",
        "https://www.innovationnewsnetwork.com/category/quantum-news/",
        "https://techxplore.com/hi-tech-news/",
        "https://openai.com/news/",
        "https://www.linkedin.com/blog/engineering"
    ]

    print(f"Scraping {len(urls)} tech news websites...")
    print("URLs:")
    for url in urls:
        print(f"  - {url}")

    print("\nFiltering criteria:")
    print("  - Articles published within the last 2 days (today and yesterday)")
    print("  - Titles containing technical keywords (AI, ML, blockchain, etc.)")
    print("  - Excluding business drama and non-technical content")
    print("  - AI selection for most important article covering:")
    print("    • New AI models/tools/breakthroughs")
    print("    • Tech product innovation")
    print("    • Developer tools/cloud/hardware updates")

    try:
        # Call the tech_news function
        articles = tech_news(urls)

        print(f"\n=== RESULTS ===")
        print(f"Found {len(articles)} relevant tech articles from the last 2 days:\n")

        if articles:
            # Save results to JSON file first
            output_file = '../data/todays_tech_news.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {output_file}")

            # AI-powered article selection
            print(f"\n🤖 AI ARTICLE SELECTION 🤖")
            print("=" * 50)

            best_article = select_best_article(output_file)
            if best_article:
                print(f"📰 ARTICLE OF THE DAY (AI Selected):")
                print(f"Title: {best_article['title']}")
                print(f"URL: {best_article['url']}")
                print(f"Reasoning: {best_article.get('ai_reasoning', 'Selected by AI')}")

                # Save AI-selected article separately in clean JSON format
                ai_selected = {
                    "title": best_article['title'],
                    "url": best_article['url']
                }
                with open('../data/ai_selected_article.json', 'w', encoding='utf-8') as f:
                    json.dump(ai_selected, f, indent=2, ensure_ascii=False)
                print(f"🎯 AI-selected article saved to: ../data/ai_selected_article.json")
                print()
            else:
                print("❌ AI selection failed - using first article as fallback")
                best_article = articles[0]
                print(f"📰 FALLBACK ARTICLE OF THE DAY:")
                print(f"Title: {best_article['title']}")
                print(f"URL: {best_article['url']}")
                print()

            # Display all results
            print(f"\n📋 ALL ARTICLES ({len(articles)} found):")
            print("=" * 50)
            for i, article in enumerate(articles, 1):
                marker = "🌟" if best_article and article['url'] == best_article['url'] else "  "
                print(f"{marker} {i}. {article['title']}")
                print(f"     URL: {article['url']}\n")

            # Show JSON format
            print(f"\n💾 JSON FORMAT:")
            print("=" * 50)
            print(json.dumps(articles, indent=2))

        else:
            print("No articles found matching the criteria.")
            print("This could mean:")
            print("  - No tech articles were published in the last 2 days on these sites")
            print("  - Articles don't match the technical keyword filters")
            print("  - Date extraction failed for the articles")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
