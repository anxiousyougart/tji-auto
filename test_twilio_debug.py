#!/usr/bin/env python3
"""
Debug script for Twilio WhatsApp integration
"""

import os
import sys
import json

def test_twilio_imports():
    """Test if Twilio can be imported."""
    print("🧪 Testing Twilio imports...")
    try:
        from twilio.rest import Client
        print("✅ Twilio library imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Twilio: {e}")
        print("💡 Install with: pip install twilio")
        return False

def test_message_file():
    """Test if message file exists and is readable."""
    print("\n🧪 Testing message file...")
    
    message_file = '../data/tji_daily_message.json'
    
    if not os.path.exists(message_file):
        print(f"❌ Message file not found: {message_file}")
        return False
    
    try:
        with open(message_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        message_body = data.get("drafted_message", "")
        if message_body:
            print(f"✅ Message file loaded successfully")
            print(f"📝 Message length: {len(message_body)} characters")
            print(f"📄 Message preview: {message_body[:100]}...")
            return True
        else:
            print(f"❌ No message content found in file")
            return False
            
    except Exception as e:
        print(f"❌ Error reading message file: {e}")
        return False

def test_twilio_config():
    """Test Twilio configuration."""
    print("\n🧪 Testing Twilio configuration...")
    
    # Test environment variables
    env_vars = {
        'TWILIO_ACCOUNT_SID': os.getenv('TWILIO_ACCOUNT_SID'),
        'TWILIO_AUTH_TOKEN': os.getenv('TWILIO_AUTH_TOKEN'),
        'TWILIO_PHONE_FROM': os.getenv('TWILIO_PHONE_FROM'),
        'TWILIO_PHONE_TO': os.getenv('TWILIO_PHONE_TO')
    }
    
    print("Environment variables:")
    for key, value in env_vars.items():
        if value:
            print(f"✅ {key}: Set (length: {len(value)})")
        else:
            print(f"❌ {key}: Not set")
    
    # Test fallback config
    fallback_config = {
        'account_sid': 'AC185a7783037edc716eaff3ca28a5993c',
        'auth_token': 'a48df63098f045e09f4db5ce5c881207',
        'phone_from': 'whatsapp:+14155238886',
        'phone_to': 'whatsapp:+918179399260'
    }
    
    print("\nFallback configuration:")
    for key, value in fallback_config.items():
        print(f"✅ {key}: {value}")
    
    return True

def test_twilio_client():
    """Test Twilio client creation."""
    print("\n🧪 Testing Twilio client creation...")
    
    try:
        from twilio.rest import Client
        
        # Use fallback config for testing
        account_sid = 'AC185a7783037edc716eaff3ca28a5993c'
        auth_token = 'a48df63098f045e09f4db5ce5c881207'
        
        client = Client(account_sid, auth_token)
        print("✅ Twilio client created successfully")
        
        # Test account info (this will validate credentials)
        try:
            account = client.api.accounts(account_sid).fetch()
            print(f"✅ Account validated: {account.friendly_name}")
            return True
        except Exception as e:
            print(f"❌ Account validation failed: {e}")
            print("💡 This might be due to invalid credentials")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create Twilio client: {e}")
        return False

def test_simple_send():
    """Test sending a simple message."""
    print("\n🧪 Testing simple message send...")
    
    try:
        from twilio.rest import Client
        
        # Configuration
        account_sid = 'AC185a7783037edc716eaff3ca28a5993c'
        auth_token = 'a48df63098f045e09f4db5ce5c881207'
        phone_from = 'whatsapp:+14155238886'
        phone_to = 'whatsapp:+918179399260'
        
        client = Client(account_sid, auth_token)
        
        # Simple test message
        test_message = "🧪 Test message from TJI automation system"
        
        print(f"📤 Sending test message...")
        print(f"From: {phone_from}")
        print(f"To: {phone_to}")
        print(f"Message: {test_message}")
        
        message = client.messages.create(
            from_=phone_from,
            to=phone_to,
            body=test_message
        )
        
        print(f"✅ Message sent successfully!")
        print(f"📱 Message SID: {message.sid}")
        print(f"📊 Status: {message.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test message: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Common error explanations
        if "HTTP 401" in str(e):
            print("💡 This is an authentication error - check your Twilio credentials")
        elif "HTTP 400" in str(e):
            print("💡 This might be a phone number format issue")
        elif "not a valid WhatsApp number" in str(e):
            print("💡 The recipient number needs to be verified in Twilio console")
        
        return False

def main():
    """Main test function."""
    print("🧪 TWILIO WHATSAPP DEBUG TEST")
    print("=" * 50)
    
    tests = [
        ("Twilio Import", test_twilio_imports),
        ("Message File", test_message_file),
        ("Twilio Config", test_twilio_config),
        ("Twilio Client", test_twilio_client),
        ("Simple Send", test_simple_send)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("Twilio integration should be working")
    else:
        print(f"\n❌ {total - passed} TESTS FAILED")
        print("Check the errors above to fix Twilio integration")

if __name__ == "__main__":
    main()
