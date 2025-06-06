# 🔗 TinyURL Shortening Automation for Daily Tech Digest

**Automated URL shortening integration** that seamlessly works with your existing web scraper ecosystem to create shortened, aliased URLs for all content using TinyURL API.

## 🎯 Overview

The TinyURL Shortening Automation script integrates with your Daily Tech Digest pipeline to automatically:
- Read URLs from `daily_tech_digest.json` 
- Shorten each URL using TinyURL API with Bearer authentication
- Apply category-specific aliases (Tech_news_TJI_1, Internship_TJI_1, etc.)
- Generate comprehensive output with both original and shortened URLs
- Provide detailed statistics and error handling

## 🚀 Quick Start

### **Prerequisites**
```bash
# Install dependencies (already included in requirements.txt)
pip install -r requirements.txt

# TinyURL API key is pre-configured in config.py
```

### **Basic Usage**
```bash
# 1. Generate daily digest first (if needed)
python master_scraper.py

# 2. Run TinyURL shortening automation
python tinyurl_shortener.py

# 3. View results
cat shortened_urls_digest.json
```

### **Demo Mode**
```bash
# Test with sample data
python demo_tinyurl_shortener.py
```

## 📊 What It Does

### **Input: `daily_tech_digest.json`**
```json
{
  "daily_tech_digest": {
    "content": {
      "tech_news": {
        "title": "New AI Framework Released",
        "url": "https://example.com/very-long-url-here"
      },
      "internships": {
        "title": "Software Engineer Intern",
        "company": "TechCorp", 
        "url": "https://linkedin.com/jobs/view/12345..."
      }
    }
  }
}
```

### **Output: `shortened_urls_digest.json`**
```json
{
  "shortened_urls_digest": {
    "metadata": {
      "generated_at": "2025-01-25T10:30:00",
      "total_urls_processed": 4,
      "successful_shortenings": 4,
      "success_rate": "100.0%"
    },
    "shortened_urls": [
      {
        "category": "tech_news",
        "title": "New AI Framework Released",
        "original_url": "https://example.com/very-long-url-here",
        "shortened_url": "https://tinyurl.com/Tech-news-TJI-1",
        "alias": "Tech_news_TJI_1",
        "success": true
      }
    ]
  }
}
```

## 🏷️ Alias Tracking System

The system tracks URLs by category with internal aliases for organization:

- **Tech News**: `Tech_news_TJI_1`, `Tech_news_TJI_2`, ...
- **Internships**: `Internship_TJI_1`, `Internship_TJI_2`, ...
- **Jobs**: `Placement_update_TJI_1`, `Placement_update_TJI_2`, ...
- **Upskill Articles**: `Upskill_TJI_1`, `Upskill_TJI_2`, ...

**Note**: TinyURL's free API doesn't support custom aliases, but the system tracks them internally for organization.

## 🔧 API Configuration

### **TinyURL API Settings**
```python
TINYURL_CONFIG = {
    'api_endpoint': 'http://tinyurl.com/api-create.php',
    'request_timeout': 30,
    'max_retries_per_url': 3,
    'delay_between_requests': 1,
    'rate_limit_delay': 5
}
```

### **Authentication**
- **Method**: No authentication required (free API)
- **Request Type**: Simple GET request with URL parameter
- **Format**: `http://tinyurl.com/api-create.php?url={url_to_shorten}`

## 📈 Integration with Existing Workflow

### **Standalone Usage**
```bash
python tinyurl_shortener.py
```

### **Integrated with Master Scraper**
```bash
# Option 1: Sequential execution
python master_scraper.py
python tinyurl_shortener.py

# Option 2: Enable in pipeline (modify run_daily_digest_pipeline.py)
# Set URL_SHORTENER["enabled"] = True
```

### **Automated Daily Workflow**
```bash
# Cron job example
0 9 * * * cd /path/to/project && python master_scraper.py && python tinyurl_shortener.py
```

## 📊 Output Analysis

### **Success Metrics**
- Total URLs processed
- Successful vs failed shortenings  
- Success rate percentage
- Category-wise breakdown
- Processing time statistics

### **Generated Files**
- `shortened_urls_digest.json` - Main output with shortened URLs
- `tinyurl_shortener.log` - Detailed processing logs
- Preserves original `daily_tech_digest.json`

## 🔧 Technical Details

### **API Request Format**
```
GET http://tinyurl.com/api-create.php?url=https://www.example.com/my-really-long-link
```

**Response**: Plain text shortened URL (e.g., `https://tinyurl.com/abc123`)

### **Error Handling**
- **Retry Logic**: Up to 3 attempts per URL with exponential backoff
- **Rate Limiting**: Built-in delays and rate limit detection
- **Alias Conflicts**: Automatic fallback with timestamp suffixes
- **Network Issues**: Comprehensive timeout and connection error handling

### **URL Processing Pipeline**
1. **Load** daily_tech_digest.json
2. **Extract** URLs by category
3. **Generate** category-specific aliases
4. **Call** TinyURL API with Bearer authentication
5. **Handle** responses and errors
6. **Save** comprehensive results

## 🚨 Troubleshooting

### **Common Issues**

**API Authentication Errors:**
- Verify API key is correct in config.py
- Check internet connection
- Ensure TinyURL API service is available

**Alias Conflicts:**
- System automatically handles conflicts with timestamp suffixes
- Check logs for specific alias resolution details

**Network Timeouts:**
- Increase request_timeout in configuration
- Check internet connection stability
- Try running during off-peak hours

### **Debug Commands**
```bash
# Test with sample data
python demo_tinyurl_shortener.py

# Run with verbose logging
python tinyurl_shortener.py  # Check tinyurl_shortener.log

# Check configuration
python -c "from config import TINYURL_CONFIG; print(TINYURL_CONFIG)"
```

## 🎯 Perfect For

- **Daily Automation**: Integrate with existing scraper pipeline
- **Content Sharing**: Clean, branded short URLs for social media
- **Analytics**: Track click-through rates with custom aliases
- **Organization**: Category-based URL management
- **Archiving**: Preserve both original and shortened URLs

## 📁 File Structure

```
tinyurl_shortener.py              # Main automation script
demo_tinyurl_shortener.py         # Demo and testing script
config.py                         # Configuration (updated)
requirements.txt                  # Dependencies
shortened_urls_digest.json        # Output file (generated)
tinyurl_shortener.log            # Processing logs (generated)
```

---

**Ready to get started?** Run `python demo_tinyurl_shortener.py` to see what's possible, then `python tinyurl_shortener.py` to shorten your URLs!
