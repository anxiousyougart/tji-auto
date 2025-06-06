#!/usr/bin/env python3
"""
Simple Demo Scraper - Works Without API

This is a simplified version that demonstrates the scraping pipeline
without requiring external APIs. Creates sample output files for testing.

Author: Augment Agent
Date: 2025-01-25
"""

import json
import logging
import os
from datetime import datetime, timedelta
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_sample_tech_news():
    """Create sample tech news data."""
    sample_articles = [
        {
            "title": "New AI Framework Released for Developers",
            "url": "https://example.com/ai-framework",
            "date": datetime.now().isoformat(),
            "source": "Tech News Demo"
        },
        {
            "title": "Breakthrough in Quantum Computing Announced",
            "url": "https://example.com/quantum-breakthrough", 
            "date": (datetime.now() - timedelta(hours=2)).isoformat(),
            "source": "Tech News Demo"
        },
        {
            "title": "Open Source Machine Learning Library Gains Popularity",
            "url": "https://example.com/ml-library",
            "date": (datetime.now() - timedelta(hours=5)).isoformat(),
            "source": "Tech News Demo"
        }
    ]
    
    # Select the most recent one (simple rule-based selection)
    selected = sample_articles[0]
    
    result = {
        "title": selected["title"],
        "url": selected["url"],
        "selection_method": "demo_fallback",
        "selection_reasoning": "Selected most recent article from demo data",
        "timestamp": datetime.now().isoformat()
    }
    
    return result

def create_sample_internships():
    """Create sample internship data."""
    sample_internships = [
        {
            "title": "Software Development Intern",
            "company": "Tech Innovations Ltd",
            "url": "https://example.com/internship1",
            "location": "Hyderabad",
            "description": "Work on web development projects using React and Node.js"
        },
        {
            "title": "Data Science Intern",
            "company": "Analytics Pro",
            "url": "https://example.com/internship2", 
            "location": "Hyderabad",
            "description": "Analyze data using Python and machine learning techniques"
        },
        {
            "title": "Mobile App Development Intern",
            "company": "Mobile Solutions Inc",
            "url": "https://example.com/internship3",
            "location": "Hyderabad", 
            "description": "Develop Android and iOS applications"
        }
    ]
    
    # Select based on simple scoring (prefer software development)
    selected = sample_internships[0]  # Software development has highest priority
    
    result = {
        "title": selected["title"],
        "company": selected["company"],
        "url": selected["url"],
        "selection_method": "demo_fallback",
        "selection_reasoning": "Selected software development internship (highest priority for CS students)",
        "timestamp": datetime.now().isoformat()
    }
    
    return result

def create_sample_jobs():
    """Create sample job data."""
    sample_jobs = [
        {
            "title": "Junior Software Engineer",
            "company": "StartupTech",
            "url": "https://example.com/job1",
            "experience": "0-1 years",
            "description": "Entry-level position for fresh graduates in software development"
        },
        {
            "title": "Associate Developer",
            "company": "Enterprise Solutions",
            "url": "https://example.com/job2",
            "experience": "0-2 years", 
            "description": "Join our development team working on enterprise applications"
        },
        {
            "title": "Graduate Trainee - IT",
            "company": "Global Tech Corp",
            "url": "https://example.com/job3",
            "experience": "Fresher",
            "description": "Comprehensive training program for engineering graduates"
        }
    ]
    
    # Select entry-level position
    selected = sample_jobs[0]  # Junior Software Engineer
    
    result = {
        "title": selected["title"],
        "company": selected["company"],
        "url": selected["url"],
        "selection_method": "demo_fallback",
        "selection_reasoning": "Selected junior software engineer position (best for fresh graduates)",
        "timestamp": datetime.now().isoformat()
    }
    
    return result

def create_sample_upskill():
    """Create sample upskill article data."""
    sample_articles = [
        {
            "title": "Complete Guide to React Hooks for Beginners",
            "url": "https://example.com/react-hooks-guide",
            "source": "Dev Learning",
            "description": "Step-by-step tutorial on using React Hooks effectively"
        },
        {
            "title": "Python Data Science Tutorial: From Basics to Advanced",
            "url": "https://example.com/python-data-science",
            "source": "Data Academy",
            "description": "Comprehensive tutorial covering pandas, numpy, and matplotlib"
        },
        {
            "title": "Building Your First REST API with Node.js",
            "url": "https://example.com/nodejs-api-tutorial",
            "source": "Backend Masters",
            "description": "Learn to create RESTful APIs using Express.js and MongoDB"
        }
    ]
    
    # Select based on popularity (React is very popular)
    selected = sample_articles[0]  # React tutorial
    
    result = {
        "title": selected["title"],
        "url": selected["url"],
        "selection_method": "demo_fallback",
        "selection_reasoning": "Selected React tutorial (high demand skill for developers)",
        "timestamp": datetime.now().isoformat()
    }
    
    return result

def create_output_files():
    """Create all output files with sample data."""
    
    print("🎭 SIMPLE DEMO SCRAPER")
    print("=" * 50)
    print("Creating sample output files for testing...")
    
    # Create tech news output
    try:
        tech_news = create_sample_tech_news()
        with open("../data/ai_selected_article.json", "w", encoding="utf-8") as f:
            json.dump(tech_news, f, indent=2, ensure_ascii=False)
        print("../data/✅ Created ai_selected_article.json")
    except Exception as e:
        print(f"❌ Failed to create tech news file: {e}")
    
    # Create internship output
    try:
        internship = create_sample_internships()
        with open("../data/selected_internship.json", "w", encoding="utf-8") as f:
            json.dump(internship, f, indent=2, ensure_ascii=False)
        print("../data/✅ Created selected_internship.json")
    except Exception as e:
        print(f"❌ Failed to create internship file: {e}")
    
    # Create job output
    try:
        job = create_sample_jobs()
        with open("../data/selected_job.json", "w", encoding="utf-8") as f:
            json.dump(job, f, indent=2, ensure_ascii=False)
        print("../data/✅ Created selected_job.json")
    except Exception as e:
        print(f"❌ Failed to create job file: {e}")
    
    # Create upskill output
    try:
        upskill = create_sample_upskill()
        with open("../data/ai_selected_upskill_article.json", "w", encoding="utf-8") as f:
            json.dump(upskill, f, indent=2, ensure_ascii=False)
        print("../data/✅ Created ai_selected_upskill_article.json")
    except Exception as e:
        print(f"❌ Failed to create upskill file: {e}")
    
    print("\n📋 SAMPLE DATA CREATED")
    print("-" * 30)
    print("• Tech News: AI Framework Release")
    print("• Internship: Software Development @ Tech Innovations")
    print("• Job: Junior Software Engineer @ StartupTech")
    print("• Upskill: React Hooks Tutorial")
    
    print(f"\n🔄 NEXT STEPS:")
    print("1. Run: python daily_tech_aggregator.py")
    print("../data/2. Check: daily_tech_digest.json")
    print("3. View: python demo_daily_digest.py")

def main():
    """Main function."""
    create_output_files()

if __name__ == "__main__":
    main()
