#!/usr/bin/env python3


import sys
import os

# Import and run the main pipeline
try:
    from run_daily_digest_pipeline import main
    
    if __name__ == "__main__":
        print("🚀 MASTER SCRAPER - DAILY TECH DIGEST")
        print("=" * 50)
        print("Executing all four web scrapers and creating unified digest...\n")
        
        # Run the main pipeline
        exit_code = main()
        sys.exit(exit_code)
        
except ImportError as e:
    print(f"❌ Error: Could not import pipeline runner: {e}")
    print("Make sure run_daily_digest_pipeline.py is in the same directory.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
