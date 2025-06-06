# Upskill Article Deduplication System

## Overview

The upskill article scraper now includes a comprehensive deduplication system that prevents the same articles from being selected repeatedly across multiple script runs. This ensures that users receive fresh, unique learning content in their daily tech digest.

## Features

### 🔄 **Persistent History Tracking**
- Maintains a rolling 30-day history of previously selected articles
- Tracks both article titles and URLs for comprehensive duplicate detection
- Automatically cleans old entries to maintain optimal performance

### 🎯 **Smart Filtering**
- Filters out previously selected articles BEFORE AI analysis
- Reduces processing time by analyzing only new content
- Provides detailed statistics on filtering effectiveness

### 📊 **Comprehensive Logging**
- Logs deduplication statistics in console output
- Shows how many articles were filtered vs. analyzed
- Displays history file status and entry counts

### 🛡️ **Robust Error Handling**
- Gracefully handles missing or corrupted history files
- Falls back to original behavior if deduplication fails
- Provides clear error messages and suggestions

## How It Works

### 1. **Article Collection**
```
Scraper finds articles → Session deduplication → Cross-run deduplication → AI selection
```

### 2. **Deduplication Process**
1. **Session Deduplication**: Removes duplicates within the current scraping session (by URL)
2. **Historical Deduplication**: Filters out articles selected in previous runs (by title and URL)
3. **AI Analysis**: Only new, unique articles are sent to the AI for selection
4. **History Update**: Selected article is added to persistent history

### 3. **History Management**
- **File**: `upskill_articles_history.json`
- **Format**: JSON with title/URL keys and selection timestamps
- **Retention**: 30 days (configurable via `HISTORY_DAYS` constant)
- **Cleanup**: Automatic removal of expired entries

## Configuration

### Constants in `upskill_scraper.py`:
```python
UPSKILL_HISTORY_FILE = "upskill_articles_history.json"  # History file name
HISTORY_DAYS = 30  # Rolling window in days
```

## Output Examples

### Console Output with Deduplication Stats:
```
📊 DEDUPLICATION STATS:
  • Total articles scraped: 35
  • Previously selected (filtered): 2
  • New articles analyzed: 33
  • Selection method: AI

📊 DEDUPLICATION HISTORY STATUS:
  • History entries: 8
  • Rolling window: 30 days
  • Tracks both titles and URLs
  • History file: upskill_articles_history.json
```

### AI Selection Result with Deduplication Metadata:
```json
{
  "selected_article": {
    "title": "Building Modern APIs with Python",
    "url": "https://example.com/python-apis"
  },
  "ai_reasoning": "Selected for practical learning value...",
  "total_articles_scraped": 35,
  "total_articles_analyzed": 33,
  "previously_selected_filtered": 2,
  "selection_criteria": "Practical learning value, technology relevance, skill building potential",
  "deduplication_enabled": true
}
```

## Key Functions

### `load_upskill_history()`
- Loads history from JSON file
- Automatically cleans expired entries
- Returns dictionary of title/URL keys with timestamps

### `save_upskill_history(history)`
- Saves history dictionary to JSON file
- Handles file I/O errors gracefully

### `add_to_upskill_history(article)`
- Adds selected article to history
- Creates both title and URL keys for comprehensive tracking
- Automatically saves updated history

### `filter_previously_selected(articles)`
- Filters out articles that have been previously selected
- Compares both titles and URLs (case-insensitive)
- Returns list of new, unique articles

## Integration with Existing Workflow

The deduplication system is seamlessly integrated into the existing upskill scraper workflow:

1. **No Breaking Changes**: Existing functionality remains unchanged
2. **Backward Compatible**: Works with or without history file
3. **Transparent Operation**: Deduplication happens automatically
4. **Enhanced Metadata**: Additional statistics in output files

## Benefits

### For Users:
- ✅ **Fresh Content**: Never see the same article twice
- ✅ **Diverse Learning**: Broader range of topics over time
- ✅ **Efficient Discovery**: Focus on new, relevant content

### For System:
- ✅ **Reduced Processing**: AI analyzes fewer articles
- ✅ **Better Performance**: Faster execution with filtering
- ✅ **Smart Resource Usage**: Optimal API usage

## Troubleshooting

### Common Scenarios:

**All articles filtered out:**
```
❌ AI selection failed: All articles have been previously selected
  • Total articles found: 25
  • All articles were previously selected
  • Suggestion: Try running the scraper again later for new content
```

**History file issues:**
- Missing file: Creates new history automatically
- Corrupted file: Falls back to empty history with warning
- Permission errors: Logs error and continues without history

### Manual History Management:

**View current history:**
```python
from upskill_scraper import load_upskill_history
history = load_upskill_history()
print(f"History entries: {len(history)}")
```

**Clear history (if needed):**
```bash
rm upskill_articles_history.json
```

## Future Enhancements

- **Configurable retention period** per user preferences
- **Category-based deduplication** for different article types
- **Export/import functionality** for history management
- **Advanced similarity detection** beyond exact title/URL matching
