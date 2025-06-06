# TJI Automation Project

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

## 🚀 Quick Start

### Automated Setup (Recommended)
```bash
# Run the setup script to configure everything automatically
python setup.py
```

### Manual Setup
1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   ```bash
   cp config/api_config_template.json config/api_config.json
   # Edit config/api_config.json with your API keys
   ```

3. **Run Complete Pipeline**
   ```bash
   python processors/run_daily_digest_pipeline.py
   ```

## Documentation

See the `docs/` directory for detailed documentation on each component.

## ✨ Features

- 🔍 **Web Scraping**: Tech news, internships, jobs, upskill articles
- 🤖 **AI Curation**: Intelligent content selection using Groq API
- 🔗 **URL Shortening**: TinyURL integration with custom aliases
- ✍️ **Message Drafting**: AI-powered professional message formatting
- 📱 **WhatsApp Delivery**: Automated message sending via Twilio
- 🧹 **Smart Cleanup**: Automatic file management with deduplication
- 🛡️ **Robust Pipeline**: Error handling and fallback mechanisms
- 🤖 **GitHub Actions**: Automated daily execution in the cloud

## 🤖 GitHub Actions Automation

The TJI pipeline includes comprehensive GitHub Actions workflows for automated daily execution:

### **Daily Automation**
- **Schedule**: Runs automatically daily at 2:30 PM UTC
- **Cloud Execution**: No local machine required
- **WhatsApp Delivery**: Automated message sending
- **Error Handling**: Robust failure recovery

### **Quick Setup**
1. **Configure Secrets**: Add API keys to GitHub repository secrets
2. **Push to GitHub**: Upload your code to a GitHub repository
3. **Automatic Execution**: Pipeline runs daily without intervention

### **Manual Testing**
- Test workflow available for validation
- Manual trigger option for immediate execution
- Component-specific testing capabilities

📖 **Complete Setup Guide**: [docs/GITHUB_ACTIONS_SETUP.md](docs/GITHUB_ACTIONS_SETUP.md)

## License

MIT License - see LICENSE file for details.
