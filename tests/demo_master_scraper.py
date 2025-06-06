#!/usr/bin/env python3
"""
Demo of the Master Scraper - Daily Tech Digest Pipeline

This script demonstrates how to use the master orchestrator to run all scrapers
and create a unified daily tech digest.

Usage:
    python demo_master_scraper.py
"""

import os
import json
import time
from datetime import datetime

def check_existing_files():
    """Check which output files already exist."""
    files_to_check = [
        "../data/ai_selected_article.json",
        "../data/selected_internship.json", 
        "../data/selected_job.json",
        "../data/ai_selected_upskill_article.json",
        "../data/daily_tech_digest.json"
    ]
    
    print("📁 CHECKING EXISTING OUTPUT FILES:")
    print("-" * 40)
    
    existing_files = []
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
            existing_files.append(file)
        else:
            print(f"❌ {file} (not found)")
    
    return existing_files

def show_sample_output():
    """Show sample content from the daily digest if it exists."""
    if os.path.exists("../data/daily_tech_digest.json"):
        print("\n📋 SAMPLE DAILY DIGEST CONTENT:")
        print("-" * 40)
        
        try:
            with open("../data/daily_tech_digest.json", 'r', encoding='utf-8') as f:
                digest = json.load(f)
            
            # Show metadata
            metadata = digest.get("daily_tech_digest", {}).get("metadata", {})
            print(f"🕒 Generated: {metadata.get('generated_at', 'Unknown')}")
            print(f"📊 Success Rate: {metadata.get('successful_sources', 'Unknown')}")
            
            # Show content summary
            content = digest.get("daily_tech_digest", {}).get("content", {})
            
            for category, data in content.items():
                if data and data != "No suitable content found":
                    print(f"\n✅ {category.replace('_', ' ').title()}:")
                    if isinstance(data, dict):
                        title = data.get('title', 'No title')
                        print(f"   📰 {title[:60]}{'...' if len(title) > 60 else ''}")
                    else:
                        print(f"   📰 Content available")
                else:
                    print(f"\n❌ {category.replace('_', ' ').title()}: No content found")
                    
        except Exception as e:
            print(f"❌ Error reading digest: {e}")
    else:
        print("\n❌ No daily digest found. Run the master scraper first.")

def main():
    """Main demo function."""
    print("🎯 MASTER SCRAPER DEMO")
    print("=" * 60)
    print("This demo shows the master orchestrator that runs all four scrapers")
    print("and creates a unified daily tech digest.\n")
    
    # Check existing files
    existing_files = check_existing_files()
    
    print(f"\n📊 Found {len(existing_files)}/5 output files")
    
    # Show current digest if available
    show_sample_output()
    
    print("\n🚀 MASTER SCRAPER COMMANDS:")
    print("-" * 40)
    print("# Run the complete pipeline:")
    print("python master_scraper.py")
    print("# OR")
    print("python run_daily_digest_pipeline.py")
    print()
    print("# View the results:")
    print("python demo_daily_digest.py")
    print("../data/cat daily_tech_digest.json")
    
    print("\n📋 WHAT THE MASTER SCRAPER DOES:")
    print("-" * 40)
    print("1. 🔬 Tech News Scraper - AI-powered article selection")
    print("2. 💼 Internship Scraper - Internshala + LinkedIn")
    print("3. 🏢 Job Scraper - Entry-level positions (0-1 years)")
    print("4. 📚 Upskill Scraper - Tutorials & best practices")
    print("../data/5. 🔄 Aggregator - Unified daily_tech_digest.json")
    
    print("\n✨ FEATURES:")
    print("-" * 40)
    print("• Sequential execution with timeout protection")
    print("• Graceful error handling - continues if one scraper fails")
    print("• Comprehensive logging and progress tracking")
    print("• Clean JSON output with essential fields only")
    print("• AI-powered content selection for quality")
    print("• Single command execution for automation")
    
    if len(existing_files) >= 4:
        print(f"\n🎉 READY TO GO!")
        print("You already have output files. The master scraper will refresh them.")
    else:
        print(f"\n🚀 GET STARTED:")
        print("Run 'python master_scraper.py' to generate fresh content!")

if __name__ == "__main__":
    main()
