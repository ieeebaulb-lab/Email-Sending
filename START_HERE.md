# 📧 Formal Email Mailer - START HERE

Welcome! This is a professional email automation tool for sending certificates and event invitations via Gmail.

## 🚀 Quick Start (First Time Users)

### 1️⃣ Easiest Way

```bash
./run_mailer.sh
```

That's it! The script handles everything:
- ✅ Activates Python environment
- ✅ Checks dependencies
- ✅ Guides you through first-time login
- ✅ Saves credentials (no more logins!)
- ✅ Runs the mailer

### 2️⃣ What You Need

Before running, make sure you have:

1. **credentials.json** (Download once from Google Cloud Console)
   - See `QUICKSTART.md` step 2 for instructions
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **A Google Sheet** with your recipient data
   - See `SHEET_EXAMPLES.md` for structure

That's all! Everything else is automatic.

---

## 🔑 Important: You Only Login Once!

**After your first run:**
- ✅ `token.json` is created with your credentials
- ✅ Future runs require NO login
- ✅ Tokens auto-refresh when expired
- ✅ No browser windows, just works!

**If you're being asked to login every time, something is wrong.**
→ See `AUTHENTICATION.md` or `HOW_AUTHENTICATION_WORKS.md`

---

## 📚 Documentation Guide

Choose your path:

### 🏃 I want to start immediately
→ Read: `QUICKSTART.md` (10 minute setup)

### 🔍 I want to understand everything
→ Read: `README.md` (complete documentation)

### ❓ I'm having authentication issues
→ Read: `AUTHENTICATION.md` (detailed auth guide)
→ Or: `HOW_AUTHENTICATION_WORKS.md` (visual flowcharts)

### 📊 I need help with my Google Sheet
→ Read: `SHEET_EXAMPLES.md` (column structures & examples)

### 🔧 Something's not working
→ Check `README.md` → Troubleshooting section
→ Or `AUTHENTICATION.md` → Troubleshooting section

---

## 📁 File Overview

### Core Files
- `mailer_dual_template.py` - Main script
- `run_mailer.sh` - Convenience launcher (use this!)
- `requirements.txt` - Python dependencies

### Credentials (You Manage These)
- `credentials.json` - OAuth credentials (download from Google)
- `token.json` - Auto-created after first login ⭐

### Documentation
- `START_HERE.md` - This file
- `QUICKSTART.md` - Fast setup guide
- `README.md` - Complete documentation
- `AUTHENTICATION.md` - Auth guide
- `HOW_AUTHENTICATION_WORKS.md` - Visual auth explanation
- `SHEET_EXAMPLES.md` - Google Sheet structure examples

### Auto-Generated
- `send_log.csv` - Email send history (created on first run)

---

## ⚡ Common Commands

### First time setup
```bash
chmod +x run_mailer.sh
./run_mailer.sh
```

### Every subsequent run
```bash
./run_mailer.sh
```

### View send history
```bash
cat send_log.csv
```

### Re-authenticate (if needed)
```bash
rm token.json
./run_mailer.sh
```

---

## 🎯 What This Tool Does

### Two Professional Email Templates

1. **Certificate Delivery**
   - Send course completion certificates
   - With Google Drive links
   - Professional formatting
   - Verification details

2. **Event Invitation**
   - Send formal event invitations
   - With RSVP and calendar links
   - Speaker information
   - Rich descriptions

### Key Features

- ✅ Read recipients from Google Sheets
- ✅ Interactive template selection
- ✅ Dry-run mode (preview before sending)
- ✅ Email validation
- ✅ CSV logging (audit trail)
- ✅ Throttling (avoid rate limits)
- ✅ One-time authentication
- ✅ Beautiful HTML emails

---

## 🔐 Security Notes

### Keep These Files Private
- `credentials.json` - OAuth client credentials
- `token.json` - Your access token

Both are in `.gitignore` automatically.

### What token.json Can Do
- Read your Google Sheets
- Send emails from your Gmail
- That's it! (limited scope)

### Protect Your Token
```bash
chmod 600 token.json credentials.json
```

See `AUTHENTICATION.md` for security best practices.

---

## 🆘 Getting Help

### "credentials.json not found"
→ Download from Google Cloud Console
→ See `QUICKSTART.md` step 2

### "Need to login every time"
→ Check if `token.json` exists: `ls -la token.json`
→ See `HOW_AUTHENTICATION_WORKS.md`

### "Missing required field"
→ Check your Google Sheet structure
→ See `SHEET_EXAMPLES.md`

### "Invalid email format"
→ Check for typos in Email column
→ Script validates email addresses

### Other Issues
→ See `README.md` → Troubleshooting section

---

## 💡 Tips for Success

1. **Always test with dry-run first**
   - Choose "Y" when asked about dry-run
   - Preview emails before sending

2. **Start small**
   - Filter to your own email first
   - Verify everything looks correct
   - Then send to full list

3. **Keep logs**
   - Review `send_log.csv` after each run
   - Track who received emails
   - Check for failures

4. **Use throttling**
   - Default 0.8 seconds between sends
   - Prevents Gmail rate limiting
   - Adjust as needed

5. **Validate your sheet**
   - All required fields filled
   - Email addresses correct
   - Links working and shareable

---

## 🎓 Example Workflow

```bash
# Day 1: Setup
./run_mailer.sh              # First run - browser opens, you login
# → token.json created
# → Send test emails in dry-run mode

# Day 2: Send certificates
./run_mailer.sh              # No login needed!
# → Choose Certificate template
# → Send to full list

# Day 7: Send event invites
./run_mailer.sh              # Still no login!
# → Choose Event template
# → Send to attendees

# Day 30: More certificates
./run_mailer.sh              # You get the idea!
# → No login, just works
```

---

## 📞 Next Steps

### Ready to start?

```bash
./run_mailer.sh
```

### Need more info first?

Read `QUICKSTART.md` for step-by-step setup.

### Want to understand the system?

Read `README.md` for complete documentation.

---

## ✨ That's It!

You're ready to send professional, formal emails at scale.

**Remember:** You only login once, then it just works! 🎉

---

**Quick Links**
- Google Cloud Console: https://console.cloud.google.com/apis/credentials
- Check Authorized Apps: https://myaccount.google.com/permissions
- Gmail API Docs: https://developers.google.com/gmail/api
- Sheets API Docs: https://developers.google.com/sheets/api

