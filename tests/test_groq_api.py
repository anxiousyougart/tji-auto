#!/usr/bin/env python3
"""
Quick test script to check if Groq API is working
"""

import os
import logging
from groq import Groq

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_groq_api():
    """Test if Groq API is working with the configured API key."""
    
    print("🔍 TESTING GROQ API")
    print("=" * 50)
    
    # Try to get API key from multiple sources
    api_key = None
    
    # 1. Environment variable
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print("✅ Found API key in environment variable")
    else:
        print("❌ No API key in environment variable")
    
    # 2. Try config.py
    if not api_key:
        try:
            from ..config.config import get_groq_api_key
            api_key = get_groq_api_key()
            if api_key:
                print("✅ Found API key in config.py")
        except ImportError:
            print("❌ Could not import from config.py")
    
    # 3. Fallback key
    if not api_key:
        api_key = "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"
        print("⚠️  Using fallback API key")
    
    if not api_key:
        print("❌ No API key available!")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...")
    
    # Test the API
    try:
        print("\n🚀 Testing API connection...")
        client = Groq(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Say 'Hello, API is working!' in exactly 5 words."}
            ],
            model="llama3-8b-8192",
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ API Response: {result}")
        print("🎉 GROQ API IS WORKING!")
        return True
        
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
        print("💡 Possible issues:")
        print("   - Invalid API key")
        print("   - Network connectivity issues")
        print("   - API service temporarily unavailable")
        print("   - Rate limiting")
        return False

if __name__ == "__main__":
    success = test_groq_api()
    
    if not success:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check your internet connection")
        print("2. Verify your API key at: https://console.groq.com/")
        print("3. Try again in a few minutes (rate limiting)")
        print("4. Check Groq service status")
    
    print(f"\n📊 Result: {'SUCCESS' if success else 'FAILED'}")
