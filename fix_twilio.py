#!/usr/bin/env python3
"""
Quick fix script for Twilio WhatsApp integration
"""

import subprocess
import sys
import os

def main():
    print("🔧 FIXING TWILIO WHATSAPP INTEGRATION")
    print("=" * 50)
    
    # Step 1: Install Twilio
    print("📦 Installing Twilio...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "twilio"], check=True)
        print("✅ Twilio installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Twilio")
        print("💡 Try running manually: pip install twilio")
        return
    
    # Step 2: Test the fixed script
    print("\n📱 Testing WhatsApp message sending...")
    
    # Change to messaging directory
    os.chdir("messaging")
    
    try:
        result = subprocess.run([sys.executable, "twillo.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Twilio script executed successfully!")
            print("Output:", result.stdout)
        else:
            print("❌ Twilio script failed!")
            print("Error:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Script timed out - this might be normal for network operations")
    except Exception as e:
        print(f"❌ Error running script: {e}")
    
    print("\n💡 If you're still having issues:")
    print("1. Make sure you have internet connection")
    print("2. Verify your Twilio credentials are correct")
    print("3. Check that your WhatsApp number is verified in Twilio console")
    print("4. Try running: cd messaging && python twillo.py")

if __name__ == "__main__":
    main()
