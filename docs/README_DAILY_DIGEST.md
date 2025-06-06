# 📅 Daily Tech Digest Aggregator

A unified aggregator that consolidates AI-selected content from all four existing scrapers into a single, comprehensive daily tech digest for computer science students.

## 🎯 Purpose

The Daily Tech Digest Aggregator creates a **one-stop daily briefing** by combining the best content from:
- **Tech News** - Latest industry developments and breakthroughs
- **Internships** - Best internship opportunities for CS students  
- **Jobs/Placements** - Top job opportunities for fresh graduates
- **Upskill Articles** - Most valuable learning resources and tutorials

## 📊 Input Sources

### **Required Input Files:**
1. `ai_selected_article.json` - Tech news scraper output
2. `selected_internship.json` - Internship scraper output  
3. `selected_job.json` - Job scraper output
4. `ai_selected_upskill_article.json` - Upskill articles scraper output

### **Flexible Format Support:**
- **Full AI Structure**: Complete scraper output with AI reasoning
- **Simple Format**: Basic title/URL structure for compatibility
- **Mixed Sources**: Handles different formats from different scrapers

## 🚀 Quick Start

### **Generate Daily Digest**
```bash
# Run all scrapers first (if needed)
python demo_tech_news.py
python internship_scraper.py  
python jobs_scraper.py
python demo_upskill.py

# Create unified digest
python daily_tech_aggregator.py
```

### **View Digest Demo**
```bash
python demo_daily_digest.py
```

## 📁 Output Structure

### **Main Output File: `daily_tech_digest.json`**

```json
{
  "daily_tech_digest": {
    "metadata": {
      "generated_at": "2025-01-25T10:30:00",
      "aggregator_version": "1.0",
      "total_sources": 4,
      "successful_sources": 4,
      "failed_sources": 0,
      "source_files": {
        "tech_news": {
          "file_path": "ai_selected_article.json",
          "display_name": "Tech News",
          "exists": true,
          "loaded_successfully": true,
          "last_modified": "2025-01-25T09:15:00"
        }
        // ... other sources
      }
    },
    "summary": {
      "tech_news": {
        "count": 1,
        "status": "success", 
        "title": "Google's Veo 3 AI video generator...",
        "ai_analysis_available": false
      },
      "internships": {
        "count": 1,
        "status": "success",
        "title": "AI/ML Engineer Intern",
        "ai_analysis_available": true
      },
      "jobs": {
        "count": 1, 
        "status": "success",
        "title": "Engineer",
        "ai_analysis_available": true
      },
      "upskill_articles": {
        "count": 1,
        "status": "success", 
        "title": "Anomaly Detection in Python...",
        "ai_analysis_available": true
      }
    },
    "content": {
      "tech_news": {
        "title": "Google's Veo 3 AI video generator is a slop monger's dream",
        "url": "https://www.theverge.com/ai-artificial-intelligence/..."
      },
      "internships": {
        "title": "AI/ML Engineer Intern",
        "company": "DraconX", 
        "url": "https://in.linkedin.com/jobs/view/...",
        "ai_reasoning": "Selected by AI as most valuable opportunity"
      },
      "jobs": {
        "title": "Engineer",
        "company": "LSEG",
        "url": "https://in.linkedin.com/jobs/view/...",
        "ai_reasoning": "Selected by AI as most valuable opportunity"
      },
      "upskill_articles": {
        "selected_article": {
          "title": "Anomaly Detection in Python with Isolation Forest",
          "url": "https://www.digitalocean.com/community/tutorials/..."
        },
        "ai_reasoning": "Excellent practical learning resource...",
        "total_articles_analyzed": 25
      }
    }
  }
}
```

## ✨ Key Features

### **Robust Error Handling**
- **Missing Files**: Gracefully handles missing scraper outputs
- **Malformed JSON**: Validates and reports JSON parsing errors
- **Mixed Formats**: Supports both AI-enhanced and simple formats
- **Partial Success**: Creates digest even if some sources fail

### **Comprehensive Metadata**
- **Generation Timestamp**: When the digest was created
- **Source File Status**: Existence, loading success, modification times
- **Success Metrics**: Count of successful vs failed sources
- **Version Tracking**: Aggregator version for compatibility

### **Content Organization**
- **Structured Order**: Tech News → Internships → Jobs → Upskill Articles
- **Preserved Fields**: Maintains all original data from each scraper
- **AI Reasoning**: Includes AI analysis when available
- **Summary Stats**: Quick overview of each content type

### **Flexible Integration**
- **Groq API Ready**: Uses existing API configuration
- **Independent Operation**: Runs after scrapers complete
- **Logging Support**: Comprehensive logging for debugging
- **Demo Scripts**: Easy demonstration and testing

## 📈 Recent Results

**Latest aggregation (4/4 sources successful):**

### **🔗 Tech News**
- **Google's Veo 3 AI video generator** - Latest AI video generation breakthrough

### **💼 Internships** 
- **AI/ML Engineer Intern at DraconX** - AI-selected best opportunity

### **💼 Jobs/Placements**
- **Engineer at LSEG** - Entry-level position for fresh graduates

### **📚 Upskill Articles**
- **Anomaly Detection in Python with Isolation Forest** - Practical ML tutorial

## 🛠 Technical Specifications

### **Dependencies**
- Python 3.7+
- `json`, `logging`, `os`, `datetime` (built-in)
- `groq` (for future AI enhancements)

### **File Structure**
```
daily_tech_aggregator.py       # Main aggregator script
demo_daily_digest.py           # Demo and visualization
daily_tech_digest.json         # Output digest file
daily_tech_aggregator.log      # Aggregation logs
```

### **Error Handling**
- **File Not Found**: Logs warning, continues with other sources
- **JSON Parse Error**: Logs error details, marks source as failed
- **Validation Failure**: Flexible validation for different formats
- **Save Errors**: Comprehensive error reporting

## 🎯 Perfect for CS Students

The Daily Tech Digest provides a **complete daily briefing** with:

### **📰 Industry Awareness**
- Latest tech developments and trends
- AI breakthroughs and innovations
- Industry news and analysis

### **🚀 Career Opportunities**
- Curated internship opportunities
- Entry-level job positions
- AI-selected best matches

### **📚 Skill Development**
- Practical tutorials and guides
- Modern technology learning resources
- Hands-on implementation examples

## 🔄 Daily Workflow

### **Morning Routine**
```bash
# 1. Run all scrapers (can be automated)
python demo_tech_news.py
python internship_scraper.py
python jobs_scraper.py  
python demo_upskill.py

# 2. Create unified digest
python daily_tech_aggregator.py

# 3. Review the digest
python demo_daily_digest.py
# or
cat daily_tech_digest.json
```

### **Automation Ready**
The aggregator is designed for easy automation:
- **Cron Jobs**: Schedule daily execution
- **CI/CD Integration**: Include in automated workflows  
- **Monitoring**: Built-in logging for status tracking
- **Error Recovery**: Graceful handling of partial failures

## 🎉 Success Metrics

**Current Performance:**
- ✅ **100% Source Coverage**: All 4 scrapers supported
- ✅ **Flexible Format Support**: Handles different JSON structures
- ✅ **Robust Error Handling**: Continues operation despite failures
- ✅ **Complete Metadata**: Comprehensive tracking and reporting
- ✅ **Easy Integration**: Works with existing scraper ecosystem

The Daily Tech Digest Aggregator provides CS students with a **comprehensive, AI-curated daily briefing** of the most important tech content across news, opportunities, and learning resources! 🎓
