#!/usr/bin/env python3
"""
Robust Master Scraper - Daily Tech Digest Pipeline

This is an enhanced version of the master scraper with better error handling,
fallback mechanisms, and the ability to work without external APIs.

Author: Augment Agent
Date: 2025-01-25
"""

import subprocess
import sys
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/robust_pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

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

# Message drafting and sending configuration
MESSAGE_DRAFTER_CONFIG = {
    "name": "TJI Message Drafter",
    "script": "message_drafter.py",
    "output_file": "../data/tji_daily_message.json",
    "timeout": 120,  # 2 minutes
    "enabled": True
}

TWILIO_SENDER_CONFIG = {
    "name": "Twilio WhatsApp Sender",
    "script": "twillo.py",
    "timeout": 60,  # 1 minute
    "enabled": True
}

class RobustPipeline:
    """Robust pipeline that handles failures gracefully."""

    def __init__(self):
        self.scrapers = [
            {
                "name": "Tech News Scraper",
                "script": "demo_tech_news.py",
                "fallback_script": "demo_simple_scraper.py",
                "output_file": "../data/ai_selected_article.json",
                "timeout": 120,
                "required": False
            },
            {
                "name": "Internship Scraper", 
                "script": "internship_scraper.py",
                "fallback_script": "demo_simple_scraper.py",
                "output_file": "../data/selected_internship.json",
                "timeout": 180,
                "required": False
            },
            {
                "name": "Job Scraper",
                "script": "jobs_scraper.py", 
                "fallback_script": "demo_simple_scraper.py",
                "output_file": "../data/selected_job.json",
                "timeout": 180,
                "required": False
            },
            {
                "name": "Upskill Articles Scraper",
                "script": "demo_upskill.py",
                "fallback_script": "demo_simple_scraper.py", 
                "output_file": "../data/ai_selected_upskill_article.json",
                "timeout": 120,
                "required": False
            }
        ]
        
        self.aggregator = {
            "name": "Daily Digest Aggregator",
            "script": "daily_tech_aggregator.py",
            "output_file": "../data/daily_tech_digest.json",
            "timeout": 60,
            "required": True
        }
    
    def run_script_with_fallback(self, scraper: Dict) -> Tuple[bool, str, str, str]:
        """
        Run a scraper script with fallback mechanism.
        
        Returns:
            (success, method_used, stdout, stderr)
        """
        script_name = scraper["script"]
        fallback_script = scraper.get("fallback_script")
        timeout = scraper["timeout"]
        
        # Try main script first
        logging.info(f"Attempting to run {script_name}...")
        success, stdout, stderr = self._run_single_script(script_name, timeout)
        
        if success:
            return True, "main_script", stdout, stderr
        
        # If main script failed and we have a fallback
        if fallback_script and os.path.exists(fallback_script):
            logging.warning(f"{script_name} failed, trying fallback: {fallback_script}")
            
            # For demo_simple_scraper.py, we need to run it in a way that creates the specific output
            if fallback_script == "demo_simple_scraper.py":
                success, stdout, stderr = self._run_fallback_for_specific_output(scraper)
            else:
                success, stdout, stderr = self._run_single_script(fallback_script, timeout)
            
            if success:
                return True, "fallback_script", stdout, stderr
        
        # If everything failed, create a minimal fallback file
        self._create_minimal_fallback(scraper)
        return False, "minimal_fallback", "", stderr
    
    def _run_single_script(self, script_name: str, timeout: int) -> Tuple[bool, str, str]:
        """Run a single script and return results."""
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", f"Timeout after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def _run_fallback_for_specific_output(self, scraper: Dict) -> Tuple[bool, str, str]:
        """Run demo_simple_scraper.py to create specific output file."""
        try:
            # Import and run the specific function
            import demo_simple_scraper
            
            output_file = scraper["output_file"]
            
            if "tech_news" in scraper["name"].lower():
                content = demo_simple_scraper.create_sample_tech_news()
            elif "internship" in scraper["name"].lower():
                content = demo_simple_scraper.create_sample_internships()
            elif "job" in scraper["name"].lower():
                content = demo_simple_scraper.create_sample_jobs()
            elif "upskill" in scraper["name"].lower():
                content = demo_simple_scraper.create_sample_upskill()
            else:
                return False, "", "Unknown scraper type"
            
            # Save the content
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            return True, f"Created fallback content for {output_file}", ""
            
        except Exception as e:
            return False, "", str(e)
    
    def _create_minimal_fallback(self, scraper: Dict):
        """Create a minimal fallback file."""
        try:
            fallback_content = {
                "message": f"No suitable content found for {scraper['name']}",
                "status": "no_content",
                "timestamp": datetime.now().isoformat(),
                "scraper": scraper["name"],
                "method": "minimal_fallback"
            }
            
            with open(scraper["output_file"], 'w', encoding='utf-8') as f:
                json.dump(fallback_content, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Created minimal fallback for {scraper['output_file']}")
            
        except Exception as e:
            logging.error(f"Failed to create minimal fallback: {e}")
    
    def check_output_file(self, file_path: str) -> bool:
        """Check if output file exists and has content."""
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                return size > 0
            return False
        except:
            return False

    def cleanup_output_files(self) -> dict:
        """
        Clean up output files from previous pipeline runs while preserving persistent data.

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

    def run_message_drafter(self) -> Tuple[bool, str]:
        """Run the message drafter script."""
        try:
            print(f"📊 OPTIONAL STEP: {MESSAGE_DRAFTER_CONFIG['name']}")
            print("-" * 40)

            start_time = time.time()
            success, stdout, stderr = self._run_single_script(
                MESSAGE_DRAFTER_CONFIG['script'],
                MESSAGE_DRAFTER_CONFIG['timeout']
            )
            end_time = time.time()

            # Check output file
            output_exists = self.check_output_file(MESSAGE_DRAFTER_CONFIG['output_file'])

            if success and output_exists:
                print(f"✅ {MESSAGE_DRAFTER_CONFIG['name']} completed successfully")
                result_msg = "success"
            else:
                print(f"❌ {MESSAGE_DRAFTER_CONFIG['name']} failed")
                if stderr:
                    print(f"Error: {stderr[:200]}...")
                result_msg = "failed"

            print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds\n")
            return success and output_exists, result_msg

        except Exception as e:
            logging.error(f"Message drafter failed: {e}")
            print(f"❌ {MESSAGE_DRAFTER_CONFIG['name']} crashed: {e}\n")
            return False, "crashed"

    def run_twilio_sender(self) -> Tuple[bool, str]:
        """Run the Twilio WhatsApp sender script."""
        try:
            print(f"📊 OPTIONAL STEP: {TWILIO_SENDER_CONFIG['name']}")
            print("-" * 40)

            start_time = time.time()
            success, stdout, stderr = self._run_single_script(
                TWILIO_SENDER_CONFIG['script'],
                TWILIO_SENDER_CONFIG['timeout']
            )
            end_time = time.time()

            if success:
                print(f"✅ {TWILIO_SENDER_CONFIG['name']} completed successfully")
                if "Message sent!" in stdout:
                    print(f"📱 WhatsApp message sent successfully!")
                result_msg = "success"
            else:
                print(f"❌ {TWILIO_SENDER_CONFIG['name']} failed")
                if stderr:
                    print(f"Error: {stderr[:200]}...")
                result_msg = "failed"

            print(f"⏱️  Execution time: {end_time - start_time:.1f} seconds\n")
            return success, result_msg

        except Exception as e:
            logging.error(f"Twilio sender failed: {e}")
            print(f"❌ {TWILIO_SENDER_CONFIG['name']} crashed: {e}\n")
            return False, "crashed"
    
    def run_pipeline(self) -> bool:
        """Run the complete pipeline with robust error handling."""
        print("🛡️  ROBUST DAILY TECH DIGEST PIPELINE")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Enhanced with fallback mechanisms and error recovery\n")

        start_time = time.time()
        results = {
            "scrapers": {},
            "cleanup": None,
            "successful_scrapers": 0,
            "failed_scrapers": 0,
            "fallback_used": 0,
            "message_drafter": None,
            "twilio_sender": None
        }

        # Step 0: Cleanup previous output files
        try:
            cleanup_stats = self.cleanup_output_files()
            results["cleanup"] = cleanup_stats
        except Exception as e:
            logging.error(f"Cleanup failed: {e}")
            print(f"⚠️  Cleanup failed: {e}")
            print("Continuing with pipeline execution...\n")
            results["cleanup"] = {"error": str(e)}
        
        # Run each scraper
        for i, scraper in enumerate(self.scrapers, 1):
            print(f"📊 STEP {i}/{len(self.scrapers)}: {scraper['name']}")
            print("-" * 40)
            
            scraper_start = time.time()
            success, method, stdout, stderr = self.run_script_with_fallback(scraper)
            scraper_end = time.time()
            
            # Check output file
            output_exists = self.check_output_file(scraper['output_file'])
            
            # Store results
            results["scrapers"][scraper['name']] = {
                "success": success,
                "method": method,
                "output_exists": output_exists,
                "execution_time": scraper_end - scraper_start
            }
            
            # Report status
            if output_exists:
                results["successful_scrapers"] += 1
                if method == "main_script":
                    print(f"✅ {scraper['name']} completed successfully")
                elif method == "fallback_script":
                    print(f"⚠️  {scraper['name']} completed using fallback")
                    results["fallback_used"] += 1
                else:
                    print(f"🔄 {scraper['name']} completed with minimal fallback")
                    results["fallback_used"] += 1
            else:
                results["failed_scrapers"] += 1
                print(f"❌ {scraper['name']} failed completely")
            
            print(f"⏱️  Execution time: {scraper_end - scraper_start:.1f}s\n")
            time.sleep(1)  # Brief pause between scrapers
        
        # Run aggregator
        print(f"📊 FINAL STEP: {self.aggregator['name']}")
        print("-" * 40)
        
        agg_start = time.time()
        agg_success, agg_stdout, agg_stderr = self._run_single_script(
            self.aggregator['script'], 
            self.aggregator['timeout']
        )
        agg_end = time.time()
        
        agg_output_exists = self.check_output_file(self.aggregator['output_file'])
        
        if agg_success and agg_output_exists:
            print(f"✅ {self.aggregator['name']} completed successfully")
        else:
            print(f"❌ {self.aggregator['name']} failed")
            if agg_stderr:
                print(f"Error: {agg_stderr[:200]}...")
        
        print(f"⏱️  Execution time: {agg_end - agg_start:.1f}s\n")

        # Message drafting step (if enabled and aggregator succeeded)
        if MESSAGE_DRAFTER_CONFIG["enabled"] and agg_success and agg_output_exists:
            message_success, message_status = self.run_message_drafter()
            results["message_drafter"] = message_status

            # Twilio sender step (if enabled and message drafter succeeded)
            if TWILIO_SENDER_CONFIG["enabled"] and message_success:
                twilio_success, twilio_status = self.run_twilio_sender()
                results["twilio_sender"] = twilio_status
            elif TWILIO_SENDER_CONFIG["enabled"]:
                print(f"⏭️  Skipping Twilio sender (message drafter failed)\n")
                results["twilio_sender"] = "skipped"
        elif MESSAGE_DRAFTER_CONFIG["enabled"]:
            print(f"⏭️  Skipping message drafter (aggregator failed)\n")
            results["message_drafter"] = "skipped"

        # Final summary
        total_time = time.time() - start_time
        
        print("📋 ROBUST PIPELINE SUMMARY")
        print("=" * 60)
        print(f"🕒 Total execution time: {total_time:.1f} seconds")

        # Cleanup summary
        if results["cleanup"] and "error" not in results["cleanup"]:
            cleanup_status = f"✅ Success ({results['cleanup']['total_cleared']} files cleared)"
        elif results["cleanup"] and "error" in results["cleanup"]:
            cleanup_status = f"❌ Failed ({results['cleanup']['error']})"
        else:
            cleanup_status = "⚪ Not performed"
        print(f"🧹 Cleanup: {cleanup_status}")

        print(f"✅ Successful scrapers: {results['successful_scrapers']}/{len(self.scrapers)}")
        print(f"🔄 Fallbacks used: {results['fallback_used']}")
        print(f"❌ Failed scrapers: {results['failed_scrapers']}")

        aggregator_status = "✅ Success" if agg_success and agg_output_exists else "❌ Failed"
        print(f"🔄 Aggregator: {aggregator_status}")

        # Message drafter status
        if MESSAGE_DRAFTER_CONFIG["enabled"]:
            if results["message_drafter"] == "success":
                print(f"✍️  Message Drafter: ✅ Success")
            elif results["message_drafter"] == "skipped":
                print(f"✍️  Message Drafter: ⏭️ Skipped (aggregator failed)")
            else:
                print(f"✍️  Message Drafter: ❌ Failed")
        else:
            print(f"✍️  Message Drafter: ⚪ Disabled")

        # Twilio sender status
        if TWILIO_SENDER_CONFIG["enabled"]:
            if results["twilio_sender"] == "success":
                print(f"📱 WhatsApp Sender: ✅ Success")
            elif results["twilio_sender"] == "skipped":
                print(f"📱 WhatsApp Sender: ⏭️ Skipped (message drafter failed)")
            else:
                print(f"📱 WhatsApp Sender: ❌ Failed")
        else:
            print(f"📱 WhatsApp Sender: ⚪ Disabled")
        
        # Check final output files
        print(f"\n📁 OUTPUT FILES:")
        all_files_exist = True
        
        for scraper in self.scrapers:
            exists = "✅" if os.path.exists(scraper['output_file']) else "❌"
            print(f"  {exists} {scraper['output_file']}")
            if not os.path.exists(scraper['output_file']):
                all_files_exist = False
        
        agg_exists = "✅" if os.path.exists(self.aggregator['output_file']) else "❌"
        print(f"  {agg_exists} {self.aggregator['output_file']}")

        # Message drafter output file (if enabled)
        if MESSAGE_DRAFTER_CONFIG["enabled"]:
            message_exists = "✅" if os.path.exists(MESSAGE_DRAFTER_CONFIG['output_file']) else "❌"
            print(f"  {message_exists} {MESSAGE_DRAFTER_CONFIG['output_file']}")
        
        # Determine overall success
        pipeline_success = (agg_success and agg_output_exists and 
                          results['successful_scrapers'] >= 1)
        
        if pipeline_success:
            print(f"\n🎉 ROBUST PIPELINE COMPLETED!")
            print(f"Daily digest available in: {self.aggregator['output_file']}")
            if results['fallback_used'] > 0:
                print(f"⚠️  Note: {results['fallback_used']} scrapers used fallback methods")

            # Additional success information for message sending
            if TWILIO_SENDER_CONFIG["enabled"] and results["twilio_sender"] == "success":
                print(f"📱 WhatsApp message sent successfully!")
            elif MESSAGE_DRAFTER_CONFIG["enabled"] and results["message_drafter"] == "success":
                print(f"✍️  Message drafted and ready for sending in: {MESSAGE_DRAFTER_CONFIG['output_file']}")
        else:
            print(f"\n❌ PIPELINE FAILED")
            print("../data/Check logs for details: robust_pipeline.log")
        
        return pipeline_success

def main():
    """Main function."""
    try:
        pipeline = RobustPipeline()
        success = pipeline.run_pipeline()
        
        if success:
            print(f"\n💡 Next steps:")
            print(f"  • View digest: python demo_daily_digest.py")
            print(f"../data/  • Check JSON: cat daily_tech_digest.json")
            if not MESSAGE_DRAFTER_CONFIG["enabled"]:
                print(f"  • Draft message: python message_drafter.py")
            if not TWILIO_SENDER_CONFIG["enabled"] and MESSAGE_DRAFTER_CONFIG["enabled"]:
                print(f"  • Send WhatsApp: python twillo.py")
            print(f"../data/  • Review logs: cat robust_pipeline.log")
        else:
            print(f"\n🔧 Troubleshooting:")
            print(f"../data/  • Check logs: robust_pipeline.log")
            print(f"  • Try: python demo_simple_scraper.py")
            print(f"  • Then: python daily_tech_aggregator.py")
        
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
