#!/usr/bin/env python3
"""
Demo script to showcase the automatic cleanup mechanism
"""

import os
import json
import time
from datetime import datetime

# Import cleanup function and configuration
from run_daily_digest_pipeline import cleanup_output_files, OUTPUT_FILES_TO_CLEAR, PERSISTENT_FILES_TO_PRESERVE

def create_demo_files():
    """Create demo files to show cleanup in action"""
    print("📝 CREATING DEMO FILES")
    print("=" * 40)
    
    # Create some output files that should be cleared
    demo_output_files = [
        "../data/ai_selected_article.json",
        "../data/daily_tech_digest.json", 
        "../data/selected_internship.json",
        "../data/todays_tech_news.json",
        "../data/tji_daily_message.json"
    ]
    
    # Create some persistent files that should be preserved
    demo_persistent_files = [
        "../data/tech_news_history.json",
        "../data/upskill_articles_history.json",
        "../data/seen_internships.json"
    ]
    
    print("Creating OUTPUT files (will be cleared):")
    for file_path in demo_output_files:
        demo_content = {
            "demo": True,
            "file_type": "output",
            "created_at": datetime.now().isoformat(),
            "should_be_cleared": True,
            "content": f"This is demo content for {file_path}"
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(demo_content, f, indent=2)
        
        file_size = os.path.getsize(file_path)
        print(f"  ✅ {file_path} ({file_size} bytes)")
    
    print(f"\nCreating PERSISTENT files (will be preserved):")
    for file_path in demo_persistent_files:
        demo_content = {
            "demo": True,
            "file_type": "persistent",
            "created_at": datetime.now().isoformat(),
            "should_be_preserved": True,
            "history_data": [
                {"entry": 1, "timestamp": datetime.now().isoformat()},
                {"entry": 2, "timestamp": datetime.now().isoformat()}
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(demo_content, f, indent=2)
        
        file_size = os.path.getsize(file_path)
        print(f"  🛡️  {file_path} ({file_size} bytes)")
    
    return demo_output_files + demo_persistent_files

def show_files_before_cleanup():
    """Show current state of files before cleanup"""
    print(f"\n📁 FILES BEFORE CLEANUP")
    print("=" * 40)
    
    all_files = OUTPUT_FILES_TO_CLEAR + PERSISTENT_FILES_TO_PRESERVE
    existing_files = []
    
    for file_path in all_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            file_type = "🛡️  PERSISTENT" if file_path in PERSISTENT_FILES_TO_PRESERVE else "📤 OUTPUT"
            print(f"  {file_type}: {file_path} ({file_size} bytes)")
            existing_files.append(file_path)
        else:
            file_type = "🛡️  PERSISTENT" if file_path in PERSISTENT_FILES_TO_PRESERVE else "📤 OUTPUT"
            print(f"  {file_type}: {file_path} (not found)")
    
    print(f"\nTotal existing files: {len(existing_files)}")
    return existing_files

def show_files_after_cleanup():
    """Show current state of files after cleanup"""
    print(f"\n📁 FILES AFTER CLEANUP")
    print("=" * 40)
    
    output_remaining = 0
    persistent_remaining = 0
    
    print("OUTPUT files (should be cleared):")
    for file_path in OUTPUT_FILES_TO_CLEAR:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  ❌ STILL EXISTS: {file_path} ({file_size} bytes)")
            output_remaining += 1
        else:
            print(f"  ✅ CLEARED: {file_path}")
    
    print(f"\nPERSISTENT files (should be preserved):")
    for file_path in PERSISTENT_FILES_TO_PRESERVE:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  🛡️  PRESERVED: {file_path} ({file_size} bytes)")
            persistent_remaining += 1
        else:
            print(f"  ⚪ NOT FOUND: {file_path}")
    
    return output_remaining, persistent_remaining

def main():
    """Main demo function"""
    print("🧹 CLEANUP MECHANISM DEMONSTRATION")
    print("=" * 60)
    print("This demo shows how the automatic cleanup mechanism works")
    print("in the TJI Daily Pipeline.\n")
    
    # Step 1: Create demo files
    created_files = create_demo_files()
    
    # Step 2: Show files before cleanup
    existing_before = show_files_before_cleanup()
    
    # Step 3: Wait a moment for dramatic effect
    print(f"\n⏳ Preparing to run cleanup in 3 seconds...")
    time.sleep(3)
    
    # Step 4: Run cleanup
    print(f"\n🧹 RUNNING CLEANUP MECHANISM")
    print("=" * 40)
    
    try:
        cleanup_stats = cleanup_output_files()
        cleanup_success = True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        cleanup_success = False
        cleanup_stats = {"error": str(e)}
    
    # Step 5: Show files after cleanup
    if cleanup_success:
        output_remaining, persistent_remaining = show_files_after_cleanup()
        
        # Step 6: Analysis
        print(f"\n📊 CLEANUP ANALYSIS")
        print("=" * 40)
        print(f"Files created: {len(created_files)}")
        print(f"Files existing before: {len(existing_before)}")
        print(f"Files cleared: {cleanup_stats.get('total_cleared', 0)}")
        print(f"Files preserved: {cleanup_stats.get('total_preserved', 0)}")
        print(f"Cleanup errors: {len(cleanup_stats.get('errors', []))}")
        
        # Determine success
        cleanup_worked = (output_remaining == 0)
        preservation_worked = (persistent_remaining > 0)
        
        print(f"\n🎯 RESULTS:")
        print(f"  • Output files cleared: {'✅ YES' if cleanup_worked else '❌ NO'}")
        print(f"  • Persistent files preserved: {'✅ YES' if preservation_worked else '⚪ NONE EXISTED'}")
        print(f"  • Overall success: {'✅ YES' if cleanup_worked else '❌ NO'}")
        
        if cleanup_worked:
            print(f"\n🎉 CLEANUP MECHANISM WORKING PERFECTLY!")
            print(f"The automatic cleanup system successfully:")
            print(f"  • Cleared {cleanup_stats.get('total_cleared', 0)} output files")
            print(f"  • Preserved {cleanup_stats.get('total_preserved', 0)} persistent files")
            print(f"  • Maintained deduplication history")
            print(f"  • Ready for fresh pipeline execution")
        else:
            print(f"\n⚠️  CLEANUP MECHANISM NEEDS ATTENTION")
            print(f"Some output files were not cleared properly.")
    else:
        print(f"\n❌ CLEANUP DEMONSTRATION FAILED")
        print(f"Error: {cleanup_stats.get('error', 'Unknown error')}")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"  • Run: python run_daily_digest_pipeline.py")
    print(f"  • Cleanup will happen automatically at the start")
    print(f"  • Check logs for detailed cleanup information")
    print(f"  • Review: README_CLEANUP_MECHANISM.md")

if __name__ == "__main__":
    main()
