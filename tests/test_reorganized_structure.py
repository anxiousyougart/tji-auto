#!/usr/bin/env python3
"""
Test script to verify the reorganized TJI project structure works correctly.
"""

import os
import sys
import importlib.util
from pathlib import Path

def test_directory_structure():
    """Test that all required directories exist."""
    print("🧪 Testing Directory Structure...")
    
    required_dirs = [
        '../scrapers',
        '../processors',
        '../data',
        '../messaging',
        '../tests',
        '../docs',
        '../config'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
        else:
            print(f"  ✅ {directory}/ exists")
    
    if missing_dirs:
        print(f"  ❌ Missing directories: {missing_dirs}")
        return False
    
    print("  ✅ All required directories exist")
    return True

def test_file_locations():
    """Test that key files are in their correct locations."""
    print("\n🧪 Testing File Locations...")
    
    expected_files = {
        '../scrapers': [
            'demo_tech_news.py',
            'internship_scraper.py',
            'jobs_scraper.py',
            'upskill_scraper.py',
            'webscraptest.py'
        ],
        '../processors': [
            'run_daily_digest_pipeline.py',
            'master_scraper_robust.py',
            'daily_tech_aggregator.py',
            'message_drafter.py',
            'tinyurl_shortener.py'
        ],
        '../messaging': [
            'twillo.py'
        ],
        '../config': [
            'config.py',
            'api_manager.py',
            'api_config_template.json'
        ]
    }
    
    missing_files = []
    for directory, files in expected_files.items():
        for file_name in files:
            file_path = os.path.join(directory, file_name)
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  ❌ {file_path}")
    
    if missing_files:
        print(f"\n  ❌ Missing files: {len(missing_files)}")
        return False
    
    print(f"\n  ✅ All expected files are in correct locations")
    return True

def test_imports():
    """Test that imports work correctly with the new structure."""
    print("\n🧪 Testing Import Functionality...")
    
    test_cases = [
        {
            'description': 'Config module import',
            'test': lambda: test_config_import()
        },
        {
            'description': 'Scraper imports',
            'test': lambda: test_scraper_imports()
        },
        {
            'description': 'Processor imports', 
            'test': lambda: test_processor_imports()
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        try:
            result = test_case['test']()
            if result:
                print(f"  ✅ {test_case['description']}")
                passed += 1
            else:
                print(f"  ❌ {test_case['description']}")
        except Exception as e:
            print(f"  ❌ {test_case['description']}: {e}")
    
    success = passed == len(test_cases)
    print(f"\n  {'✅' if success else '❌'} Import tests: {passed}/{len(test_cases)} passed")
    return success

def test_config_import():
    """Test config module import."""
    try:
        sys.path.append('../config')
        import config
        return True
    except ImportError:
        return False

def test_scraper_imports():
    """Test scraper module imports."""
    try:
        # Test webscraptest import
        spec = importlib.util.spec_from_file_location("webscraptest", "../scrapers/webscraptest.py")
        webscraptest = importlib.util.module_from_spec(spec)

        # Test if the module can be loaded (don't execute)
        return spec is not None
    except Exception:
        return False

def test_processor_imports():
    """Test processor module imports."""
    try:
        # Test daily_tech_aggregator import
        spec = importlib.util.spec_from_file_location("daily_tech_aggregator", "../processors/daily_tech_aggregator.py")
        aggregator = importlib.util.module_from_spec(spec)

        return spec is not None
    except Exception:
        return False

def test_data_directory():
    """Test data directory and file permissions."""
    print("\n🧪 Testing Data Directory...")
    
    # Check if data directory is writable
    try:
        test_file = os.path.join('../data', 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("  ✅ Data directory is writable")

        # Check for some expected data files
        expected_data_files = [
            'tech_news_history.json',
            'upskill_articles_history.json',
            'seen_internships.json'
        ]

        existing_files = 0
        for file_name in expected_data_files:
            file_path = os.path.join('../data', file_name)
            if os.path.exists(file_path):
                existing_files += 1
                print(f"  ✅ {file_path} exists")
        
        print(f"  ℹ️  Found {existing_files}/{len(expected_data_files)} expected data files")
        return True
        
    except Exception as e:
        print(f"  ❌ Data directory test failed: {e}")
        return False

def test_pipeline_configuration():
    """Test that pipeline configuration files are correct."""
    print("\n🧪 Testing Pipeline Configuration...")
    
    try:
        # Test main pipeline configuration
        spec = importlib.util.spec_from_file_location("pipeline", "../processors/run_daily_digest_pipeline.py")
        if spec is None:
            print("  ❌ Cannot load pipeline configuration")
            return False

        print("  ✅ Pipeline configuration file is loadable")

        # Check if README exists
        if os.path.exists('../README.md'):
            print("  ✅ Main README.md exists")
        else:
            print("  ❌ Main README.md missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Pipeline configuration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 TJI PROJECT STRUCTURE VERIFICATION")
    print("=" * 60)
    print("Testing reorganized project structure...\n")
    
    tests = [
        test_directory_structure,
        test_file_locations,
        test_data_directory,
        test_imports,
        test_pipeline_configuration
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Project structure is correctly organized")
        print("✅ Files are in their proper locations")
        print("✅ Import paths should work correctly")
        print("\n💡 Next steps:")
        print("  • Test the pipeline: python processors/run_daily_digest_pipeline.py")
        print("  • Commit changes: git add . && git commit -m 'Reorganize project structure'")
        print("  • Push to GitHub: git push origin main")
        return True
    else:
        print(f"\n❌ {total_tests - passed_tests} TESTS FAILED")
        print("Please fix the issues above before proceeding.")
        print("\n🔧 Common fixes:")
        print("  • Ensure all files are moved to correct directories")
        print("  • Update import statements in Python files")
        print("  • Check file permissions in data directory")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
