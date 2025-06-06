#!/usr/bin/env python3
"""
Demo script for the Daily Tech Digest Aggregator.
Shows how to use the unified digest and displays the consolidated content.
"""

import json
import os
from datetime import datetime
from daily_tech_aggregator import create_daily_digest, save_daily_digest, generate_digest_summary

def display_content_details(content: dict, content_type: str):
    """Display detailed information about a specific content type."""

    if not content:
        print(f"   ❌ No content available")
        return

    print(f"   ✅ Content available:")

    if content_type == "tech_news":
        if "selected_article" in content:
            article = content["selected_article"]
            print(f"   📰 Title: {article.get('title', 'Unknown')}")
            print(f"   🔗 URL: {article.get('url', 'Unknown')}")
        else:
            # Simple format
            print(f"   📰 Title: {content.get('title', 'Unknown')}")
            print(f"   🔗 URL: {content.get('url', 'Unknown')}")
        if "ai_reasoning" in content:
            reasoning = content["ai_reasoning"][:200] + "..." if len(content["ai_reasoning"]) > 200 else content["ai_reasoning"]
            print(f"   🤖 AI Reasoning: {reasoning}")

    elif content_type == "internships":
        if "selected_internship" in content:
            internship = content["selected_internship"]
            print(f"   💼 Title: {internship.get('title', 'Unknown')}")
            print(f"   🏢 Company: {internship.get('company', 'Unknown')}")
            print(f"   🔗 URL: {internship.get('url', 'Unknown')}")
        else:
            # Simple format
            print(f"   💼 Title: {content.get('title', 'Unknown')}")
            print(f"   🏢 Company: {content.get('company', 'Unknown')}")
            print(f"   🔗 URL: {content.get('url', 'Unknown')}")
        if "ai_reasoning" in content:
            reasoning = content["ai_reasoning"][:200] + "..." if len(content["ai_reasoning"]) > 200 else content["ai_reasoning"]
            print(f"   🤖 AI Reasoning: {reasoning}")

    elif content_type == "jobs":
        if "selected_job" in content:
            job = content["selected_job"]
            print(f"   💼 Title: {job.get('title', 'Unknown')}")
            print(f"   🏢 Company: {job.get('company', 'Unknown')}")
            print(f"   🔗 URL: {job.get('url', 'Unknown')}")
        else:
            # Simple format
            print(f"   💼 Title: {content.get('title', 'Unknown')}")
            print(f"   🏢 Company: {content.get('company', 'Unknown')}")
            print(f"   🔗 URL: {content.get('url', 'Unknown')}")
        if "ai_reasoning" in content:
            reasoning = content["ai_reasoning"][:200] + "..." if len(content["ai_reasoning"]) > 200 else content["ai_reasoning"]
            print(f"   🤖 AI Reasoning: {reasoning}")

    elif content_type == "upskill_articles":
        if "selected_article" in content:
            article = content["selected_article"]
            print(f"   📚 Title: {article.get('title', 'Unknown')}")
            print(f"   🔗 URL: {article.get('url', 'Unknown')}")
        else:
            # Simple format
            print(f"   📚 Title: {content.get('title', 'Unknown')}")
            print(f"   🔗 URL: {content.get('url', 'Unknown')}")
        if "ai_reasoning" in content:
            reasoning = content["ai_reasoning"][:200] + "..." if len(content["ai_reasoning"]) > 200 else content["ai_reasoning"]
            print(f"   🤖 AI Reasoning: {reasoning}")

def display_digest_overview(digest: dict):
    """Display a comprehensive overview of the daily digest."""

    print("\n📊 DAILY TECH DIGEST OVERVIEW")
    print("=" * 60)

    metadata = digest["daily_tech_digest"]["metadata"]
    summary = digest["daily_tech_digest"]["summary"]
    content = digest["daily_tech_digest"]["content"]

    # Metadata
    print(f"🕒 Generated: {metadata['generated_at'][:19]}")
    print(f"📈 Success Rate: {metadata['successful_sources']}/{metadata['total_sources']} sources")
    print(f"../data/📁 Output File: daily_tech_digest.json")

    # Content breakdown
    print(f"\n📋 CONTENT BREAKDOWN:")
    print("-" * 40)

    content_order = ["tech_news", "internships", "jobs", "upskill_articles"]

    for i, content_type in enumerate(content_order, 1):
        display_name = {
            "tech_news": "Tech News",
            "internships": "Internships",
            "jobs": "Jobs/Placements",
            "upskill_articles": "Upskill Articles"
        }[content_type]

        print(f"\n{i}. 🔗 {display_name.upper()}")

        status = summary[content_type]["status"]
        if status == "success":
            print(f"   ✅ Status: Available")
            display_content_details(content[content_type], content_type)
        else:
            print(f"   ❌ Status: {status.replace('_', ' ').title()}")

def show_json_structure():
    """Show the JSON structure of the daily digest."""

    print(f"\n💻 JSON STRUCTURE PREVIEW:")
    print("=" * 50)

    sample_structure = {
        "daily_tech_digest": {
            "metadata": {
                "generated_at": "2025-01-25T10:30:00",
                "successful_sources": "X/4",
                "source_files": "{ file status for each scraper }"
            },
            "summary": {
                "tech_news": {"count": 1, "status": "success", "title": "..."},
                "internships": {"count": 1, "status": "success", "title": "..."},
                "jobs": {"count": 1, "status": "success", "title": "..."},
                "upskill_articles": {"count": 1, "status": "success", "title": "..."}
            },
            "content": {
                "tech_news": "{ complete AI-selected article data }",
                "internships": "{ complete AI-selected internship data }",
                "jobs": "{ complete AI-selected job data }",
                "upskill_articles": "{ complete AI-selected article data }"
            }
        }
    }

    print(json.dumps(sample_structure, indent=2))

def check_source_files():
    """Check which source files are available."""

    print(f"\n📁 SOURCE FILES STATUS:")
    print("-" * 30)

    source_files = {
        "../data/ai_selected_article.json": "Tech News Scraper",
        "../data/selected_internship.json": "Internship Scraper",
        "../data/selected_job.json": "Job Scraper",
        "../data/ai_selected_upskill_article.json": "Upskill Articles Scraper"
    }

    available_count = 0
    for file_path, description in source_files.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
            available_count += 1
        else:
            print(f"❌ {file_path} - {description} (missing)")

    print(f"\n📊 Available: {available_count}/{len(source_files)} source files")

    if available_count == 0:
        print(f"\n⚠️  No source files found. Run the individual scrapers first:")
        print(f"   1. python demo_tech_news.py")
        print(f"   2. python internship_scraper.py")
        print(f"   3. python jobs_scraper.py")
        print(f"   4. python demo_upskill.py")

    return available_count

def main():
    """Main demo function."""

    print("🎯 DAILY TECH DIGEST AGGREGATOR DEMO")
    print("=" * 60)
    print("This demo shows how the aggregator consolidates AI-selected")
    print("content from all four scrapers into a unified daily digest.\n")

    # Check source files
    available_files = check_source_files()

    if available_files > 0:
        print(f"\n🚀 Creating unified daily digest...")

        # Create the digest
        digest = create_daily_digest()

        if digest:
            # Save the digest
            save_daily_digest(digest)

            # Display overview
            display_digest_overview(digest)

            # Show JSON structure
            show_json_structure()

            print(f"\n🎉 SUCCESS!")
            print(f"Daily digest created with content from {available_files} sources.")
            print(f"Check '../data/daily_tech_digest.json' for the complete unified data.")

        else:
            print(f"❌ Failed to create daily digest")

    else:
        print(f"\n💡 TIP: Run the individual scrapers first to generate source files,")
        print(f"then run this aggregator to create the unified daily digest.")

    print(f"\n📖 USAGE:")
    print(f"   python daily_tech_aggregator.py  # Create digest")
    print(f"   python demo_daily_digest.py      # View this demo")

if __name__ == "__main__":
    main()
