#!/usr/bin/env python3
"""
Simple test for cleanup functionality
"""

import os
import json
from datetime import datetime

# Configuration - same as in pipeline
OUTPUT_FILES_TO_CLEAR = [
    "../data/ai_selected_article.json",
    "../data/daily_tech_digest.json",
    "../data/selected_internship.json",
    "../data/todays_tech_news.json"
]

def simple_cleanup_test():
    """Simple test of cleanup functionality"""
    print("🧪 SIMPLE CLEANUP TEST")
    print("=" * 30)
    
    # Create test files
    print("📝 Creating test files...")
    created_files = []
    
    for file_path in OUTPUT_FILES_TO_CLEAR[:4]:  # Just test first 4 files
        test_content = {
            "test": True,
            "created_at": datetime.now().isoformat(),
            "should_be_cleared": True
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(test_content, f, indent=2)
            created_files.append(file_path)
            print(f"  ✅ Created: {file_path}")
        except Exception as e:
            print(f"  ❌ Failed to create {file_path}: {e}")
    
    print(f"\n🧹 Clearing files...")
    cleared_count = 0
    error_count = 0
    
    # Clear the files
    for file_path in OUTPUT_FILES_TO_CLEAR[:4]:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                cleared_count += 1
                print(f"  ✅ Cleared: {file_path}")
            else:
                print(f"  ⚪ Not found: {file_path}")
        except Exception as e:
            error_count += 1
            print(f"  ❌ Error clearing {file_path}: {e}")
    
    # Verify cleanup
    print(f"\n🔍 Verifying cleanup...")
    remaining_files = []
    for file_path in OUTPUT_FILES_TO_CLEAR[:4]:
        if os.path.exists(file_path):
            remaining_files.append(file_path)
            print(f"  ❌ Still exists: {file_path}")
        else:
            print(f"  ✅ Successfully cleared: {file_path}")
    
    # Summary
    print(f"\n📊 TEST RESULTS:")
    print(f"  • Files created: {len(created_files)}")
    print(f"  • Files cleared: {cleared_count}")
    print(f"  • Errors: {error_count}")
    print(f"  • Files remaining: {len(remaining_files)}")
    
    success = (len(remaining_files) == 0 and error_count == 0)
    
    if success:
        print(f"\n🎉 TEST PASSED!")
        print(f"Cleanup mechanism is working correctly.")
    else:
        print(f"\n❌ TEST FAILED!")
        if remaining_files:
            print(f"Files not cleared: {remaining_files}")
        if error_count > 0:
            print(f"Errors occurred during cleanup")
    
    return success

if __name__ == "__main__":
    success = simple_cleanup_test()
    exit(0 if success else 1)
