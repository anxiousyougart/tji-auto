#!/usr/bin/env python3
"""
Demonstration of the upskill articles scraper for CS students.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from scrapers.upskill_scraper import upskill_articles, select_best_upskill_article
import json

def main():
    """Demonstrate the upskill articles scraper."""

    print("=== Upskill Articles Scraper for CS Students ===")
    print("This scraper finds educational content to help computer science students")
    print("learn new technologies, best practices, and implementation techniques.\n")

    print("🎯 TARGET CONTENT:")
    print("  • Technology tutorials and how-to guides")
    print("  • Best practices and tech stack recommendations")
    print("  • Project implementation tutorials")
    print("  • Company engineering blogs and technical insights")
    print("  • Developer tools and framework guides\n")

    print("📚 SOURCES:")
    print("  • Dev.to (tutorial section)")
    print("  • KDnuggets (data science & ML)")
    print("  • Medium (programming & tech tags)")
    print("  • Company engineering blogs (GitHub, Microsoft, Netflix, etc.)")
    print("  • Tech education sites (FreeCodeCamp, CSS-Tricks, DigitalOcean, etc.)")
    print("  • The New Stack (WebAssembly, AI, Security, Frontend, Backend, etc.)")
    print("  • XDA Developers and additional tech sites\n")

    print("🔍 FILTERING CRITERIA:")
    print("  • Articles published within the last 7 days")
    print("  • Titles containing educational keywords (tutorial, guide, how-to, etc.)")
    print("  • Focus on practical, hands-on learning content")
    print("  • Exclude opinion pieces and non-technical content")
    print("  • AI selection for most valuable learning resource\n")

    print("🤖 AI SELECTION CRITERIA:")
    print("  • Practical learning value (tutorials, implementation guides)")
    print("  • Technology relevance (modern, in-demand technologies)")
    print("  • Skill building potential (concrete, applicable skills)")
    print("  • Best practices and professional development")
    print("  • Career impact (portfolio-worthy skills)\n")

    try:
        print("🚀 Starting scraping process...\n")

        # Call the upskill_articles function
        articles = upskill_articles()

        print(f"\n=== RESULTS ===")
        if articles:
            print(f"Found {len(articles)} relevant upskill articles:\n")

            # Save all articles to JSON
            with open("../data/upskill_articles.json", 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)

            # Display articles by source
            sources = {}
            for article in articles:
                url = article['url']
                if 'dev.to' in url:
                    source = 'Dev.to'
                elif 'kdnuggets.com' in url:
                    source = 'KDnuggets'
                elif 'medium.com' in url:
                    source = 'Medium'
                elif any(company in url for company in ['github.blog', 'engineering.fb.com', 'netflixtechblog.com',
                                                       'blog.google', 'aws.amazon.com', 'devblogs.microsoft.com',
                                                       'blog.twitter.com', 'engineering.linkedin.com', 'stackoverflow.blog',
                                                       'blog.jetbrains.com', 'blog.docker.com', 'kubernetes.io']):
                    source = 'Company Blogs'
                elif any(site in url for site in ['freecodecamp.org', 'css-tricks.com', 'smashingmagazine.com',
                                                 'hackernoon.com', 'digitalocean.com']):
                    source = 'Tech Education Sites'
                elif 'thenewstack.io' in url:
                    source = 'The New Stack'
                elif any(site in url for site in ['xda-developers.com']):
                    source = 'XDA Developers & Additional'
                else:
                    source = 'Other'

                if source not in sources:
                    sources[source] = []
                sources[source].append(article)

            # Display by source
            for source, source_articles in sources.items():
                print(f"📖 {source} ({len(source_articles)} articles):")
                for i, article in enumerate(source_articles[:3], 1):  # Show first 3 from each source
                    print(f"  {i}. {article['title'][:80]}...")
                    print(f"     {article['url']}\n")
                if len(source_articles) > 3:
                    print(f"     ... and {len(source_articles) - 3} more from {source}\n")

            print(f"../data/💾 All articles saved to: upskill_articles.json")

            # AI selection
            print("\n🤖 AI analyzing articles to select the most valuable learning resource...")
            ai_result = select_best_upskill_article()

            if "selected_article" in ai_result:
                print(f"\n⭐ AI SELECTED BEST UPSKILL ARTICLE:")
                print("=" * 60)
                print(f"📰 Title: {ai_result['selected_article']['title']}")
                print(f"🔗 URL: {ai_result['selected_article']['url']}")
                print(f"\n🧠 AI Reasoning:")
                print(f"{ai_result['ai_reasoning']}")
                print(f"\n📊 Analysis Summary:")
                print(f"  • Total articles analyzed: {ai_result['total_articles_analyzed']}")
                print(f"  • Selection criteria: {ai_result['selection_criteria']}")
                print(f"../data/\n💾 AI selection saved to: ai_selected_upskill_article.json")
                print("=" * 60)
            else:
                print(f"\n❌ AI selection failed: {ai_result.get('error', 'Unknown error')}")

            # Show JSON format sample
            print(f"\n💻 JSON FORMAT SAMPLE:")
            print("=" * 50)
            sample_articles = articles[:2]  # Show first 2 articles
            print(json.dumps(sample_articles, indent=2))
            print("=" * 50)

        else:
            print("No upskill articles found matching the criteria.")
            print("\n🤔 This could mean:")
            print("  • No educational articles were published in the last 7 days")
            print("  • Articles don't match the upskill keyword filters")
            print("  • Date extraction failed for the articles")
            print("  • Network issues preventing scraping")
            print("\n💡 Try running again later or check the log file for details.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("\n🔧 Troubleshooting:")
        print("  • Check your internet connection")
        print("  • Verify the Groq API key is valid")
        print("  • Check the upskill_scraper.log file for detailed error information")

if __name__ == "__main__":
    main()
