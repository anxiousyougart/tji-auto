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
