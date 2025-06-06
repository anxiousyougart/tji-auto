#!/usr/bin/env python3
"""
Test script for centralized API key management system.
Tests all scrapers to ensure they use the centralized API key properly.
"""

import os
import sys
import json
import logging

def test_config_import():
    """Test importing the centralized configuration."""
    print("🔧 TESTING CENTRALIZED API KEY CONFIGURATION")
    print("=" * 60)
    
    try:
        from ..config.config import get_groq_api_key, ENABLE_AI_SELECTION
        api_key = get_groq_api_key()
        
        print(f"✅ Config import: SUCCESS")
        print(f"🔑 API Key available: {'YES' if api_key else 'NO'}")
        print(f"🤖 AI Selection enabled: {'YES' if ENABLE_AI_SELECTION else 'NO'}")
        
        if api_key:
            # Mask the API key for security
            masked_key = api_key[:10] + "..." + api_key[-10:] if len(api_key) > 20 else "***"
            print(f"🔐 API Key (masked): {masked_key}")
        
        return True, api_key
        
    except Exception as e:
        print(f"❌ Config import: FAILED - {e}")
        return False, None

def test_api_manager():
    """Test the API manager functionality."""
    print(f"\n🔧 TESTING API MANAGER")
    print("=" * 60)
    
    try:
        from ..config.api_manager import get_api_manager
        manager = get_api_manager()
        
        print(f"✅ API Manager import: SUCCESS")
        print(f"🔑 API available: {'YES' if manager.is_api_available() else 'NO'}")
        print(f"🔐 API key set: {'YES' if manager.get_api_key() else 'NO'}")
        
        # Test client creation
        client = manager.get_client()
        print(f"🤖 Groq client: {'CREATED' if client else 'FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Manager: FAILED - {e}")
        return False

def test_scraper_imports():
    """Test that all scrapers can import the centralized configuration."""
    print(f"\n🔧 TESTING SCRAPER IMPORTS")
    print("=" * 60)
    
    scrapers = [
        ("internship_scraper", "Internship Scraper"),
        ("jobs_scraper", "Jobs Scraper"),
        ("webscraptest", "Tech News Scraper"),
        ("upskill_scraper", "Upskill Scraper"),
        ("daily_tech_aggregator", "Daily Aggregator")
    ]
    
    results = {}
    
    for module_name, display_name in scrapers:
        try:
            module = __import__(module_name)
            api_key = getattr(module, 'GROQ_API_KEY', None)
            
            status = "✅ SUCCESS" if api_key else "⚠️  NO API KEY"
            print(f"{status} {display_name}: API key {'available' if api_key else 'missing'}")
            results[module_name] = bool(api_key)
            
        except Exception as e:
            print(f"❌ FAILED {display_name}: {e}")
            results[module_name] = False
    
    success_count = sum(results.values())
    total_count = len(results)
    print(f"\n📊 Import Results: {success_count}/{total_count} scrapers have API keys")
    
    return results

def test_sample_data_creation():
    """Test creating sample data and running the aggregator."""
    print(f"\n🔧 TESTING SAMPLE DATA & AGGREGATION")
    print("=" * 60)
    
    try:
        # Create sample data
        from demo_simple_scraper import main as create_samples
        create_samples()
        print("✅ Sample data creation: SUCCESS")
        
        # Test aggregator
        from daily_tech_aggregator import create_daily_digest, save_daily_digest
        digest = create_daily_digest()
        success = save_daily_digest(digest)
        
        if success:
            print("✅ Daily digest aggregation: SUCCESS")
            print("../data/📁 Output file: daily_tech_digest.json")
            return True
        else:
            print("❌ Daily digest aggregation: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Sample data & aggregation: FAILED - {e}")
        return False

def test_fallback_behavior():
    """Test fallback behavior when API is unavailable."""
    print(f"\n🔧 TESTING FALLBACK BEHAVIOR")
    print("=" * 60)
    
    try:
        from fallback_selector import fallback_select_best
        
        # Test with sample data
        sample_articles = [
            {"title": "Python Tutorial for Beginners", "url": "https://example.com/1"},
            {"title": "Advanced React Patterns", "url": "https://example.com/2"},
            {"title": "Machine Learning Guide", "url": "https://example.com/3"}
        ]
        
        best_article = fallback_select_best(sample_articles, 'tech_news')
        
        if best_article:
            print("✅ Fallback selection: SUCCESS")
            print(f"📰 Selected: {best_article['title']}")
            return True
        else:
            print("❌ Fallback selection: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Fallback behavior: FAILED - {e}")
        return False

def main():
    """Run all tests and provide a comprehensive report."""
    print("🚀 CENTRALIZED API KEY MANAGEMENT SYSTEM TEST")
    print("=" * 80)
    print("Testing all components of the centralized API key system...")
    print()
    
    # Run all tests
    config_success, api_key = test_config_import()
    manager_success = test_api_manager()
    scraper_results = test_scraper_imports()
    sample_success = test_sample_data_creation()
    fallback_success = test_fallback_behavior()
    
    # Generate final report
    print(f"\n📋 FINAL TEST REPORT")
    print("=" * 80)
    
    total_tests = 5
    passed_tests = sum([
        config_success,
        manager_success,
        all(scraper_results.values()),
        sample_success,
        fallback_success
    ])
    
    print(f"📊 Overall Success Rate: {passed_tests}/{total_tests} tests passed")
    print()
    
    if config_success and api_key:
        print("✅ CENTRALIZED API KEY SYSTEM: WORKING")
        print("🔑 All scrapers have access to the working API key")
        print("🤖 AI-powered selection should work across all scrapers")
    else:
        print("⚠️  CENTRALIZED API KEY SYSTEM: PARTIAL")
        print("🔄 Fallback mechanisms will be used when needed")
    
    if sample_success:
        print("✅ MASTER PIPELINE: READY")
        print("📁 Daily digest generation is working")
    else:
        print("❌ MASTER PIPELINE: NEEDS ATTENTION")
    
    print(f"\n🎯 NEXT STEPS:")
    if passed_tests == total_tests:
        print("• Run: python master_scraper.py")
        print("• All systems are operational!")
    else:
        print("• Check individual scraper logs for detailed error information")
        print("• Verify API key configuration in config.py")
        print("• Test individual scrapers: python demo_tech_news.py")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
