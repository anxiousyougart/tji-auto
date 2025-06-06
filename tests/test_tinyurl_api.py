#!/usr/bin/env python3
"""
Simple test script to verify TinyURL API functionality

This script tests the basic TinyURL API to ensure it works correctly
before running the full shortener.

Author: Augment Agent
Date: 2025-01-25
"""

import requests
import time

def test_tinyurl_api():
    """Test the TinyURL API with a simple URL."""
    print("🔗 Testing TinyURL API...")
    
    test_url = "https://www.google.com"
    api_endpoint = "http://tinyurl.com/api-create.php"
    
    try:
        print(f"📤 Shortening: {test_url}")
        
        params = {'url': test_url}
        response = requests.get(api_endpoint, params=params, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Text: {response.text}")
        
        if response.status_code == 200:
            shortened_url = response.text.strip()
            
            if shortened_url.startswith('http') and 'tinyurl.com' in shortened_url:
                print(f"✅ Success! Shortened URL: {shortened_url}")
                return True
            else:
                print(f"❌ Invalid response: {shortened_url}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multiple_urls():
    """Test shortening multiple URLs."""
    print("\n🔗 Testing multiple URLs...")
    
    test_urls = [
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.python.org"
    ]
    
    api_endpoint = "http://tinyurl.com/api-create.php"
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📤 Test {i}/{len(test_urls)}: {url}")
        
        try:
            params = {'url': url}
            response = requests.get(api_endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                shortened_url = response.text.strip()
                
                if shortened_url.startswith('http') and 'tinyurl.com' in shortened_url:
                    print(f"✅ Success: {shortened_url}")
                    results.append(True)
                else:
                    print(f"❌ Invalid response: {shortened_url}")
                    results.append(False)
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
        
        # Add delay between requests
        if i < len(test_urls):
            time.sleep(1)
    
    success_count = sum(results)
    print(f"\n📊 Results: {success_count}/{len(test_urls)} URLs successfully shortened")
    return success_count == len(test_urls)

def main():
    """Run all tests."""
    print("🧪 TINYURL API TESTS")
    print("=" * 40)
    
    # Test 1: Basic API functionality
    test1_result = test_tinyurl_api()
    
    # Test 2: Multiple URLs
    test2_result = test_multiple_urls()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 20)
    print(f"Basic API Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Multiple URLs Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print(f"\n🎉 All tests passed! TinyURL API is working correctly.")
        print(f"\nYou can now run:")
        print(f"  python tinyurl_shortener.py")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Check your internet connection.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
