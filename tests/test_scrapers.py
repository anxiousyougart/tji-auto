#!/usr/bin/env python3
"""
Test Individual Scrapers

This script tests each scraper individually to identify specific issues
and provides detailed error reporting for debugging.

"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime

def test_scraper(script_name: str, timeout: int = 60) -> dict:
    """
    Test an individual scraper and return detailed results.
    
    Args:
        script_name: Name of the Python script to test
        timeout: Timeout in seconds
        
    Returns:
        Dictionary with test results
    """
    print(f"\n🧪 TESTING: {script_name}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Analyze results
        success = result.returncode == 0
        
        test_result = {
            "script": script_name,
            "success": success,
            "return_code": result.returncode,
            "execution_time": execution_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timeout": False
        }
        
        # Print immediate feedback
        if success:
            print(f"✅ SUCCESS - Completed in {execution_time:.1f}s")
        else:
            print(f"❌ FAILED - Return code: {result.returncode}")
            print(f"⏱️  Execution time: {execution_time:.1f}s")
            
            # Show first few lines of error
            if result.stderr:
                error_lines = result.stderr.split('\n')[:3]
                print("🔍 Error preview:")
                for line in error_lines:
                    if line.strip():
                        print(f"   {line}")
        
        return test_result
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"⏰ TIMEOUT - Exceeded {timeout}s limit")
        
        return {
            "script": script_name,
            "success": False,
            "return_code": -1,
            "execution_time": execution_time,
            "stdout": "",
            "stderr": f"Timeout after {timeout} seconds",
            "timeout": True
        }
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"💥 CRASHED - {str(e)}")
        
        return {
            "script": script_name,
            "success": False,
            "return_code": -2,
            "execution_time": execution_time,
            "stdout": "",
            "stderr": str(e),
            "timeout": False
        }

def check_output_files():
    """Check which output files exist and their sizes."""
    print("\n📁 OUTPUT FILE STATUS:")
    print("-" * 50)
    
    expected_files = [
        "../data/ai_selected_article.json",
        "../data/selected_internship.json",
        "../data/selected_job.json", 
        "../data/ai_selected_upskill_article.json",
        "../data/daily_tech_digest.json"
    ]
    
    file_status = {}
    
    for filename in expected_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} ({size} bytes)")
            file_status[filename] = {"exists": True, "size": size}
            
            # Try to peek at content
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        if "message" in content and "No suitable content found" in content["message"]:
                            print(f"   ⚠️  Contains fallback message")
                        else:
                            print(f"   ✅ Contains valid content")
                    file_status[filename]["valid_json"] = True
            except:
                print(f"   ❌ Invalid JSON")
                file_status[filename]["valid_json"] = False
        else:
            print(f"❌ {filename} (not found)")
            file_status[filename] = {"exists": False, "size": 0}
    
    return file_status

def main():
    """Main testing function."""
    print("🔬 SCRAPER TESTING SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing individual scrapers to identify issues...\n")
    
    # List of scrapers to test
    scrapers = [
        {"script": "demo_tech_news.py", "timeout": 120},
        {"script": "internship_scraper.py", "timeout": 180},
        {"script": "jobs_scraper.py", "timeout": 180},
        {"script": "demo_upskill.py", "timeout": 120},
        {"script": "daily_tech_aggregator.py", "timeout": 60}
    ]
    
    results = []
    
    # Test each scraper
    for scraper in scrapers:
        result = test_scraper(scraper["script"], scraper["timeout"])
        results.append(result)
        
        # Small delay between tests
        time.sleep(2)
    
    # Check output files
    file_status = check_output_files()
    
    # Generate summary report
    print("\n📊 TESTING SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    print(f"⏱️  Total time: {sum(r['execution_time'] for r in results):.1f}s")
    
    # Detailed failure analysis
    failed_scrapers = [r for r in results if not r["success"]]
    
    if failed_scrapers:
        print(f"\n🔍 FAILURE ANALYSIS:")
        print("-" * 30)
        
        for failure in failed_scrapers:
            print(f"\n❌ {failure['script']}:")
            print(f"   Return code: {failure['return_code']}")
            print(f"   Execution time: {failure['execution_time']:.1f}s")
            
            if failure["timeout"]:
                print(f"   Issue: Timeout")
            elif failure["stderr"]:
                # Show key error lines
                error_lines = failure["stderr"].split('\n')
                key_errors = [line for line in error_lines if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'traceback'])]
                if key_errors:
                    print(f"   Key errors:")
                    for error in key_errors[:3]:  # Show first 3 key errors
                        print(f"     {error.strip()}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 30)
    
    if any(r["timeout"] for r in results):
        print("⏰ Some scrapers timed out - consider increasing timeout values")
    
    if any("401" in r["stderr"] for r in results):
        print("🔑 API authentication issues detected - check Groq API key")
    
    if any("403" in r["stderr"] for r in results):
        print("🚫 Access forbidden errors - some sites may be blocking requests")
    
    if any("import" in r["stderr"].lower() for r in results):
        print("📦 Import errors detected - check if all dependencies are installed")
    
    # Save detailed results
    try:
        with open("../data/scraper_test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "successful": successful,
                    "total": total,
                    "total_time": sum(r['execution_time'] for r in results)
                },
                "results": results,
                "file_status": file_status
            }, f, indent=2)
        print(f"../data/\n💾 Detailed results saved to: scraper_test_results.json")
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")

if __name__ == "__main__":
    main()
