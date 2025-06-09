#!/usr/bin/env python3
"""
Test script to verify TinyURL API key and custom alias functionality

This script tests the TinyURL API with the provided API key to ensure
it works correctly with custom aliases.

"""

import requests
import json
import time

def test_tinyurl_api_key():
    """Test the TinyURL API with the provided API key."""
    print("🔑 Testing TinyURL API with provided API key...")
    
    api_key = 'Rmg2VwW1ZBaL9LP3myDkCtq7AzFXWg8csW5CwXIGmBW5iAkUy3gn8mmwmmZq'
    api_endpoint = 'https://api.tinyurl.com/create'
    
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Test with a simple URL and unique alias
    test_url = "https://www.google.com"
    test_alias = f"test_tji_{int(time.time())}"
    
    payload = {
        'url': test_url,
        'domain': 'tinyurl.com',
        'alias': test_alias
    }
    
    try:
        print(f"📤 Testing URL: {test_url}")
        print(f"📤 Testing alias: {test_alias}")
        print(f"📤 API endpoint: {api_endpoint}")
        
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print(f"📊 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Success! Response JSON: {json.dumps(result, indent=2)}")
                
                shortened_url = result.get('data', {}).get('tiny_url')
                if shortened_url:
                    print(f"🔗 Shortened URL: {shortened_url}")
                    
                    # Check if the alias is in the URL
                    if test_alias in shortened_url:
                        print(f"✅ Custom alias '{test_alias}' is in the URL!")
                        return True
                    else:
                        print(f"⚠️  Custom alias '{test_alias}' not found in URL")
                        return False
                else:
                    print(f"❌ No shortened URL in response")
                    return False
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text}")
                return False
                
        elif response.status_code == 401:
            print(f"❌ Authentication failed - API key might be invalid")
            return False
        elif response.status_code == 422:
            print(f"❌ Validation error - check request format")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
            return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_without_alias():
    """Test the TinyURL API without custom alias."""
    print("\n🔑 Testing TinyURL API without custom alias...")
    
    api_key = 'Rmg2VwW1ZBaL9LP3myDkCtq7AzFXWg8csW5CwXIGmBW5iAkUy3gn8mmwmmZq'
    api_endpoint = 'https://api.tinyurl.com/create'
    
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    payload = {
        'url': 'https://www.github.com',
        'domain': 'tinyurl.com'
    }
    
    try:
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success without alias: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Failed without alias: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 TINYURL API KEY TESTS")
    print("=" * 50)
    
    # Test 1: With custom alias
    test1_result = test_tinyurl_api_key()
    
    # Test 2: Without custom alias
    test2_result = test_without_alias()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Custom Alias Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"No Alias Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result:
        print(f"\n🎉 API key is valid and custom aliases work!")
    elif test2_result:
        print(f"\n⚠️  API key is valid but custom aliases might not be supported")
    else:
        print(f"\n❌ API key appears to be invalid or API is not accessible")
    
    return test1_result or test2_result

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
