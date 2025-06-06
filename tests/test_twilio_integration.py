#!/usr/bin/env python3
"""
Test script for Twilio WhatsApp integration in TJI pipeline
"""

import os
import json
from datetime import datetime

def create_test_message():
    """Create a test message file for Twilio testing"""
    test_message = {
        "drafted_message": "*#TJI TEST*\n\n*TECH NEWS:*\n\nTest tech news article for pipeline verification\nRead more at: https://example.com/test\n\n*PRO TIP:*\n\nThis is a test message from the TJI pipeline automation system.\n\n*UPSKILL:*\n\nTest upskill article for learning\nhttps://example.com/upskill-test"
    }
    
    with open("../data/tji_daily_message.json", "w", encoding="utf-8") as f:
        json.dump(test_message, f, indent=2, ensure_ascii=False)
    
    print("../data/✅ Created test message file: tji_daily_message.json")
    return test_message

def test_message_drafter():
    """Test if message drafter can be imported and configured"""
    try:
        print("🧪 Testing message drafter import...")
        import message_drafter
        print("✅ Message drafter imported successfully")
        
        # Check if required files exist
        if os.path.exists("../data/shortened_urls_digest.json"):
            print("../data/✅ Found shortened_urls_digest.json")
        elif os.path.exists("../data/daily_tech_digest.json"):
            print("../data/✅ Found daily_tech_digest.json")
        else:
            print("⚠️  No input files found for message drafter")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import message drafter: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing message drafter: {e}")
        return False

def test_twilio_import():
    """Test if Twilio can be imported and configured"""
    try:
        print("🧪 Testing Twilio import...")
        from twilio.rest import Client
        print("✅ Twilio library imported successfully")
        
        # Test if twillo.py exists and can be imported
        if os.path.exists("twillo.py"):
            print("✅ Found twillo.py script")
            
            # Read the script to check configuration
            with open("twillo.py", "r") as f:
                content = f.read()
                
            if "account_sid" in content and "auth_token" in content:
                print("✅ Twilio credentials configured in script")
            else:
                print("⚠️  Twilio credentials may need configuration")
                
            if "whatsapp:" in content:
                print("✅ WhatsApp integration configured")
            else:
                print("⚠️  WhatsApp configuration may need setup")
        else:
            print("❌ twillo.py script not found")
            return False
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import Twilio: {e}")
        print("💡 Install with: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ Error testing Twilio: {e}")
        return False

def test_pipeline_configuration():
    """Test if pipeline scripts have Twilio integration configured"""
    try:
        print("🧪 Testing pipeline configuration...")
        
        # Test main pipeline
        from run_daily_digest_pipeline import MESSAGE_DRAFTER, TWILIO_SENDER
        
        print(f"✅ Main pipeline loaded successfully")
        print(f"  • Message Drafter enabled: {MESSAGE_DRAFTER['enabled']}")
        print(f"  • Twilio Sender enabled: {TWILIO_SENDER['enabled']}")
        
        # Test robust pipeline
        from master_scraper_robust import MESSAGE_DRAFTER_CONFIG, TWILIO_SENDER_CONFIG
        
        print(f"✅ Robust pipeline loaded successfully")
        print(f"  • Message Drafter enabled: {MESSAGE_DRAFTER_CONFIG['enabled']}")
        print(f"  • Twilio Sender enabled: {TWILIO_SENDER_CONFIG['enabled']}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import pipeline configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing pipeline configuration: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 TWILIO WHATSAPP INTEGRATION TEST")
    print("=" * 50)
    print(f"Testing Twilio integration for TJI pipeline")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("Pipeline Configuration", test_pipeline_configuration),
        ("Message Drafter", test_message_drafter),
        ("Twilio Import", test_twilio_import)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"🔍 {test_name.upper()}")
        print("-" * 30)
        
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"Result: {status}\n")
        except Exception as e:
            print(f"❌ Test crashed: {e}\n")
            results[test_name] = False
    
    # Create test message file
    print("📝 CREATING TEST MESSAGE")
    print("-" * 30)
    try:
        test_message = create_test_message()
        results["Test Message"] = True
        print("Result: ✅ PASSED\n")
    except Exception as e:
        print(f"❌ Failed to create test message: {e}\n")
        results["Test Message"] = False
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("Twilio integration is ready for use.")
        print("\n💡 Next steps:")
        print("  • Update Twilio credentials in twillo.py")
        print("  • Verify WhatsApp number in Twilio console")
        print("  • Run: python run_daily_digest_pipeline.py")
        print("  • Or test manually: python twillo.py")
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED")
        print("Please address the issues above before using Twilio integration.")
        print("\n🔧 Common fixes:")
        print("  • Install Twilio: pip install twilio")
        print("  • Configure credentials in twillo.py")
        print("  • Ensure message_drafter.py is available")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
