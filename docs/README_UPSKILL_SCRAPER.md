# 🎓 Upskill Articles Scraper for CS Students

A comprehensive web scraper designed to help computer science engineering students discover valuable learning resources, tutorials, and technical content from top-tier educational and industry sources.

## 🎯 Purpose

This scraper finds educational content that helps CS students:
- Learn new technologies and frameworks
- Discover best practices and implementation guides
- Access hands-on tutorials and project examples
- Stay updated with industry trends and tools
- Build portfolio-worthy skills

## 📚 Sources Covered

### **Company Engineering Blogs** (12 sources)
- GitHub Engineering Blog
- Microsoft DevBlogs
- Netflix Tech Blog
- Google Technology Blog
- AWS Blog
- Stack Overflow Blog
- JetBrains Blog
- Docker Blog
- Kubernetes Blog
- Meta Engineering
- LinkedIn Engineering
- Twitter Engineering

### **Tech Education Sites** (6 sources)
- FreeCodeCamp
- CSS-Tricks
- Smashing Magazine
- HackerNoon
- DigitalOcean Community Tutorials
- Codecademy Blog

### **The New Stack** (9 specialized categories)
- WebAssembly
- Software Development
- Security
- LLM/AI
- Frontend Development
- Data
- Backend Development
- API Management
- AI

### **Additional Tech Sites**
- Dev.to (Tutorial section)
- KDnuggets (Data Science & ML)
- Medium (Programming tags)
- XDA Developers

**Total: 30+ URLs across 7 categories**

## 🔍 Smart Filtering

### **Date Filtering**
- **7-day window** for broader educational content discovery
- Lenient handling of missing dates (assumes recent)
- Site-specific date parsing for accuracy

### **Content Filtering**
**Include Keywords:**
- Tutorial, guide, how-to, step-by-step
- Best practices, tips, optimization
- Implementation, project, hands-on
- Framework, library, tool, stack
- Popular technologies (Python, React, AI/ML, Docker, etc.)

**Exclude Keywords:**
- Business news, funding, acquisitions
- Opinion pieces, editorials
- Outdated/deprecated content
- Non-technical content

### **AI-Powered Selection**
Uses Groq API to select the most valuable learning article based on:
1. **Practical Learning Value** - Tutorials and implementation guides
2. **Technology Relevance** - Modern, in-demand technologies
3. **Skill Building** - Concrete, applicable skills
4. **Career Impact** - Portfolio-worthy skills

## 🚀 Quick Start

### **Basic Usage**
```bash
# Run the demo
python demo_upskill.py

# Run just the scraper
python -c "from upskill_scraper import upskill_articles; articles = upskill_articles(); print(f'Found {len(articles)} articles')"
```

### **Output Files**
- `upskill_articles.json` - All scraped articles
- `ai_selected_upskill_article.json` - AI-selected best article
- `upskill_scraper.log` - Detailed logging

## 🔧 Easy URL Management

### **Configuration File**
All URLs are stored in `upskill_urls_config.json` for easy management:

```json
{
  "tech_education": [
    "https://www.freecodecamp.org/news/",
    "https://css-tricks.com/"
  ],
  "thenewstack": [
    "https://thenewstack.io/ai/",
    "https://thenewstack.io/security/"
  ]
}
```

### **Adding New URLs**

**Method 1: Edit JSON file directly**
```json
{
  "tech_education": [
    "https://existing-url.com",
    "https://new-url.com"  // Add here
  ]
}
```

**Method 2: Use the management script**
```bash
python manage_upskill_urls.py
```

**Method 3: Programmatically**
```python
from upskill_scraper import add_url_to_config

# Add a new URL to existing category
add_url_to_config("tech_education", "https://new-site.com")

# The scraper will automatically use the new URL
```

### **URL Categories**
- `dev_to` - Dev.to tutorial sections
- `kdnuggets` - Data science and ML content
- `medium` - Programming and tech tags
- `company_blogs` - Engineering blogs from major companies
- `tech_education` - Educational tech sites and tutorials
- `thenewstack` - The New Stack's specialized categories
- `additional_tech` - XDA Developers and other tech sites

## 📊 Recent Results

**Latest scraping session found:**
- **28 relevant upskill articles**
- **Company Blogs**: 15 articles (Visual Studio, Azure, DevOps, AI)
- **Tech Education**: 9 articles (Python ML, Web Design, MySQL)
- **The New Stack**: 2 articles (WebAssembly, ML Frameworks)
- **XDA Developers**: 1 article (PC Building Experience)

**Sample Articles:**
- "How to Build AI Agents with Ruby" (DigitalOcean)
- "Circuit Breaker Policy Fine-tuning Best Practice" (Microsoft)
- "WebAssembly is very suitable for serverless environments" (The New Stack)
- "Anomaly Detection in Python with Isolation Forest" (DigitalOcean)

## 🛠 Technical Features

- **Robust error handling** with retry logic
- **Site-specific parsing** for better accuracy
- **Duplicate removal** based on URLs
- **Comprehensive logging** for debugging
- **Clean JSON output** with title and URL
- **Configurable URL management**
- **AI-powered content curation**

## 📁 File Structure

```
upskill_scraper.py              # Main scraper with all functionality
demo_upskill.py                 # Demonstration script
manage_upskill_urls.py          # Interactive URL management
demo_url_management.py          # URL management demonstration
upskill_urls_config.json        # URL configuration file
upskill_articles.json           # Scraped articles output
ai_selected_upskill_article.json # AI-selected best article
upskill_scraper.log            # Detailed logs
```

## 🎯 Perfect for CS Students

This scraper is specifically designed for computer science students who want to:
- **Stay current** with technology trends
- **Learn practical skills** through tutorials
- **Discover new tools** and frameworks
- **Access quality content** from industry experts
- **Build technical knowledge** systematically

## 🔄 Daily Usage

Run daily to discover fresh learning content:
```bash
# Morning routine - get today's learning resources
python demo_upskill.py

# Check the AI-selected article for focused learning
cat ai_selected_upskill_article.json
```

The scraper is ready to help CS students discover valuable learning resources every day! 🎓
