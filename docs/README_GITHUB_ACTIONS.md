# 🤖 GitHub Actions Automation for TJI Pipeline

## Overview

The TJI automation project now includes comprehensive GitHub Actions workflows that automatically run the daily tech digest pipeline in the cloud. This eliminates the need for local execution and provides reliable, scheduled automation.

## 🔄 Workflow Architecture

### **Main Workflow: `daily-tji-pipeline.yml`**
- **Schedule**: Daily at 2:30 PM UTC (14:30)
- **Trigger**: Automatic (cron) + Manual
- **Duration**: ~15-20 minutes
- **Environment**: Ubuntu Latest + Python 3.9

### **Test Workflow: `test-tji-setup.yml`**
- **Schedule**: Manual trigger only
- **Purpose**: Validate setup and configuration
- **Duration**: ~5 minutes
- **Components**: Environment, Config, Scrapers, Messaging

## 📊 Pipeline Flow in GitHub Actions

```
🚀 Checkout → 🐍 Python Setup → 📦 Dependencies → 🔍 Validation
    ↓
📁 Data Restore → 🧹 Initialize → 📰 Tech News → 💼 Internships
    ↓
🏢 Jobs → 📚 Upskill → 🔄 Aggregator → 🔗 URL Shortener
    ↓
✍️ Message Drafter → 📱 WhatsApp Sender → 📊 Summary → 💾 Artifacts
```

## 🔧 Key Features

### **1. Environment Management**
- **Secrets Integration**: Secure API key management
- **Path Resolution**: Automatic file path handling
- **Configuration Detection**: GitHub Actions vs local environment

### **2. Data Persistence**
- **Caching Strategy**: Preserves deduplication history across runs
- **Artifact Storage**: Saves output files for 7 days
- **State Management**: Maintains counters and seen items

### **3. Error Handling**
- **Continue on Error**: Individual step failures don't stop pipeline
- **Fallback Creation**: Empty files created for missing content
- **Critical Component Detection**: Fails workflow if aggregator/drafter fails

### **4. Monitoring & Logging**
- **Detailed Logs**: Comprehensive execution logging
- **Status Reporting**: Success/failure summary for each component
- **Artifact Downloads**: Access to all generated files

## 🔑 Security & Configuration

### **GitHub Secrets Required**
```
GROQ_API_KEY          # AI content selection
TINYURL_API_KEY       # URL shortening
TWILIO_ACCOUNT_SID    # WhatsApp messaging
TWILIO_AUTH_TOKEN     # WhatsApp authentication
TWILIO_PHONE_FROM     # Twilio WhatsApp number
TWILIO_PHONE_TO       # Recipient WhatsApp number
```

### **Configuration Updates**
- **Environment Detection**: Automatic GitHub Actions detection
- **Path Management**: Dynamic path resolution for different environments
- **API Integration**: Environment variable priority over local config

## 📱 WhatsApp Integration

### **Message Format Compatibility**
- **Line Breaks**: Proper `\n` handling for WhatsApp
- **Special Characters**: Bold formatting with `*text*`
- **URL Placement**: URLs on separate lines for better readability
- **Character Limits**: Automatic message length validation

### **Delivery Verification**
- **Twilio Status**: Message SID and delivery status logging
- **Error Handling**: Detailed error messages for troubleshooting
- **Fallback Options**: Graceful degradation if messaging fails

## 🧪 Testing & Validation

### **Pre-deployment Testing**
```bash
# Run the test workflow manually
GitHub → Actions → Test TJI Setup → Run workflow
```

### **Component Testing Options**
- **All**: Complete system validation
- **Environment**: Directory structure and dependencies
- **Config**: API keys and configuration loading
- **Scrapers**: Import and basic functionality
- **Messaging**: Twilio setup and message formatting

### **Local Testing**
```bash
# Test with GitHub Actions environment simulation
export TJI_ENVIRONMENT=github_actions
export GROQ_API_KEY=your_key
export TWILIO_ACCOUNT_SID=your_sid
# ... other environment variables
python processors/run_daily_digest_pipeline.py
```

## 📈 Monitoring & Maintenance

### **Workflow Monitoring**
- **GitHub Actions Tab**: Real-time execution monitoring
- **Email Notifications**: Automatic failure notifications
- **Logs Access**: Detailed step-by-step execution logs

### **Performance Metrics**
- **Execution Time**: Typical 15-20 minute runtime
- **Success Rate**: Track component success/failure rates
- **Resource Usage**: Monitor GitHub Actions minutes consumption

### **Maintenance Tasks**
- **Dependency Updates**: Regular `requirements.txt` updates
- **API Key Rotation**: Periodic secret updates
- **Quota Monitoring**: Track API usage limits

## 🔄 Customization Options

### **Schedule Modification**
```yaml
# Edit .github/workflows/daily-tji-pipeline.yml
schedule:
  - cron: '30 14 * * *'  # Current: 2:30 PM UTC daily
  - cron: '0 9 * * 1-5'  # Example: 9 AM UTC, weekdays only
```

### **Component Selection**
```yaml
# Disable specific scrapers by commenting out steps
# - name: 💼 Internship Scraper
#   run: echo "Skipped"
```

### **Timeout Adjustments**
```yaml
# Modify individual step timeouts
timeout-minutes: 30  # Overall job timeout
```

## 🚨 Troubleshooting

### **Common Issues**

**1. Workflow Not Triggering**
- Check repository Actions are enabled
- Verify cron syntax is correct
- Ensure workflow file is in `.github/workflows/`

**2. Secret Access Errors**
- Verify all required secrets are configured
- Check secret names match exactly (case-sensitive)
- Ensure repository has access to organization secrets (if applicable)

**3. Scraper Failures**
- Check website accessibility from GitHub Actions
- Verify rate limiting isn't blocking requests
- Review timeout settings for slow websites

**4. Twilio/WhatsApp Issues**
- Verify WhatsApp number is verified in Twilio console
- Check account balance and messaging limits
- Ensure phone numbers include proper country codes

### **Debug Strategies**

**1. Enable Debug Mode**
```yaml
# Manual workflow trigger with debug option
workflow_dispatch:
  inputs:
    debug_mode: true
```

**2. Download Artifacts**
- Access generated JSON files from workflow runs
- Review logs and output for debugging

**3. Test Individual Components**
```bash
# Run test workflow for specific components
GitHub → Actions → Test TJI Setup → Run workflow → Select component
```

## 📊 Expected Outputs

### **Successful Run Artifacts**
```
data/
├── ai_selected_article.json         # Tech news selection
├── selected_internship.json         # Best internship
├── selected_job.json               # Best job posting
├── ai_selected_upskill_article.json # Learning resource
├── daily_tech_digest.json          # Consolidated digest
├── shortened_urls_digest.json      # URLs with TinyURL aliases
├── tji_daily_message.json          # Formatted WhatsApp message
└── *.log                           # Execution logs
```

### **WhatsApp Message Delivery**
- Professional formatted message with TJI branding
- Shortened URLs with custom aliases
- AI-generated pro tips for engineering students
- Clean structure with proper line breaks

## 🎯 Benefits of GitHub Actions Automation

### **Reliability**
- **Cloud Infrastructure**: No dependency on local machines
- **Consistent Environment**: Same setup every execution
- **Automatic Recovery**: Built-in retry mechanisms

### **Scalability**
- **Parallel Execution**: Multiple workflow runs if needed
- **Resource Management**: Automatic scaling and cleanup
- **Global Availability**: Runs from GitHub's global infrastructure

### **Maintenance**
- **Automated Updates**: Dependency and security updates
- **Monitoring Integration**: Built-in logging and alerting
- **Version Control**: All changes tracked in Git

### **Cost Efficiency**
- **Free Tier**: 2000 minutes/month for public repositories
- **Pay-as-you-go**: Only pay for actual usage
- **No Infrastructure**: No server maintenance required

The GitHub Actions integration transforms the TJI automation from a local script into a professional, cloud-based automation system with enterprise-grade reliability and monitoring capabilities.
