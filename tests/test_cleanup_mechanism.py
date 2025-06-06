#!/usr/bin/env python3
"""
Test script to verify the cleanup mechanism functionality
"""

import os
import json
from datetime import datetime

# Import the cleanup function from the pipeline
from run_daily_digest_pipeline import cleanup_output_files, OUTPUT_FILES_TO_CLEAR, PERSISTENT_FILES_TO_PRESERVE

def create_test_files():
    """Create test files to verify cleanup functionality"""
    print("📝 Creating test files...")
    
    # Create some output files that should be cleared
    test_output_files = [
        "../data/ai_selected_article.json",
        "../data/daily_tech_digest.json", 
        "../data/selected_internship.json",
        "../data/todays_tech_news.json"
    ]
    
    # Create some persistent files that should be preserved
    test_persistent_files = [
        "../data/upskill_articles_history.json",
        "../data/tech_news_history.json",
        "../data/seen_internships.json"
    ]
    
    created_files = []
    
    # Create output files
    for file_path in test_output_files:
        test_content = {
            "test": True,
            "created_at": datetime.now().isoformat(),
            "file_type": "output_file",
            "should_be_cleared": True
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_content, f, indent=2)
        
        created_files.append(file_path)
        print(f"  ✅ Created: {file_path}")
    
    # Create persistent files
    for file_path in test_persistent_files:
        test_content = {
            "test": True,
            "created_at": datetime.now().isoformat(),
            "file_type": "persistent_file",
            "should_be_preserved": True
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_content, f, indent=2)
        
        created_files.append(file_path)
        print(f"  🛡️  Created: {file_path}")
    
    return created_files

def verify_cleanup_results():
    """Verify that cleanup worked correctly"""
    print("\n🔍 Verifying cleanup results...")
    
    # Check that output files were cleared
    output_files_cleared = 0
    output_files_remaining = 0
    
    for file_path in OUTPUT_FILES_TO_CLEAR:
        if os.path.exists(file_path):
            output_files_remaining += 1
            print(f"  ❌ Still exists: {file_path}")
        else:
            output_files_cleared += 1
            print(f"  ✅ Cleared: {file_path}")
    
    # Check that persistent files were preserved
    persistent_files_preserved = 0
    persistent_files_missing = 0
    
    for file_path in PERSISTENT_FILES_TO_PRESERVE:
        if os.path.exists(file_path):
            persistent_files_preserved += 1
            print(f"  🛡️  Preserved: {file_path}")
        else:
            persistent_files_missing += 1
            print(f"  ⚪ Not found: {file_path}")
    
    print(f"\n📊 VERIFICATION RESULTS:")
    print(f"  • Output files cleared: {output_files_cleared}")
    print(f"  • Output files remaining: {output_files_remaining}")
    print(f"  • Persistent files preserved: {persistent_files_preserved}")
    print(f"  • Persistent files missing: {persistent_files_missing}")
    
    # Determine success
    cleanup_successful = (output_files_remaining == 0)
    
    if cleanup_successful:
        print(f"  ✅ Cleanup verification: SUCCESS")
    else:
        print(f"  ❌ Cleanup verification: FAILED")
    
    return cleanup_successful

def main():
    """Main test function"""
    print("🧪 TESTING CLEANUP MECHANISM")
    print("=" * 50)
    
    # Step 1: Create test files
    created_files = create_test_files()
    
    # Step 2: Run cleanup
    print(f"\n🧹 Running cleanup function...")
    try:
        cleanup_stats = cleanup_output_files()
        print(f"✅ Cleanup function completed")
    except Exception as e:
        print(f"❌ Cleanup function failed: {e}")
        return False
    
    # Step 3: Verify results
    verification_success = verify_cleanup_results()
    
    # Step 4: Summary
    print(f"\n🎯 TEST SUMMARY:")
    print(f"  • Files created: {len(created_files)}")
    print(f"  • Cleanup executed: {'✅ Yes' if 'total_cleared' in cleanup_stats else '❌ No'}")
    print(f"  • Verification: {'✅ Passed' if verification_success else '❌ Failed'}")
    
    if verification_success:
        print(f"\n🎉 CLEANUP MECHANISM TEST PASSED!")
        print(f"The cleanup system is working correctly.")
    else:
        print(f"\n❌ CLEANUP MECHANISM TEST FAILED!")
        print(f"Check the implementation for issues.")
    
    return verification_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
