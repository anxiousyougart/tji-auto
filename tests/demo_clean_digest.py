#!/usr/bin/env python3
"""
Demo script for the Clean Daily Tech Digest.
Shows the simplified, clean JSON format with only essential fields.
"""

import json
import os
from daily_tech_aggregator import create_daily_digest, save_daily_digest

def display_clean_digest():
    """Display the clean daily digest in a formatted way."""
    
    print("🧹 CLEAN DAILY TECH DIGEST")
    print("=" * 50)
    print("Simplified format with only essential fields:\n")
    
    # Check if digest file exists
    if os.path.exists("../data/daily_tech_digest.json"):
        with open("../data/daily_tech_digest.json", 'r', encoding='utf-8') as f:
            digest = json.load(f)
        
        print("📋 CURRENT DIGEST CONTENT:")
        print("-" * 30)
        
        # Tech News
        if digest.get("tech_news"):
            news = digest["tech_news"]
            print(f"📰 TECH NEWS:")
            print(f"   Title: {news['title']}")
            print(f"   URL: {news['url']}\n")
        else:
            print(f"📰 TECH NEWS: Not available\n")
        
        # Internships
        if digest.get("internships"):
            internship = digest["internships"]
            print(f"💼 INTERNSHIPS:")
            print(f"   Title: {internship['title']}")
            print(f"   Company: {internship['company']}")
            print(f"   URL: {internship['url']}\n")
        else:
            print(f"💼 INTERNSHIPS: Not available\n")
        
        # Jobs
        if digest.get("jobs"):
            job = digest["jobs"]
            print(f"💼 JOBS:")
            print(f"   Title: {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   URL: {job['url']}\n")
        else:
            print(f"💼 JOBS: Not available\n")
        
        # Upskill Articles
        if digest.get("upskill_articles"):
            article = digest["upskill_articles"]
            print(f"📚 UPSKILL ARTICLES:")
            print(f"   Title: {article['title']}")
            print(f"   URL: {article['url']}\n")
        else:
            print(f"📚 UPSKILL ARTICLES: Not available\n")
        
        # Show clean JSON format
        print("💻 CLEAN JSON FORMAT:")
        print("=" * 50)
        print(json.dumps(digest, indent=2))
        print("=" * 50)
        
        # Statistics
        available_count = sum(1 for content in digest.values() if content is not None)
        print(f"\n📊 SUMMARY:")
        print(f"   Available: {available_count}/4 sources")
        print(f"   Format: Clean JSON with essential fields only")
        print(f"   File size: {os.path.getsize('../data/daily_tech_digest.json')} bytes")
        
    else:
        print("❌ No digest file found. Creating new one...")
        create_new_digest()

def create_new_digest():
    """Create a new clean digest."""
    
    print("\n🔄 Creating new clean digest...")
    
    # Create the digest
    digest = create_daily_digest()
    
    if digest:
        # Save the digest
        if save_daily_digest(digest):
            print("✅ Clean digest created successfully!")
            
            # Display the new digest
            print("\n📋 NEW DIGEST CONTENT:")
            print("-" * 30)
            print(json.dumps(digest, indent=2))
            
            # Statistics
            available_count = sum(1 for content in digest.values() if content is not None)
            print(f"\n📊 SUMMARY:")
            print(f"   Available: {available_count}/4 sources")
            print(f"   Format: Clean JSON with essential fields only")
        else:
            print("❌ Failed to save digest")
    else:
        print("❌ Failed to create digest")

def show_format_comparison():
    """Show the difference between old complex format and new clean format."""
    
    print("\n🔄 FORMAT COMPARISON:")
    print("=" * 60)
    
    print("❌ OLD COMPLEX FORMAT:")
    print("-" * 30)
    old_format = {
        "daily_tech_digest": {
            "metadata": {
                "generated_at": "2025-01-25T10:30:00",
                "aggregator_version": "1.0",
                "total_sources": 4,
                "successful_sources": 4,
                "source_files": {"...": "lots of metadata"}
            },
            "summary": {
                "tech_news": {"count": 1, "status": "success", "title": "..."},
                "internships": {"count": 1, "status": "success", "title": "..."}
            },
            "content": {
                "tech_news": {"selected_article": {"title": "...", "url": "..."}, "ai_reasoning": "..."},
                "internships": {"selected_internship": {"title": "...", "company": "...", "url": "..."}, "ai_reasoning": "..."}
            }
        }
    }
    print(json.dumps(old_format, indent=2)[:400] + "...")
    
    print("\n✅ NEW CLEAN FORMAT:")
    print("-" * 30)
    clean_format = {
        "tech_news": {
            "title": "Article Title",
            "url": "https://example.com"
        },
        "internships": {
            "title": "Internship Title",
            "company": "Company Name",
            "url": "https://example.com"
        },
        "jobs": {
            "title": "Job Title", 
            "company": "Company Name",
            "url": "https://example.com"
        },
        "upskill_articles": {
            "title": "Article Title",
            "url": "https://example.com"
        }
    }
    print(json.dumps(clean_format, indent=2))
    
    print(f"\n📊 BENEFITS OF CLEAN FORMAT:")
    print(f"   ✅ 90% smaller file size")
    print(f"   ✅ Only essential fields")
    print(f"   ✅ Easy to parse and use")
    print(f"   ✅ No unnecessary metadata")
    print(f"   ✅ Direct access to content")

def main():
    """Main demo function."""
    
    print("🧹 CLEAN DAILY TECH DIGEST DEMO")
    print("=" * 60)
    print("This demo shows the simplified, clean JSON format")
    print("with only the essential fields you requested.\n")
    
    # Show format comparison first
    show_format_comparison()
    
    # Display current digest
    display_clean_digest()
    
    print(f"\n🎯 CLEAN FORMAT SPECIFICATIONS:")
    print(f"   📰 Tech News: title, url")
    print(f"   💼 Internships: title, company, url") 
    print(f"   💼 Jobs: title, company, url")
    print(f"   📚 Upskill Articles: title, url")
    
    print(f"\n🚀 USAGE:")
    print(f"   python daily_tech_aggregator.py  # Create clean digest")
    print(f"   python demo_clean_digest.py      # View this demo")
    print(f"   cat daily_tech_digest.json       # View raw JSON")

if __name__ == "__main__":
    main()
