# 🚀 Master Scraper - Daily Tech Digest Pipeline

**One command to rule them all!** The master orchestrator script that executes all four web scrapers in sequence and aggregates their results into a single unified JSON output file.

## 🎯 Overview

The Master Scraper is a comprehensive orchestration system that:
- Executes all four specialized web scrapers sequentially
- Handles failures gracefully and continues execution
- Aggregates results into a unified `daily_tech_digest.json`
- Provides detailed progress tracking and error reporting
- Supports automation and daily scheduling

## 🔧 Quick Start

### **Single Command Execution**
```bash
# Run everything with one command
python master_scraper.py

# Alternative (same functionality)
python run_daily_digest_pipeline.py
```

### **View Results**
```bash
# Interactive demo of results
python demo_daily_digest.py

# View raw JSON
cat daily_tech_digest.json

# Pretty print JSON
python -m json.tool daily_tech_digest.json
```

## 📊 What It Does

### **Sequential Scraper Execution:**

1. **🔬 Tech News Scraper** (`demo_tech_news.py`)
   - Scrapes 16+ major tech news sources
   - 48-hour date filtering for recent content
   - AI-powered selection of most important article
   - Output: `ai_selected_article.json`

2. **💼 Internship Scraper** (`internship_scraper.py`)
   - Targets Internshala and LinkedIn
   - Filters for CS/IT/Engineering branches
   - 48-hour date filtering for relevance
   - Output: `selected_internship.json`

3. **🏢 Job Scraper** (`jobs_scraper.py`)
   - Entry-level positions (0-1 years experience)
   - Excludes trainee/internship positions
   - 24-hour strict date filtering
   - Output: `selected_job.json`

4. **📚 Upskill Article Scraper** (`demo_upskill.py`)
   - 33+ educational tech sources
   - Tutorials, best practices, tech stacks
   - AI-powered selection for learning value
   - Output: `ai_selected_upskill_article.json`

5. **🔄 Aggregator** (`daily_tech_aggregator.py`)
   - Consolidates all AI-selected content
   - Clean, simplified JSON format
   - Metadata and summary statistics
   - Output: `daily_tech_digest.json`

## 🛡️ Error Handling

### **Graceful Failure Management:**
- **Individual Scraper Failures**: Pipeline continues even if one scraper fails
- **Timeout Protection**: Each scraper has configurable timeout limits
- **Missing Content**: Shows "No suitable content found" instead of crashing
- **Network Issues**: Handles connection problems gracefully
- **Comprehensive Logging**: Detailed logs in `daily_digest_pipeline.log`

### **Success Criteria:**
- ✅ **Full Success**: All 4 scrapers find content
- ✅ **Partial Success**: At least 1 scraper finds content
- ⚠️ **No Content**: All scrapers run but find nothing
- ❌ **Pipeline Failure**: Aggregator fails to run

## 📁 Output Structure

### **Final Output: `daily_tech_digest.json`**
```json
{
  "daily_tech_digest": {
    "metadata": {
      "generated_at": "2025-01-25T10:30:00",
      "successful_sources": "4/4",
      "source_files": {
        "tech_news": "ai_selected_article.json",
        "internships": "selected_internship.json",
        "jobs": "selected_job.json", 
        "upskill_articles": "ai_selected_upskill_article.json"
      }
    },
    "summary": {
      "tech_news": {"count": 1, "status": "success"},
      "internships": {"count": 1, "status": "success"},
      "jobs": {"count": 1, "status": "success"},
      "upskill_articles": {"count": 1, "status": "success"}
    },
    "content": {
      "tech_news": {"title": "...", "url": "..."},
      "internships": {"title": "...", "company": "...", "url": "..."},
      "jobs": {"title": "...", "company": "...", "url": "..."},
      "upskill_articles": {"title": "...", "url": "..."}
    }
  }
}
```

## ⚙️ Configuration

### **Timeout Settings:**
- Tech News Scraper: 5 minutes
- Internship Scraper: 10 minutes  
- Job Scraper: 10 minutes
- Upskill Scraper: 5 minutes
- Aggregator: 1 minute

### **Customization:**
Edit `run_daily_digest_pipeline.py` to modify:
- Timeout values
- Scraper order
- Output file names
- Logging configuration

## 🔄 Automation

### **Daily Scheduling:**
```bash
# Cron job (Linux/Mac)
0 9 * * * cd /path/to/project && python master_scraper.py

# Windows Task Scheduler
# Schedule: python master_scraper.py
# Working Directory: C:\path\to\project
```

### **CI/CD Integration:**
```yaml
# GitHub Actions example
- name: Run Daily Tech Digest
  run: python master_scraper.py
  working-directory: ./tji-auto
```

## 📋 Monitoring & Logs

### **Console Output:**
- Real-time progress tracking
- Success/failure status for each scraper
- Execution time for each step
- Final summary with file locations

### **Log Files:**
- `daily_digest_pipeline.log` - Complete pipeline execution log
- Individual scraper logs (if enabled)

## 🎉 Success Metrics

### **Typical Results:**
- **Execution Time**: 15-30 minutes total
- **Success Rate**: 80-95% (3-4 out of 4 scrapers)
- **Content Quality**: AI-selected best articles/opportunities
- **File Size**: 2-10KB final digest

### **What Success Looks Like:**
```
🎉 PIPELINE COMPLETED SUCCESSFULLY!
All scrapers found content. Daily digest available in: daily_tech_digest.json

📁 OUTPUT FILES:
  ✅ ai_selected_article.json
  ✅ selected_internship.json  
  ✅ selected_job.json
  ✅ ai_selected_upskill_article.json
  ✅ daily_tech_digest.json
```

## 🚨 Troubleshooting

### **Common Issues:**
1. **Network Timeouts**: Increase timeout values in configuration
2. **API Rate Limits**: Add delays between scraper executions
3. **Missing Dependencies**: Run `pip install -r requirements.txt`
4. **Permission Errors**: Check file write permissions

### **Debug Commands:**
```bash
# Check individual scrapers
python demo_tech_news.py
python internship_scraper.py
python jobs_scraper.py
python demo_upskill.py

# Test aggregator only
python daily_tech_aggregator.py

# View detailed logs
cat daily_digest_pipeline.log
```

## 🎯 Perfect For

- **Daily Tech Monitoring**: Stay updated with latest developments
- **Job/Internship Hunting**: Fresh opportunities for CS students
- **Skill Development**: Curated learning resources
- **Automation**: Set-and-forget daily digest generation
- **Research**: Comprehensive tech landscape overview

---

**Ready to get started?** Run `python demo_master_scraper.py` to see what's available, then `python master_scraper.py` to generate fresh content!
