# 🚀 GitHub Actions Setup Guide for TJI Automation

This guide explains how to set up the TJI automation pipeline to run automatically on GitHub Actions daily at 2:30 PM UTC.

## 📋 Prerequisites

1. **GitHub Repository**: Your TJI project uploaded to GitHub
2. **API Keys**: Valid API keys for all services
3. **Twilio Account**: Configured WhatsApp sandbox or business account

## 🔧 Step 1: Repository Secrets Configuration

Navigate to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

### **Required API Keys**

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `GROQ_API_KEY` | Groq API key for AI content selection | `gsk_...` |
| `TINYURL_API_KEY` | TinyURL API key for URL shortening | `Rmg2VwW1...` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | `AC...` |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | `a48df...` |
| `TWILIO_PHONE_FROM` | Twilio WhatsApp number | `whatsapp:+14155238886` |
| `TWILIO_PHONE_TO` | Your WhatsApp number | `whatsapp:+1234567890` |

### **How to Add Secrets**

1. Go to your repository on GitHub
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Enter the secret name and value
6. Click **Add secret**

## 🔑 Step 2: Obtain API Keys

### **Groq API Key**
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up/login to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_`)

### **TinyURL API Key**
1. Visit [TinyURL API](https://tinyurl.com/app/dev)
2. Sign up for a developer account
3. Generate an API key
4. Copy the API key

### **Twilio Configuration**
1. Visit [Twilio Console](https://console.twilio.com/)
2. Sign up/login to your account
3. Get your Account SID and Auth Token from the dashboard
4. Set up WhatsApp sandbox or business account
5. Note your Twilio WhatsApp number and verify your recipient number

## 📅 Step 3: Workflow Schedule

The workflow is configured to run daily at **2:30 PM UTC (14:30)**. 

To change the schedule, edit `.github/workflows/daily-tji-pipeline.yml`:

```yaml
schedule:
  - cron: '30 14 * * *'  # 2:30 PM UTC daily
```

### **Common Schedule Examples**
- `'0 9 * * *'` - 9:00 AM UTC daily
- `'30 18 * * 1-5'` - 6:30 PM UTC, Monday to Friday
- `'0 12 * * 0'` - 12:00 PM UTC, Sundays only

## 🧪 Step 4: Test the Workflow

### **Manual Trigger**
1. Go to your repository → Actions tab
2. Click on "Daily TJI Tech Digest Pipeline"
3. Click "Run workflow" button
4. Optionally enable debug mode
5. Click "Run workflow"

### **Monitor Execution**
1. Watch the workflow run in real-time
2. Check each step's logs for issues
3. Verify output artifacts are created
4. Confirm WhatsApp message is received

## 📊 Step 5: Workflow Components

The workflow executes these steps in sequence:

1. **🚀 Checkout Repository** - Downloads your code
2. **🐍 Set up Python** - Installs Python 3.9
3. **📦 Install Dependencies** - Installs required packages
4. **🔍 Validate Environment** - Checks directory structure
5. **📁 Restore Persistent Data** - Loads deduplication history
6. **🧹 Initialize Data Directory** - Prepares data files
7. **📰 Tech News Scraper** - Scrapes tech news
8. **💼 Internship Scraper** - Scrapes internships
9. **🏢 Jobs Scraper** - Scrapes job postings
10. **📚 Upskill Articles Scraper** - Scrapes learning resources
11. **🔄 Daily Digest Aggregator** - Combines all content
12. **🔗 TinyURL Shortener** - Creates shortened URLs
13. **✍️ Message Drafter** - Formats WhatsApp message
14. **📱 WhatsApp Sender** - Sends message via Twilio
15. **📊 Pipeline Summary** - Reports execution status
16. **💾 Save Pipeline Artifacts** - Stores output files
17. **🔄 Cache Persistent Data** - Saves deduplication data

## 🛡️ Step 6: Error Handling

### **Continue on Error**
- Individual steps can fail without stopping the pipeline
- Critical components (aggregator, message drafter) will fail the workflow
- Non-critical failures are logged but don't stop execution

### **Fallback Behavior**
- Empty output files are created if scrapers find no content
- Persistent data is preserved across runs
- Detailed logging helps with debugging

## 📱 Step 7: WhatsApp Message Format

The automated message follows this structure:

```
*#TJI 376*

*TECH NEWS:*

Google boosts coding power with Gemini 2.5 Pro AI model
Read more at:
https://tinyurl.com/tech-news-tji-376

*INTERNSHIP UPDATE:*

Join Accio Robotics as a Deployment Engineer Intern in Hyderabad
Apply now at:
https://tinyurl.com/internship-tji-376

*PLACEMENT UPDATE:*

Secure a Cybersecurity Analyst role at Prudent Technologies
Apply now at:
https://tinyurl.com/placement-update-tji-376

*PRO TIP:*

Review 3 examples, 3 pieces of code, or 3 concepts at a time to solidify understanding.

*UPSKILL:*

Agentic DevOps in action: Reimagining every phase of the developer lifecycle
https://tinyurl.com/upskill-tji-376
```

## 🔧 Step 8: Troubleshooting

### **Common Issues**

**1. Workflow Not Running**
- Check if secrets are properly configured
- Verify cron schedule syntax
- Ensure repository has Actions enabled

**2. API Key Errors**
- Verify all required secrets are added
- Check API key validity and quotas
- Ensure secret names match exactly

**3. Twilio Errors**
- Verify WhatsApp number is verified in Twilio
- Check account balance and limits
- Ensure phone numbers include country code

**4. Scraper Failures**
- Check internet connectivity in GitHub Actions
- Verify website accessibility
- Review rate limiting and timeouts

### **Debug Mode**
Enable debug mode when manually triggering the workflow for detailed logging.

### **Logs and Artifacts**
- Check workflow logs for detailed error messages
- Download artifacts to inspect output files
- Review persistent data for deduplication issues

## 📈 Step 9: Monitoring and Maintenance

### **Regular Checks**
- Monitor workflow success rate
- Check WhatsApp message delivery
- Review API usage and quotas
- Update dependencies periodically

### **Notifications**
- GitHub will email you on workflow failures
- Set up additional monitoring if needed
- Consider Slack/Discord webhooks for alerts

## 🎯 Step 10: Success Verification

After setup, verify:

- ✅ Workflow runs daily at scheduled time
- ✅ All scrapers execute successfully
- ✅ Content is aggregated and processed
- ✅ URLs are shortened with custom aliases
- ✅ WhatsApp message is formatted correctly
- ✅ Message is delivered to your phone
- ✅ Persistent data is maintained across runs

## 🔄 Step 11: Customization

### **Modify Schedule**
Edit the cron expression in the workflow file

### **Add/Remove Scrapers**
Update the workflow steps and configuration

### **Change Message Format**
Modify the message drafter script

### **Add Notifications**
Integrate additional messaging services

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review workflow logs in GitHub Actions
3. Verify all secrets are correctly configured
4. Test individual components locally first

The GitHub Actions automation provides a robust, scalable solution for daily TJI content delivery with comprehensive error handling and monitoring capabilities.
