# 🧹 Automatic Cleanup Mechanism for TJI Daily Pipeline

## Overview

The TJI Daily Pipeline now includes an automatic cleanup mechanism that clears specific output files at the beginning of each execution to ensure fresh data generation while preserving critical historical data for deduplication systems.

## 🎯 Purpose

- **Fresh Data Generation**: Ensures each pipeline run starts with clean output files
- **Prevent Stale Data**: Eliminates confusion from previous run results
- **Preserve Deduplication**: Maintains historical data needed for duplicate prevention
- **Automated Operation**: Runs automatically without manual intervention

## 🗂️ File Categories

### 📤 **Output Files (CLEARED)**
These files are automatically cleared before each pipeline run:

```
ai_selected_article.json           # Tech news AI selection
ai_selected_upskill_article.json   # Upskill article AI selection  
daily_tech_digest.json             # Aggregated daily digest
filtered_internships.json          # Filtered internship results
filtered_jobs.json                 # Filtered job results
selected_internship.json           # AI-selected best internship
selected_job.json                  # AI-selected best job
shortened_urls_digest.json         # URL shortening results
todays_tech_news.json              # Scraped tech news
tji_daily_message.json             # Formatted message output
upskill_articles.json              # Scraped upskill articles
```

### 🛡️ **Persistent Files (PRESERVED)**
These files are **NEVER** cleared and maintain historical data:

```
upskill_articles_history.json      # Upskill deduplication history
tech_news_history.json             # Tech news deduplication history
seen_internships.json              # Internship deduplication tracking
seen_jobs.json                     # Job deduplication tracking
tinyurl_run_counter.json           # URL shortening counter
```

## 🔧 Implementation

### Integration Points

The cleanup mechanism is integrated into:

1. **`run_daily_digest_pipeline.py`** - Main pipeline orchestrator
2. **`master_scraper_robust.py`** - Robust pipeline with fallbacks

### Execution Flow

```
Pipeline Start → Cleanup Files → Run Scrapers → Aggregate Results → Complete
```

### Function Signature

```python
def cleanup_output_files() -> dict:
    """
    Clean up output files from previous pipeline runs while preserving persistent data.
    
    Returns:
        Dictionary with cleanup statistics and results
    """
```

## 📊 Cleanup Statistics

The cleanup function returns detailed statistics:

```python
{
    "files_cleared": ["file1.json", "file2.json"],
    "files_not_found": ["file3.json"],
    "files_preserved": ["history1.json", "history2.json"],
    "errors": [],
    "total_cleared": 2,
    "total_preserved": 2
}
```

## 🖥️ Console Output

### Successful Cleanup
```
🧹 CLEANUP: Clearing previous output files...
--------------------------------------------------
  ✅ Cleared: ai_selected_article.json
  ✅ Cleared: daily_tech_digest.json
  ⚪ Not found: selected_internship.json
  ⚪ Not found: selected_job.json

🛡️  PRESERVED: Checking persistent files...
  🛡️  Preserved: tech_news_history.json (1024 bytes)
  🛡️  Preserved: upskill_articles_history.json (512 bytes)
  ⚪ Not found: seen_internships.json

📊 CLEANUP SUMMARY:
  • Files cleared: 2
  • Files preserved: 2
  • Errors: 0
  ✅ Cleanup completed successfully
```

### Pipeline Summary Integration
```
📋 PIPELINE SUMMARY
============================================================
🕒 Total execution time: 125.3 seconds
🧹 Cleanup: ✅ Success (3 files cleared)
✅ Successful scrapers: 4/4
❌ Failed scrapers: 0/4
🔄 Aggregator: ✅ Success
```

## 🚨 Error Handling

### Graceful Degradation
- **File Permission Errors**: Logged but pipeline continues
- **Missing Files**: Normal operation (files may not exist)
- **Cleanup Failure**: Pipeline continues with warning

### Error Scenarios
```
🧹 CLEANUP: Clearing previous output files...
--------------------------------------------------
  ✅ Cleared: ai_selected_article.json
  ❌ Error: daily_tech_digest.json - Permission denied
  ⚪ Not found: selected_internship.json

📊 CLEANUP SUMMARY:
  • Files cleared: 1
  • Files preserved: 2
  • Errors: 1
  ⚠️  Cleanup errors occurred - check logs for details
```

## 🔧 Configuration

### Adding New Files to Clear
Edit the configuration in pipeline scripts:

```python
OUTPUT_FILES_TO_CLEAR = [
    "ai_selected_article.json",
    "new_output_file.json",  # Add new files here
    # ... existing files
]
```

### Adding New Persistent Files
Edit the preservation list:

```python
PERSISTENT_FILES_TO_PRESERVE = [
    "tech_news_history.json",
    "new_history_file.json",  # Add new persistent files here
    # ... existing files
]
```

## 🧪 Testing

### Manual Testing
```bash
# Create test files
echo '{"test": true}' > ai_selected_article.json
echo '{"test": true}' > daily_tech_digest.json

# Run pipeline (cleanup will occur automatically)
python run_daily_digest_pipeline.py

# Verify files were cleared
ls -la *.json
```

### Automated Testing
```bash
# Run the cleanup test
python simple_cleanup_test.py
```

## 📝 Logging

### Log Levels
- **INFO**: Successful file operations
- **DEBUG**: Files not found (normal)
- **WARNING**: Cleanup completed with errors
- **ERROR**: Individual file operation failures

### Log Examples
```
2025-06-07 00:15:30,123 - INFO - 🧹 Starting automatic cleanup of output files...
2025-06-07 00:15:30,124 - INFO - ✅ Cleared: ai_selected_article.json (1024 bytes)
2025-06-07 00:15:30,125 - DEBUG - ⚪ Not found: selected_internship.json
2025-06-07 00:15:30,126 - INFO - 🛡️  Preserved: tech_news_history.json (512 bytes)
2025-06-07 00:15:30,127 - INFO - Cleanup completed successfully: 2 files cleared
```

## ✅ Benefits

### For Users
- **Consistent Results**: Each run produces fresh, current data
- **No Confusion**: Clear separation between runs
- **Reliable Operation**: Automated without manual intervention

### For System
- **Data Integrity**: Prevents mixing old and new data
- **Deduplication Preserved**: Historical data remains intact
- **Clean State**: Each execution starts from known state

### For Maintenance
- **Predictable Behavior**: Known file state at start
- **Easy Debugging**: Clear logs of cleanup operations
- **Flexible Configuration**: Easy to add/remove files

## 🔄 Integration with Existing Systems

### Deduplication Systems
- **Upskill Articles**: History preserved in `upskill_articles_history.json`
- **Tech News**: History preserved in `tech_news_history.json`
- **Internships**: Tracking preserved in `seen_internships.json`
- **Jobs**: Tracking preserved in `seen_jobs.json`

### URL Shortening
- **Counter Persistence**: `tinyurl_run_counter.json` preserved for sequential numbering

### Message Drafting
- **Fresh Templates**: Previous message drafts cleared for new generation

## 🚀 Usage

The cleanup mechanism runs automatically when you execute:

```bash
# Main pipeline (includes cleanup)
python run_daily_digest_pipeline.py

# Alternative entry point
python master_scraper.py

# Robust pipeline (includes cleanup)
python master_scraper_robust.py
```

No manual intervention required - cleanup happens automatically at the start of each pipeline execution!
