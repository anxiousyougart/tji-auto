#!/usr/bin/env python3
"""
Test script for TinyURL integration

This script tests the TinyURL shortening functionality with sample data
to ensure everything works correctly before running on real data.

"""

import json
import os
import sys
import time
import requests
from datetime import datetime

def test_api_connectivity():
    """Test basic connectivity to TinyURL API."""
    print("🔗 Testing TinyURL API connectivity...")
    
    try:
        # Test with a simple request (this might fail due to auth, but tests connectivity)
        response = requests.get("https://api.tinyurl.com", timeout=10)
        print(f"✅ TinyURL API is reachable (status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ TinyURL API connectivity test failed: {e}")
        return False

def test_api_authentication():
    """Test TinyURL API authentication with the configured key."""
    print("🔑 Testing TinyURL API authentication...")
    
    try:
        from ..config.config import TINYURL_CONFIG
        api_key = TINYURL_CONFIG['api_key']
        
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Test with a simple URL
        payload = {
            'url': 'https://www.google.com',
            'domain': 'tinyurl.com',
            'alias': f'test_tji_{int(time.time())}'  # Unique alias
        }
        
        response = requests.post(
            TINYURL_CONFIG['api_endpoint'],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            shortened_url = result.get('data', {}).get('tiny_url')
            if shortened_url:
                print(f"✅ Authentication successful! Test URL: {shortened_url}")
                return True
            else:
                print(f"⚠️  Authentication worked but no URL returned: {result}")
                return False
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
            
    except ImportError:
        print("❌ Could not import configuration. Check config.py exists.")
        return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def create_test_digest():
    """Create a test daily_tech_digest.json file."""
    print("📄 Creating test digest file...")
    
    test_data = {
        "daily_tech_digest": {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "test_mode": True
            },
            "content": {
                "tech_news": {
                    "title": "Test Tech News Article",
                    "url": "https://www.example.com/tech-news-article-with-very-long-url-for-testing-purposes"
                },
                "internships": {
                    "title": "Test Software Engineer Intern Position",
                    "company": "TestCorp",
                    "url": "https://www.example.com/internship-posting-with-extremely-long-url-that-needs-shortening"
                },
                "jobs": {
                    "title": "Test Junior Developer Position",
                    "company": "StartupTest",
                    "url": "https://www.example.com/job-posting-with-very-long-url-for-testing-url-shortening-functionality"
                },
                "upskill_articles": {
                    "title": "Test Programming Tutorial",
                    "url": "https://www.example.com/programming-tutorial-with-long-url-for-testing-shortening-service"
                }
            }
        }
    }
    
    try:
        with open('../data/daily_tech_digest.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        print("✅ Test digest created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create test digest: {e}")
        return False

def test_shortener_script():
    """Test the TinyURL shortener script."""
    print("🔧 Testing TinyURL shortener script...")
    
    try:
        # Import and run the shortener
        from tinyurl_shortener import TinyURLShortener
        
        shortener = TinyURLShortener()
        
        # Test loading input data
        data = shortener.load_input_data()
        if not data:
            print("❌ Failed to load test data")
            return False
        
        # Test URL extraction
        urls = shortener.extract_urls_from_data(data)
        if not urls:
            print("❌ Failed to extract URLs from test data")
            return False
        
        print(f"✅ Successfully extracted {len(urls)} URLs for testing")
        
        # Test alias generation
        for category in ['tech_news', 'internships', 'jobs', 'upskill_articles']:
            alias = shortener.generate_alias(category)
            print(f"  • {category}: {alias}")
        
        print("✅ Alias generation working correctly")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import TinyURL shortener: {e}")
        return False
    except Exception as e:
        print(f"❌ Shortener script test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files."""
    print("🧹 Cleaning up test files...")
    
    test_files = [
        '../data/daily_tech_digest.json',
        '../data/shortened_urls_digest.json',
        '../data/tinyurl_shortener.log'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  • Removed {file}")
            except Exception as e:
                print(f"  • Failed to remove {file}: {e}")

def main():
    """Run all tests."""
    print("🧪 TINYURL INTEGRATION TESTS")
    print("=" * 50)
    print("Testing TinyURL shortening integration...")
    print()
    
    tests = [
        ("API Connectivity", test_api_connectivity),
        ("API Authentication", test_api_authentication),
        ("Test Digest Creation", create_test_digest),
        ("Shortener Script", test_shortener_script)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"💥 Test crashed: {e}")
            results[test_name] = False
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! TinyURL integration is ready.")
        print("\nNext steps:")
        print("  • Run: python tinyurl_shortener.py")
        print("  • Or: python demo_tinyurl_shortener.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("  • Verify internet connection")
        print("  • Check API key in config.py")
        print("  • Ensure all dependencies are installed")
    
    # Ask about cleanup
    print(f"\n🧹 Clean up test files? (y/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            cleanup_test_files()
    except KeyboardInterrupt:
        print("\nSkipping cleanup.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
