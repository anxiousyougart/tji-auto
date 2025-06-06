#!/usr/bin/env python3


import subprocess
import sys
import time
import logging
import os
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/daily_digest_pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Pipeline configuration
SCRAPERS = [
    {
        "name": "Tech News Scraper",
        "script": "../scrapers/demo_tech_news.py",
        "output_file": "../data/ai_selected_article.json",
        "timeout": 300  # 5 minutes
    },
    {
        "name": "Internship Scraper",
        "script": "../scrapers/internship_scraper.py",
        "output_file": "../data/selected_internship.json",
        "timeout": 600  # 10 minutes
    },
    {
        "name": "Job Scraper",
        "script": "../scrapers/jobs_scraper.py",
        "output_file": "../data/selected_job.json",
        "timeout": 600  # 10 minutes
    },
    {
        "name": "Upskill Articles Scraper",
        "script": "../tests/demo_upskill.py",
        "output_file": "../data/ai_selected_upskill_article.json",
        "timeout": 300  # 5 minutes
    }
]

AGGREGATOR = {
    "name": "Daily Digest Aggregator",
    "script": "daily_tech_aggregator.py",
    "output_file": "../data/daily_tech_digest.json",
    "timeout": 60  # 1 minute
}

# Optional TinyURL shortener step
URL_SHORTENER = {
    "name": "TinyURL Shortener",
    "script": "tinyurl_shortener.py",
    "output_file": "../data/shortened_urls_digest.json",
    "timeout": 300,  # 5 minutes
    "enabled": True  # Set to True to enable URL shortening in pipeline
}

# Message drafting and sending steps
MESSAGE_DRAFTER = {
    "name": "TJI Message Drafter",
    "script": "message_drafter.py",
    "output_file": "../data/tji_daily_message.json",
    "timeout": 120,  # 2 minutes
    "enabled": True  # Set to True to enable message drafting
}

TWILIO_SENDER = {
    "name": "Twilio WhatsApp Sender",
    "script": "../messaging/twillo.py",
    "output_file": None,  # No specific output file, just sends message
    "timeout": 60,  # 1 minute
    "enabled": True  # Set to True to enable WhatsApp message sending
}

# Cleanup configuration - files to clear before each pipeline run
OUTPUT_FILES_TO_CLEAR = [
    "../data/ai_selected_article.json",           # Tech news AI selection
    "../data/ai_selected_upskill_article.json",   # Upskill article AI selection
    "../data/daily_tech_digest.json",             # Aggregated daily digest
    "../data/filtered_internships.json",          # Filtered internship results
    "../data/filtered_jobs.json",                 # Filtered job results
    "../data/selected_internship.json",           # AI-selected best internship
    "../data/selected_job.json",                  # AI-selected best job
    "../data/shortened_urls_digest.json",         # URL shortening results
    "../data/todays_tech_news.json",              # Scraped tech news
    "../data/tji_daily_message.json",             # Formatted message output
    "../data/upskill_articles.json"               # Scraped upskill articles
]

# Persistent files to PRESERVE (never clear these)
PERSISTENT_FILES_TO_PRESERVE = [
    "../data/upskill_articles_history.json",      # Upskill deduplication history
    "../data/tech_news_history.json",             # Tech news deduplication history
    "../data/seen_internships.json",              # Internship deduplication tracking
    "../data/seen_jobs.json",                     # Job deduplication tracking
    "../data/tinyurl_run_counter.json"            # URL shortening counter
]

def run_script(script_name: str, timeout: int = 300) -> tuple:
    """
    Run a Python script with timeout and capture output.

    Args:
        script_name: Name of the Python script to run
        timeout: Maximum time to wait in seconds

    Returns:
        Tuple of (success: bool, output: str, error: str)
    """
    try:
        logging.info(f"Starting {script_name}...")

        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )

        if result.returncode == 0:
            logging.info(f"✅ {script_name} completed successfully")
            return True, result.stdout, result.stderr
        else:
            logging.error(f"❌ {script_name} failed with return code {result.returncode}")
            return False, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        logging.error(f"⏰ {script_name} timed out after {timeout} seconds")
        return False, "", f"Timeout after {timeout} seconds"
    except Exception as e:
        logging.error(f"💥 {script_name} crashed: {e}")
        return False, "", str(e)

def check_output_file(file_path: str) -> bool:
    """
    Check if an output file exists and is not empty.

    Args:
        file_path: Path to the output file

    Returns:
        True if file exists and has content, False otherwise
    """
    try:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > 0:
                logging.info(f"📁 Output file created: {file_path} ({size} bytes)")
                return True
            else:
                logging.warning(f"📁 Output file is empty: {file_path}")
                return False
        else:
            logging.warning(f"📁 Output file not found: {file_path}")
            return False
    except Exception as e:
        logging.error(f"📁 Error checking output file {file_path}: {e}")
        return False

def create_fallback_output(file_path: str, scraper_name: str) -> None:
    """Create a fallback output file when scraper fails or produces no content."""
    try:
        fallback_content = {
            "message": f"No suitable content found for {scraper_name}",
            "status": "no_content",
            "timestamp": datetime.now().isoformat(),
            "scraper": scraper_name
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(fallback_content, f, indent=2, ensure_ascii=False)

        logging.info(f"Created fallback output file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to create fallback output file {file_path}: {e}")

def cleanup_output_files() -> dict:
    """
    Clean up output files from previous pipeline runs while preserving persistent data.

    This function removes old output files to ensure fresh data generation while
    carefully preserving deduplication history and other persistent files.

    Returns:
        Dictionary with cleanup statistics and results
    """
    cleanup_stats = {
        "files_cleared": [],
        "files_not_found": [],
        "files_preserved": [],
        "errors": [],
        "total_cleared": 0,
        "total_preserved": 0
    }

    logging.info("🧹 Starting automatic cleanup of output files...")
    print("🧹 CLEANUP: Clearing previous output files...")
    print("-" * 50)

    # Clear output files
    for file_path in OUTPUT_FILES_TO_CLEAR:
        try:
            if os.path.exists(file_path):
                # Get file size before deletion for logging
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                cleanup_stats["files_cleared"].append(file_path)
                cleanup_stats["total_cleared"] += 1
                logging.info(f"✅ Cleared: {file_path} ({file_size} bytes)")
                print(f"  ✅ Cleared: {file_path}")
            else:
                cleanup_stats["files_not_found"].append(file_path)
                logging.debug(f"⚪ Not found: {file_path}")
                print(f"  ⚪ Not found: {file_path}")
        except Exception as e:
            error_msg = f"Failed to clear {file_path}: {e}"
            cleanup_stats["errors"].append(error_msg)
            logging.error(f"❌ {error_msg}")
            print(f"  ❌ Error: {file_path} - {e}")

    # Verify persistent files are preserved (informational)
    print(f"\n🛡️  PRESERVED: Checking persistent files...")
    for file_path in PERSISTENT_FILES_TO_PRESERVE:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            cleanup_stats["files_preserved"].append(file_path)
            cleanup_stats["total_preserved"] += 1
            logging.info(f"🛡️  Preserved: {file_path} ({file_size} bytes)")
            print(f"  🛡️  Preserved: {file_path} ({file_size} bytes)")
        else:
            logging.debug(f"⚪ Persistent file not found: {file_path}")
            print(f"  ⚪ Not found: {file_path}")

    # Summary
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"  • Files cleared: {cleanup_stats['total_cleared']}")
    print(f"  • Files preserved: {cleanup_stats['total_preserved']}")
    print(f"  • Errors: {len(cleanup_stats['errors'])}")

    if cleanup_stats['errors']:
        print(f"  ⚠️  Cleanup errors occurred - check logs for details")
        logging.warning(f"Cleanup completed with {len(cleanup_stats['errors'])} errors")
    else:
        print(f"  ✅ Cleanup completed successfully")
        logging.info(f"Cleanup completed successfully: {cleanup_stats['total_cleared']} files cleared")

    print()  # Add spacing before next pipeline step
    return cleanup_stats

def run_pipeline():
    """
    Run the complete daily digest pipeline.
    """
    print("🚀 DAILY TECH DIGEST PIPELINE")
    print("=" * 60)
    print(f"Starting pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Running {len(SCRAPERS)} scrapers + aggregator\n")

    pipeline_start_time = time.time()
    results = {
        "scrapers": {},
        "aggregator": None,
        "cleanup": None,
        "total_time": 0,
        "successful_scrapers": 0,
        "failed_scrapers": 0
    }

    # Step 0: Cleanup previous output files
    try:
        cleanup_stats = cleanup_output_files()
        results["cleanup"] = cleanup_stats
    except Exception as e:
        logging.error(f"Cleanup failed: {e}")
        print(f"⚠️  Cleanup failed: {e}")
        print("Continuing with pipeline execution...\n")
        results["cleanup"] = {"error": str(e)}

    # Run each scraper
    for i, scraper in enumerate(SCRAPERS, 1):
        print(f"📊 STEP {i}/{len(SCRAPERS)}: {scraper['name']}")
        print("-" * 40)

        start_time = time.time()
        success, stdout, stderr = run_script(scraper['script'], scraper['timeout'])
        end_time = time.time()

        # Check output file
        output_exists = check_output_file(scraper['output_file'])

        # Store results
        results["scrapers"][scraper['name']] = {
            "success": success,
            "output_file_exists": output_exists,
            "execution_time": end_time - start_time,
            "stdout": stdout[:500] + "..." if len(stdout) > 500 else stdout,
            "stderr": stderr[:500] + "..." if len(stderr) > 500 else stderr
        }

        if success and output_exists:
            results["successful_scrapers"] += 1
            print(f"✅ {scraper['name']} completed successfully")
        elif success and not output_exists:
            # Create a fallback output file to prevent aggregator failure
            create_fallback_output(scraper['output_file'], scraper['name'])
            results["successful_scrapers"] += 1  # Still count as success
            print(f"⚠️  {scraper['name']} completed but no content found")
            print("   (Created fallback file for aggregator)")
        else:
            # Create a fallback output file to prevent aggregator failure
            create_fallback_output(scraper['output_file'], scraper['name'])
            results["failed_scrapers"] += 1
            print(f"❌ {scraper['name']} failed")
            if stderr:
                print(f"Error: {stderr[:200]}...")
            print("   (Created fallback file for aggregator)")

        print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds\n")

        # Small delay between scrapers
        time.sleep(2)

    # Run aggregator
    print(f"📊 FINAL STEP: {AGGREGATOR['name']}")
    print("-" * 40)

    start_time = time.time()
    success, stdout, stderr = run_script(AGGREGATOR['script'], AGGREGATOR['timeout'])
    end_time = time.time()

    # Check output file
    output_exists = check_output_file(AGGREGATOR['output_file'])

    # Store aggregator results
    results["aggregator"] = {
        "success": success,
        "output_file_exists": output_exists,
        "execution_time": end_time - start_time,
        "stdout": stdout[:500] + "..." if len(stdout) > 500 else stdout,
        "stderr": stderr[:500] + "..." if len(stderr) > 500 else stderr
    }

    if success and output_exists:
        print(f"✅ {AGGREGATOR['name']} completed successfully")
    else:
        print(f"❌ {AGGREGATOR['name']} failed")
        if stderr:
            print(f"Error: {stderr[:200]}...")

    print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds\n")

    # Optional TinyURL shortener step
    if URL_SHORTENER["enabled"] and results["aggregator"]["success"]:
        print(f"📊 OPTIONAL STEP: {URL_SHORTENER['name']}")
        print("-" * 40)

        start_time = time.time()
        success, stdout, stderr = run_script(URL_SHORTENER['script'], URL_SHORTENER['timeout'])
        end_time = time.time()

        # Check output file
        output_exists = check_output_file(URL_SHORTENER['output_file'])

        # Store URL shortener results
        results["url_shortener"] = {
            "success": success,
            "output_file_exists": output_exists,
            "execution_time": end_time - start_time,
            "stdout": stdout[:500] + "..." if len(stdout) > 500 else stdout,
            "stderr": stderr[:500] + "..." if len(stderr) > 500 else stderr
        }

        if success and output_exists:
            print(f"✅ {URL_SHORTENER['name']} completed successfully")
        else:
            print(f"❌ {URL_SHORTENER['name']} failed")
            if stderr:
                print(f"Error: {stderr[:200]}...")

        print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds\n")
    elif URL_SHORTENER["enabled"]:
        print(f"⏭️  Skipping TinyURL shortener (aggregator failed)\n")

    # Message drafting step (depends on URL shortener or aggregator)
    message_input_available = (URL_SHORTENER["enabled"] and "url_shortener" in results and results["url_shortener"]["success"]) or results["aggregator"]["success"]

    if MESSAGE_DRAFTER["enabled"] and message_input_available:
        print(f"📊 OPTIONAL STEP: {MESSAGE_DRAFTER['name']}")
        print("-" * 40)

        start_time = time.time()
        success, stdout, stderr = run_script(MESSAGE_DRAFTER['script'], MESSAGE_DRAFTER['timeout'])
        end_time = time.time()

        # Check output file
        output_exists = check_output_file(MESSAGE_DRAFTER['output_file'])

        # Store message drafter results
        results["message_drafter"] = {
            "success": success,
            "output_file_exists": output_exists,
            "execution_time": end_time - start_time,
            "stdout": stdout[:500] + "..." if len(stdout) > 500 else stdout,
            "stderr": stderr[:500] + "..." if len(stderr) > 500 else stderr
        }

        if success and output_exists:
            print(f"✅ {MESSAGE_DRAFTER['name']} completed successfully")
        else:
            print(f"❌ {MESSAGE_DRAFTER['name']} failed")
            if stderr:
                print(f"Error: {stderr[:200]}...")

        print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds\n")
    elif MESSAGE_DRAFTER["enabled"]:
        print(f"⏭️  Skipping message drafter (no input data available)\n")

    # Twilio WhatsApp sender step (depends on message drafter)
    if TWILIO_SENDER["enabled"] and MESSAGE_DRAFTER["enabled"] and "message_drafter" in results and results["message_drafter"]["success"]:
        print(f"📊 OPTIONAL STEP: {TWILIO_SENDER['name']}")
        print("-" * 40)

        start_time = time.time()
        success, stdout, stderr = run_script(TWILIO_SENDER['script'], TWILIO_SENDER['timeout'])
        end_time = time.time()

        # Store Twilio sender results (no output file to check)
        results["twilio_sender"] = {
            "success": success,
            "execution_time": end_time - start_time,
            "stdout": stdout[:500] + "..." if len(stdout) > 500 else stdout,
            "stderr": stderr[:500] + "..." if len(stderr) > 500 else stderr
        }

        if success:
            print(f"✅ {TWILIO_SENDER['name']} completed successfully")
            if "Message sent!" in stdout:
                print(f"📱 WhatsApp message sent successfully!")
        else:
            print(f"❌ {TWILIO_SENDER['name']} failed")
            if stderr:
                print(f"Error: {stderr[:200]}...")

        print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds\n")
    elif TWILIO_SENDER["enabled"]:
        print(f"⏭️  Skipping Twilio sender (message drafter failed or disabled)\n")

    # Calculate total time
    pipeline_end_time = time.time()
    results["total_time"] = pipeline_end_time - pipeline_start_time

    # Display summary
    print("📋 PIPELINE SUMMARY")
    print("=" * 60)
    print(f"🕒 Total execution time: {results['total_time']:.1f} seconds")

    # Cleanup summary
    if results["cleanup"] and "error" not in results["cleanup"]:
        cleanup_status = f"✅ Success ({results['cleanup']['total_cleared']} files cleared)"
    elif results["cleanup"] and "error" in results["cleanup"]:
        cleanup_status = f"❌ Failed ({results['cleanup']['error']})"
    else:
        cleanup_status = "⚪ Not performed"
    print(f"🧹 Cleanup: {cleanup_status}")

    print(f"✅ Successful scrapers: {results['successful_scrapers']}/{len(SCRAPERS)}")
    print(f"❌ Failed scrapers: {results['failed_scrapers']}/{len(SCRAPERS)}")

    aggregator_status = "✅ Success" if results["aggregator"]["success"] else "❌ Failed"
    print(f"🔄 Aggregator: {aggregator_status}")

    # TinyURL shortener status (if enabled)
    if URL_SHORTENER["enabled"]:
        if "url_shortener" in results:
            url_shortener_status = "✅ Success" if results["url_shortener"]["success"] else "❌ Failed"
            print(f"🔗 TinyURL Shortener: {url_shortener_status}")
        else:
            print(f"🔗 TinyURL Shortener: ⏭️ Skipped (aggregator failed)")
    else:
        print(f"🔗 TinyURL Shortener: ⚪ Disabled")

    # Message drafter status (if enabled)
    if MESSAGE_DRAFTER["enabled"]:
        if "message_drafter" in results:
            message_drafter_status = "✅ Success" if results["message_drafter"]["success"] else "❌ Failed"
            print(f"✍️  Message Drafter: {message_drafter_status}")
        else:
            print(f"✍️  Message Drafter: ⏭️ Skipped (no input data)")
    else:
        print(f"✍️  Message Drafter: ⚪ Disabled")

    # Twilio sender status (if enabled)
    if TWILIO_SENDER["enabled"]:
        if "twilio_sender" in results:
            twilio_sender_status = "✅ Success" if results["twilio_sender"]["success"] else "❌ Failed"
            print(f"📱 WhatsApp Sender: {twilio_sender_status}")
        else:
            print(f"📱 WhatsApp Sender: ⏭️ Skipped (message drafter failed)")
    else:
        print(f"📱 WhatsApp Sender: ⚪ Disabled")

    # Final output files check
    print(f"\n📁 OUTPUT FILES:")
    for scraper in SCRAPERS:
        exists = "✅" if os.path.exists(scraper['output_file']) else "❌"
        print(f"  {exists} {scraper['output_file']}")

    aggregator_exists = "✅" if os.path.exists(AGGREGATOR['output_file']) else "❌"
    print(f"  {aggregator_exists} {AGGREGATOR['output_file']}")

    # TinyURL shortener output file (if enabled)
    if URL_SHORTENER["enabled"]:
        url_shortener_exists = "✅" if os.path.exists(URL_SHORTENER['output_file']) else "❌"
        print(f"  {url_shortener_exists} {URL_SHORTENER['output_file']}")

    # Message drafter output file (if enabled)
    if MESSAGE_DRAFTER["enabled"]:
        message_drafter_exists = "✅" if os.path.exists(MESSAGE_DRAFTER['output_file']) else "❌"
        print(f"  {message_drafter_exists} {MESSAGE_DRAFTER['output_file']}")

    # Success criteria - pipeline succeeds if aggregator runs and at least one scraper worked
    if results["aggregator"]["success"]:
        if results["successful_scrapers"] >= len(SCRAPERS):
            print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"All scrapers found content. Daily digest available in: {AGGREGATOR['output_file']}")
        elif results["successful_scrapers"] > 0:
            print(f"\n✅ PIPELINE COMPLETED WITH PARTIAL SUCCESS!")
            print(f"{results['successful_scrapers']}/{len(SCRAPERS)} scrapers found content.")
            print(f"Daily digest available in: {AGGREGATOR['output_file']}")
        else:
            print(f"\n⚠️  PIPELINE COMPLETED BUT NO CONTENT FOUND")
            print(f"All scrapers returned empty results. Check internet connection.")
            print(f"Empty digest available in: {AGGREGATOR['output_file']}")

        # Additional success information for message sending
        if TWILIO_SENDER["enabled"] and "twilio_sender" in results and results["twilio_sender"]["success"]:
            print(f"📱 WhatsApp message sent successfully!")
        elif MESSAGE_DRAFTER["enabled"] and "message_drafter" in results and results["message_drafter"]["success"]:
            print(f"✍️  Message drafted and ready for sending in: {MESSAGE_DRAFTER['output_file']}")
        return True
    else:
        print(f"\n❌ PIPELINE FAILED")
        print(f"../data/Aggregator failed to run. Check logs for details: daily_digest_pipeline.log")
        return False

def main():
    """Main function to run the pipeline."""
    try:
        success = run_pipeline()

        if success:
            print(f"\n💡 Next steps:")
            print(f"  • View digest: python demo_daily_digest.py")
            print(f"  • Check JSON: cat {AGGREGATOR['output_file']}")
            if not URL_SHORTENER["enabled"]:
                print(f"  • Shorten URLs: python tinyurl_shortener.py")
            if not MESSAGE_DRAFTER["enabled"]:
                print(f"  • Draft message: python message_drafter.py")
            if not TWILIO_SENDER["enabled"] and MESSAGE_DRAFTER["enabled"]:
                print(f"  • Send WhatsApp: python twillo.py")
            print(f"../data/  • Review logs: cat daily_digest_pipeline.log")
        else:
            print(f"\n🔧 Troubleshooting:")
            print(f"  • Check individual scraper logs")
            print(f"  • Verify internet connection")
            print(f"  • Review error messages above")
            print(f"../data/  • Check pipeline log: daily_digest_pipeline.log")

        return 0 if success else 1

    except KeyboardInterrupt:
        print(f"\n⏹️  Pipeline interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Pipeline crashed: {e}")
        logging.error(f"Pipeline crashed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
