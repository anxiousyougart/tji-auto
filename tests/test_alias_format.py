#!/usr/bin/env python3



import requests
import json
import time

def test_alias_format(alias):
    """Test a specific alias format."""
    print(f"🔑 Testing alias format: '{alias}'")
    
    api_key = 'Rmg2VwW1ZBaL9LP3myDkCtq7AzFXWg8csW5CwXIGmBW5iAkUy3gn8mmwmmZq'
    api_endpoint = 'https://api.tinyurl.com/create'
    
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    payload = {
        'url': 'https://www.example.com',
        'domain': 'tinyurl.com',
        'alias': alias
    }
    
    try:
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            shortened_url = result.get('data', {}).get('tiny_url')
            print(f"✅ Success! URL: {shortened_url}")
            return True
        else:
            try:
                error_data = response.json()
                errors = error_data.get('errors', [])
                print(f"❌ Failed: {errors}")
            except:
                print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Test different alias formats."""
    print("🧪 TINYURL ALIAS FORMAT TESTS")
    print("=" * 50)
    
    # Test different formats
    test_formats = [
        'technews-tji-1',
        'intern-tji-1', 
        'job-tji-1',
        'upskill-tji-1',
        'technewstji1',
        'interntji1',
        'jobtji1',
        'upskilltji1',
        f'tech{int(time.time())}',
        f'intern{int(time.time())}',
        f'job{int(time.time())}',
        f'upskill{int(time.time())}'
    ]
    
    results = {}
    
    for alias in test_formats:
        results[alias] = test_alias_format(alias)
        print()
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("📊 RESULTS SUMMARY")
    print("=" * 30)
    
    successful = []
    failed = []
    
    for alias, success in results.items():
        if success:
            successful.append(alias)
            print(f"✅ {alias}")
        else:
            failed.append(alias)
            print(f"❌ {alias}")
    
    print(f"\nSuccessful formats: {len(successful)}/{len(test_formats)}")
    
    if successful:
        print(f"\n🎉 Working alias formats found!")
        print("Recommended format for implementation:")
        print(f"  • {successful[0]}")
    else:
        print(f"\n⚠️  No working alias formats found. Using auto-generated aliases.")

if __name__ == "__main__":
    main()
