#!/usr/bin/env python3
"""
TJI Automation Project Setup Script

This script helps users set up the TJI automation project quickly by:
1. Checking Python version compatibility
2. Installing required dependencies
3. Setting up configuration files
4. Verifying the installation
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   TJI Automation requires Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    
    try:
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print("❌ requirements.txt not found")
            return False
        
        # Install packages
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_config():
    """Set up configuration files."""
    print("\n⚙️ Setting up configuration...")
    
    try:
        # Check if template exists
        template_path = Path('config/api_config_template.json')
        config_path = Path('config/api_config.json')
        
        if not template_path.exists():
            print("❌ API config template not found")
            return False
        
        # Copy template if config doesn't exist
        if not config_path.exists():
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            
            with open(config_path, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            print("✅ Created config/api_config.json from template")
            print("⚠️  Please edit config/api_config.json with your actual API keys")
        else:
            print("✅ Configuration file already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up configuration: {e}")
        return False

def verify_structure():
    """Verify the project structure is correct."""
    print("\n🔍 Verifying project structure...")
    
    required_dirs = [
        'scrapers',
        'processors',
        'data',
        'messaging',
        'tests',
        'docs',
        'config'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
        else:
            print(f"✅ {directory}/ directory exists")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    # Check key files
    key_files = [
        'processors/run_daily_digest_pipeline.py',
        'scrapers/demo_tech_news.py',
        'config/config.py',
        'README.md'
    ]
    
    missing_files = []
    for file_path in key_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ Project structure is correct")
    return True

def test_imports():
    """Test that key modules can be imported."""
    print("\n🧪 Testing imports...")
    
    try:
        # Test config import
        sys.path.append('config')
        import config
        print("✅ Config module can be imported")
        
        # Test that data directory is accessible
        if os.path.exists('data') and os.access('data', os.W_OK):
            print("✅ Data directory is writable")
        else:
            print("❌ Data directory is not writable")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def display_usage_instructions():
    """Display usage instructions."""
    print("\n📋 USAGE INSTRUCTIONS")
    print("=" * 50)
    print("1. Configure API keys:")
    print("   Edit config/api_config.json with your actual API keys")
    print("   - Groq API key for AI content selection")
    print("   - TinyURL API key for URL shortening")
    print("   - Twilio credentials for WhatsApp messaging")
    print()
    print("2. Run the complete pipeline:")
    print("   python processors/run_daily_digest_pipeline.py")
    print()
    print("3. Run individual components:")
    print("   python scrapers/demo_tech_news.py")
    print("   python scrapers/internship_scraper.py")
    print("   python processors/daily_tech_aggregator.py")
    print("   python messaging/twillo.py")
    print()
    print("4. Run tests:")
    print("   python tests/test_twilio_integration.py")
    print("   python tests/test_pipeline_import.py")
    print()
    print("📚 Documentation:")
    print("   - Main README: README.md")
    print("   - Component docs: docs/README_*.md")

def main():
    """Main setup function."""
    print("🚀 TJI AUTOMATION PROJECT SETUP")
    print("=" * 50)
    print("Setting up the TJI daily tech digest automation...\n")
    
    setup_steps = [
        ("Python Version Check", check_python_version),
        ("Project Structure Verification", verify_structure),
        ("Dependency Installation", install_dependencies),
        ("Configuration Setup", setup_config),
        ("Import Testing", test_imports)
    ]
    
    passed_steps = 0
    total_steps = len(setup_steps)
    
    for step_name, step_func in setup_steps:
        try:
            if step_func():
                passed_steps += 1
                print(f"✅ {step_name}: SUCCESS")
            else:
                print(f"❌ {step_name}: FAILED")
                break
        except Exception as e:
            print(f"❌ {step_name}: ERROR - {e}")
            break
    
    print("\n" + "=" * 50)
    print(f"📊 SETUP RESULTS: {passed_steps}/{total_steps} steps completed")
    
    if passed_steps == total_steps:
        print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("✅ TJI Automation is ready to use")
        display_usage_instructions()
        return True
    else:
        print(f"\n❌ SETUP INCOMPLETE")
        print(f"Please resolve the issues above and run setup again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
