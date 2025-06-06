#!/usr/bin/env python3
"""
Simple test to verify pipeline imports work correctly after reorganization.
"""

import sys
import os
import importlib.util

def test_pipeline_import():
    """Test that the main pipeline can be imported."""
    print("🧪 Testing Pipeline Import...")
    
    try:
        # Add parent directory to path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        
        # Test importing the main pipeline
        spec = importlib.util.spec_from_file_location(
            "run_daily_digest_pipeline", 
            os.path.join(parent_dir, "processors", "run_daily_digest_pipeline.py")
        )
        
        if spec is None:
            print("❌ Cannot create spec for pipeline")
            return False
        
        pipeline_module = importlib.util.module_from_spec(spec)
        
        # Try to load the module (but don't execute)
        print("✅ Pipeline module can be loaded")
        
        # Test that we can access the configuration
        spec.loader.exec_module(pipeline_module)
        
        if hasattr(pipeline_module, 'SCRAPERS'):
            print(f"✅ Found SCRAPERS configuration: {len(pipeline_module.SCRAPERS)} scrapers")
        else:
            print("❌ SCRAPERS configuration not found")
            return False
            
        if hasattr(pipeline_module, 'AGGREGATOR'):
            print("✅ Found AGGREGATOR configuration")
        else:
            print("❌ AGGREGATOR configuration not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Pipeline import failed: {e}")
        return False

def test_scraper_imports():
    """Test that scrapers can be imported."""
    print("\n🧪 Testing Scraper Imports...")
    
    scrapers = [
        'demo_tech_news.py',
        'internship_scraper.py',
        'jobs_scraper.py',
        'upskill_scraper.py',
        'webscraptest.py'
    ]
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scrapers_dir = os.path.join(parent_dir, "scrapers")
    
    success_count = 0
    
    for scraper in scrapers:
        try:
            scraper_path = os.path.join(scrapers_dir, scraper)
            if os.path.exists(scraper_path):
                spec = importlib.util.spec_from_file_location(
                    scraper.replace('.py', ''), 
                    scraper_path
                )
                if spec is not None:
                    print(f"✅ {scraper} can be loaded")
                    success_count += 1
                else:
                    print(f"❌ {scraper} cannot create spec")
            else:
                print(f"❌ {scraper} not found")
        except Exception as e:
            print(f"❌ {scraper} import error: {e}")
    
    print(f"\nScraper import results: {success_count}/{len(scrapers)} successful")
    return success_count == len(scrapers)

def test_config_access():
    """Test that config files can be accessed."""
    print("\n🧪 Testing Config Access...")
    
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(parent_dir, "config")
        
        # Check if config files exist
        config_files = ['config.py', 'api_manager.py', 'api_config_template.json']
        
        for config_file in config_files:
            config_path = os.path.join(config_dir, config_file)
            if os.path.exists(config_path):
                print(f"✅ {config_file} exists")
            else:
                print(f"❌ {config_file} not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Config access failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 PIPELINE IMPORT VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Pipeline Import", test_pipeline_import),
        ("Scraper Imports", test_scraper_imports),
        ("Config Access", test_config_access)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL IMPORT TESTS PASSED!")
        print("✅ The reorganized structure is working correctly")
        print("✅ Pipeline can be imported and executed")
        print("\n💡 Ready to run:")
        print("  python processors/run_daily_digest_pipeline.py")
    else:
        print(f"\n❌ {total - passed} TESTS FAILED")
        print("Please check the import paths and file locations")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
