# Quick Start Guide

Get started sending formal emails in 10 minutes.

## 🔑 Authentication Note

**You only need to login ONCE!** After first authentication:
- Your credentials are saved in `token.json`
- Tokens auto-refresh when expired
- No more browser windows or login prompts
- See `AUTHENTICATION.md` for details

---

## 1. Install Dependencies (1 minute)

```bash
# If using the existing venv:
source venv/bin/activate
pip install -r requirements.txt

# Or use the convenience script:
chmod +x run_mailer.sh
./run_mailer.sh  # Handles everything automatically!
```

## 2. Get Google Credentials (3 minutes - ONE TIME SETUP)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use existing)
3. Enable **Gmail API** and **Google Sheets API**
4. Create **OAuth 2.0 Client ID** (Application type: Desktop)
5. Download as `credentials.json`
6. Place in same folder as script

## 3. Prepare Your Sheet (2 minutes)

Create a Google Sheet with these columns for **Certificate**:
```
Name | Email | CourseTitle | CompletionDate | CertificateDriveLink | CertificateID | OrgName | SupportEmail | Year
```

Or these for **Event**:
```
Name | Email | OrgName | EventTitle | EventDate | EventTime | EventTimezone | EventLocation | EventDescription | RSVP_URL | CalendarICSURL | SupportEmail | Year
```

See `SHEET_EXAMPLES.md` for detailed examples.

## 4. Run First Test (4 minutes)

### First Time (Login Required)

```bash
# Option 1: Use the convenience script
./run_mailer.sh

# Option 2: Manual run
source venv/bin/activate
python mailer_dual_template.py
```

**What happens:**
1. Script detects no `token.json`
2. Shows "FIRST-TIME AUTHENTICATION" message
3. Browser opens for Google login
4. You authorize the app
5. `token.json` is created and saved
6. ✅ You're done! Never need to login again!

### Every Run After (No Login!)

```bash
./run_mailer.sh
```

**What happens:**
1. Script finds `token.json`
2. Loads credentials automatically
3. ✅ No browser, no login, just works!

---

### Follow the prompts:

**Sheet ID**: Copy from URL between `/d/` and `/edit`
```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
```

**Range**: Default is fine → press Enter
```
Sheet1!A1:Z1000
```

**Template**: Choose 1 (Certificate) or 2 (Event)

**Column Mapping**: Press Enter to accept suggestions

**Options**:
- Dry-run? → **Y** (always test first!)
- Throttle? → 0.8 (default is fine)
- From address? → blank (press Enter)
- Filter email? → **your@email.com** (test with yourself first)
- Log path? → press Enter
- Subject? → press Enter (use default)

**Preview** → Check sample looks good

**Confirm** → Y

## 5. Review Results

Check the output:
```
[1/1] DRY-RUN your@email.com: Certificate of Completion — Python...
```

Check the log:
```bash
cat send_log.csv
```

## 6. Send for Real

Run again with same settings, but:
- **Dry-run?** → **n** (send for real)
- **Filter email?** → blank (send to all)

Done! 🎉

---

## Running Again Later

### Quick Run

```bash
./run_mailer.sh
```

**That's it!** No login, no setup. The script:
- ✓ Activates venv automatically
- ✓ Uses saved `token.json`
- ✓ Auto-refreshes expired tokens
- ✓ Just works!

### Files You Should Have

After first run, your directory should contain:

```
IEEE/
├── mailer_dual_template.py    # Main script
├── run_mailer.sh               # Convenience launcher
├── requirements.txt            # Dependencies
├── credentials.json            # OAuth credentials (manual download)
├── token.json                  # Auth token (auto-created) ⭐
├── send_log.csv               # Email history (auto-created)
├── README.md                   # Full docs
├── AUTHENTICATION.md           # Auth guide
└── venv/                       # Python virtual environment
```

**Important:** Keep `token.json` - it's your saved login!

### What If I Delete token.json?

No problem! Just run the script again:
1. Browser will open once
2. Login again
3. New `token.json` is created
4. Back to normal - no more logins needed

## Common Issues

### "credentials.json not found"
Place the downloaded OAuth file in the script directory.

### "No data found in sheet"
Check your Sheet ID and range are correct.

### "Missing required field"
Verify all required columns have data (see SHEET_EXAMPLES.md).

### "Invalid email format"
Check for typos or extra spaces in email column.

## Next Steps

- Read `README.md` for full documentation
- See `SHEET_EXAMPLES.md` for detailed sheet structures
- Customize subject lines with placeholders
- Add optional fields for richer content

## Need Help?

Check these resources:
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Sheets API Docs](https://developers.google.com/sheets/api)
- Review `README.md` troubleshooting section

