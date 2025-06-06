#!/usr/bin/env python3
"""
TJI Project Reorganization Script

This script reorganizes the TJI automation project into a proper directory structure
for GitHub upload and updates all file path references accordingly.
"""

import os
import shutil
import re
from pathlib import Path

# Directory structure mapping
DIRECTORY_STRUCTURE = {
    'scrapers': [
        'demo_tech_news.py',
        'internship_scraper.py', 
        'jobs_scraper.py',
        'upskill_scraper.py',
        'webscraptest.py'
    ],
    'processors': [
        'daily_tech_aggregator.py',
        'message_drafter.py',
        'tinyurl_shortener.py',
        'run_daily_digest_pipeline.py',
        'master_scraper_robust.py',
        'master_scraper.py',
        'fallback_selector.py'
    ],
    'data': [
        # JSON files - will be moved dynamically
    ],
    'messaging': [
        'twillo.py'
    ],
    'tests': [
        'demo_clean_digest.py',
        'demo_cleanup_mechanism.py', 
        'demo_daily_digest.py',
        'demo_enhanced_tech_news.py',
        'demo_master_scraper.py',
        'demo_simple_scraper.py',
        'demo_tinyurl_shortener.py',
        'demo_upskill.py',
        'demo_url_management.py',
        'debug_linkedin_structure.py',
        'manage_upskill_urls.py',
        'simple_cleanup_test.py',
        'test_alias_format.py',
        'test_api_integration.py',
        'test_cleanup_mechanism.py',
        'test_groq_api.py',
        'test_scrapers.py',
        'test_tinyurl_api.py',
        'test_tinyurl_api_key.py',
        'test_tinyurl_counter.py',
        'test_tinyurl_integration.py',
        'test_twilio_integration.py',
        'test_upskill_deduplication.py'
    ],
    'docs': [
        'README_CLEANUP_MECHANISM.md',
        'README_CLEAN_DIGEST.md',
        'README_DAILY_DIGEST.md',
        'README_ENHANCED_TECH_NEWS.md',
        'README_MASTER_SCRAPER.md',
        'README_TINYURL_SHORTENER.md',
        'README_TWILIO_INTEGRATION.md',
        'README_UPSKILL_DEDUPLICATION.md',
        'README_UPSKILL_SCRAPER.md'
    ],
    'config': [
        'config.py',
        'api_manager.py',
        'api_config_template.json'
    ]
}

# Path mappings for updating file references
PATH_MAPPINGS = {
    # From scrapers to data
    'scrapers': {
        'data_files': '../data/',
        'config_files': '../config/',
        'processors': '../processors/'
    },
    # From processors to data  
    'processors': {
        'data_files': '../data/',
        'config_files': '../config/',
        'scrapers': '../scrapers/',
        'messaging': '../messaging/'
    },
    # From messaging to data
    'messaging': {
        'data_files': '../data/',
        'config_files': '../config/',
        'processors': '../processors/'
    },
    # From tests to other directories
    'tests': {
        'data_files': '../data/',
        'config_files': '../config/',
        'scrapers': '../scrapers/',
        'processors': '../processors/',
        'messaging': '../messaging/'
    }
}

def create_directories():
    """Create the target directory structure."""
    print("📁 Creating directory structure...")
    
    for directory in DIRECTORY_STRUCTURE.keys():
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ Created: {directory}/")
    
    print()

def move_files():
    """Move files to their appropriate directories."""
    print("📦 Moving files to appropriate directories...")
    
    # Move categorized files
    for target_dir, files in DIRECTORY_STRUCTURE.items():
        if target_dir == 'data':  # Handle data files separately
            continue
            
        for file_name in files:
            if os.path.exists(file_name):
                target_path = os.path.join(target_dir, file_name)
                shutil.move(file_name, target_path)
                print(f"  ✅ Moved: {file_name} → {target_path}")
            else:
                print(f"  ⚠️  Not found: {file_name}")
    
    # Move all JSON files to data directory
    print(f"\n📊 Moving JSON files to data/...")
    for file_name in os.listdir('.'):
        if file_name.endswith('.json'):
            target_path = os.path.join('data', file_name)
            shutil.move(file_name, target_path)
            print(f"  ✅ Moved: {file_name} → {target_path}")
    
    # Move log files to data directory
    print(f"\n📋 Moving log files to data/...")
    for file_name in os.listdir('.'):
        if file_name.endswith('.log'):
            target_path = os.path.join('data', file_name)
            shutil.move(file_name, target_path)
            print(f"  ✅ Moved: {file_name} → {target_path}")
    
    print()

def update_file_paths_in_script(file_path, source_dir):
    """Update file path references in a Python script."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update JSON file references
        json_patterns = [
            r'open\s*\(\s*["\']([^"\']+\.json)["\']',
            r'with\s+open\s*\(\s*["\']([^"\']+\.json)["\']',
            r'["\']([^"\']*\.json)["\']'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if not match.startswith('../') and not match.startswith('./'):
                    # Simple filename, needs path update
                    new_path = PATH_MAPPINGS[source_dir]['data_files'] + match
                    content = content.replace(f'"{match}"', f'"{new_path}"')
                    content = content.replace(f"'{match}'", f"'{new_path}'")
        
        # Update log file references
        log_patterns = [
            r'open\s*\(\s*["\']([^"\']+\.log)["\']',
            r'with\s+open\s*\(\s*["\']([^"\']+\.log)["\']',
            r'["\']([^"\']*\.log)["\']'
        ]
        
        for pattern in log_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if not match.startswith('../') and not match.startswith('./'):
                    new_path = PATH_MAPPINGS[source_dir]['data_files'] + match
                    content = content.replace(f'"{match}"', f'"{new_path}"')
                    content = content.replace(f"'{match}'", f"'{new_path}'")
        
        # Update config imports
        config_imports = [
            r'from\s+config\s+import',
            r'import\s+config',
            r'from\s+api_manager\s+import',
            r'import\s+api_manager'
        ]
        
        for pattern in config_imports:
            if re.search(pattern, content):
                if source_dir != 'config':
                    # Add relative import path
                    content = re.sub(r'from\s+config\s+import', 'from ..config.config import', content)
                    content = re.sub(r'import\s+config(?!\w)', 'import config.config as config', content)
                    content = re.sub(r'from\s+api_manager\s+import', 'from ..config.api_manager import', content)
                    content = re.sub(r'import\s+api_manager(?!\w)', 'import config.api_manager as api_manager', content)
        
        # Save updated content if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ Error updating {file_path}: {e}")
        return False

def update_all_file_paths():
    """Update file path references in all moved Python scripts."""
    print("🔧 Updating file path references...")
    
    for directory in DIRECTORY_STRUCTURE.keys():
        if directory == 'data' or directory == 'docs':
            continue
            
        print(f"\n  📂 Updating files in {directory}/...")
        
        if os.path.exists(directory):
            for file_name in os.listdir(directory):
                if file_name.endswith('.py'):
                    file_path = os.path.join(directory, file_name)
                    updated = update_file_paths_in_script(file_path, directory)
                    
                    if updated:
                        print(f"    ✅ Updated: {file_path}")
                    else:
                        print(f"    ⚪ No changes: {file_path}")

def create_main_readme():
    """Create a main README.md file for the project."""
    readme_content = """# TJI Automation Project

Automated daily tech digest pipeline with web scraping, content curation, and WhatsApp delivery.

## Directory Structure

```
tji-auto/
├── scrapers/           # Web scraping scripts
├── processors/         # Data processing and aggregation
├── data/              # JSON files and persistent data
├── messaging/         # WhatsApp/Twilio integration
├── tests/             # Test scripts and demos
├── docs/              # Documentation files
└── config/            # Configuration and API management
```

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure API keys:
   ```bash
   cp config/api_config_template.json config/api_config.json
   # Edit api_config.json with your API keys
   ```

3. Run the complete pipeline:
   ```bash
   python processors/run_daily_digest_pipeline.py
   ```

## Documentation

See the `docs/` directory for detailed documentation on each component.

## Features

- 🔍 **Web Scraping**: Tech news, internships, jobs, upskill articles
- 🤖 **AI Curation**: Intelligent content selection using Groq API
- 🔗 **URL Shortening**: TinyURL integration with custom aliases
- ✍️ **Message Drafting**: AI-powered professional message formatting
- 📱 **WhatsApp Delivery**: Automated message sending via Twilio
- 🧹 **Smart Cleanup**: Automatic file management with deduplication
- 🛡️ **Robust Pipeline**: Error handling and fallback mechanisms

## License

MIT License - see LICENSE file for details.
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📝 Created main README.md")

def main():
    """Main reorganization function."""
    print("🚀 TJI PROJECT REORGANIZATION")
    print("=" * 50)
    print("Restructuring project for GitHub upload...\n")
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Move files
    move_files()
    
    # Step 3: Update file paths
    update_all_file_paths()
    
    # Step 4: Create main README
    create_main_readme()
    
    print("✅ REORGANIZATION COMPLETE!")
    print("=" * 50)
    print("Project has been successfully reorganized.")
    print("\n📁 New structure:")
    for directory in DIRECTORY_STRUCTURE.keys():
        if os.path.exists(directory):
            file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
            print(f"  📂 {directory}/ ({file_count} files)")
    
    print(f"\n💡 Next steps:")
    print(f"  • Test the reorganized scripts")
    print(f"  • Update any remaining hardcoded paths")
    print(f"  • Commit to Git: git add . && git commit -m 'Reorganize project structure'")
    print(f"  • Push to GitHub: git push origin main")

if __name__ == "__main__":
    main()
