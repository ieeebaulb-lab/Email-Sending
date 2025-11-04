# How Authentication Works - Visual Guide

## 🎯 The Key Point

**You login ONCE. That's it. Forever.**

---

## First Run Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. You run: ./run_mailer.sh                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Script checks: Does token.json exist?                       │
│     Answer: NO (first time)                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Script shows:                                               │
│     "FIRST-TIME AUTHENTICATION"                                 │
│     "Browser will open - login once, then never again"          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Browser opens → Google login screen                         │
│     - Enter your email/password                                 │
│     - Click "Allow" to grant permissions                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Browser shows "Success!" - close it                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Script creates token.json with:                             │
│     - Access token (expires in 1 hour)                          │
│     - Refresh token (NEVER expires)                             │
│     ⭐ THIS FILE IS YOUR SAVED LOGIN ⭐                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. Script continues with email sending...                      │
│     ✓ You're now authenticated!                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Result:** `token.json` now exists on your computer

---

## Second Run Flow (And Forever After)

```
┌─────────────────────────────────────────────────────────────────┐
│  1. You run: ./run_mailer.sh                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Script checks: Does token.json exist?                       │
│     Answer: YES! ✓                                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Script shows:                                               │
│     "✓ Found existing token.json"                               │
│     "✓ No login required!"                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Script loads token.json                                     │
│     - Checks if access token is still valid                     │
│     - If expired, uses refresh token to get new access token    │
│     - ALL AUTOMATIC, NO USER ACTION NEEDED                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Script continues with email sending...                      │
│     ✓ You're authenticated!                                     │
│     ❌ NO browser opened                                        │
│     ❌ NO login prompt                                          │
└─────────────────────────────────────────────────────────────────┘
```

**Result:** Script just works, no interaction needed!

---

## Token Lifecycle

### What's Inside token.json?

```json
{
  "token": "ya29.a0Aa4x...",           // Access token (expires in 1 hour)
  "refresh_token": "1//0gH...",        // Refresh token (never expires)
  "token_uri": "https://oauth2...",
  "client_id": "123456...",
  "client_secret": "GOCSPX...",
  "scopes": [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/gmail.send"
  ],
  "expiry": "2025-11-03T14:30:00Z"     // When access token expires
}
```

### Token Refresh (Automatic!)

```
Time: 1:00 PM
You run script → Access token valid → ✓ Works

Time: 2:00 PM
You run script → Access token valid → ✓ Works

Time: 3:00 PM
You run script → Access token EXPIRED
               → Script uses refresh_token
               → Gets new access_token automatically
               → Updates token.json
               → ✓ Works (you saw nothing!)

Time: 4:00 PM
You run script → New access token valid → ✓ Works
```

**You never notice token refreshes happening!**

---

## File States Comparison

### ❌ Without token.json (First Run)

```
Your Computer:
├── credentials.json     ✓ (you downloaded this)
└── token.json           ✗ (doesn't exist yet)

Script behavior:
→ Opens browser
→ Asks you to login
→ Creates token.json after login
```

### ✅ With token.json (All Subsequent Runs)

```
Your Computer:
├── credentials.json     ✓ (you downloaded this)
└── token.json           ✓ (was created on first run)

Script behavior:
→ NO browser
→ NO login
→ Uses token.json
→ Just works!
```

---

## Common Questions

### Q: How long does token.json last?

**A: Forever!**

The `refresh_token` inside never expires. The `access_token` expires every hour, but it's automatically refreshed using the `refresh_token`.

### Q: Do I need to re-login periodically?

**A: NO!**

Unless:
- You delete token.json (then login once again)
- You revoke access in Google account settings (then login once again)
- Token gets corrupted (rare - then login once again)

### Q: What if I don't run the script for months?

**A: Still works!**

When you run it again:
1. Script loads token.json
2. Access token is expired (obviously)
3. Script refreshes it automatically
4. You see: "⟳ Token expired - refreshing..."
5. You see: "✓ Token refreshed!"
6. Script continues normally

**No login needed!**

### Q: What if I run the script on a different computer?

**A: Need credentials again**

Each computer needs:
1. `credentials.json` (copy from first computer OR download again)
2. `token.json` (either copy from first computer OR login once on new computer)

**Option 1:** Copy both files to new computer → works immediately
**Option 2:** Copy only credentials.json → login once on new computer

### Q: Can I share token.json with team members?

**A: Technically yes, but NOT recommended**

Security concerns:
- Everyone would send emails as the same account
- Anyone with the file has FULL access
- No individual accountability
- If leaked, compromises the account

**Better approach:** Each person does their own OAuth once, gets their own token.json

---

## Troubleshooting: "I'm being asked to login every time"

This means token.json is NOT persisting. Check:

### 1. Does token.json exist?

```bash
ls -la token.json
```

**Expected:** `-rw------- 1 user user 1500 Nov 3 14:00 token.json`

**If missing:** Script failed to create it (check permissions)

### 2. Is token.json in the right place?

```bash
pwd
# Should show: /home/mohamad-ghoush/Documents/IEEE

ls -la *.py *.json
# Should show: mailer_dual_template.py, credentials.json, token.json
```

**If in wrong directory:** Move token.json to script directory

### 3. Can script write to directory?

```bash
touch test.txt
rm test.txt
```

**If error:** Permission issue - fix directory permissions

### 4. Are you using consistent Python environment?

```bash
# Always use:
source venv/bin/activate
python mailer_dual_template.py

# OR always use:
./run_mailer.sh

# DON'T mix different Python versions/environments
```

### 5. Is token.json valid JSON?

```bash
cat token.json
# Should show valid JSON with token, refresh_token, etc.

# Check validity:
python3 -c "import json; json.load(open('token.json')); print('✓ Valid')"
```

**If error:** File is corrupted - delete and re-authenticate

---

## Security: Protecting Your token.json

### ⚠️ What token.json Can Do

Anyone with your `token.json` can:
- ✅ Read your Google Sheets
- ✅ Send emails from your Gmail
- ❌ Cannot change password
- ❌ Cannot access other Google services
- ❌ Cannot modify sheets (read-only scope)

### 🔒 Protection Checklist

```bash
# ✓ Proper file permissions (only you can read)
chmod 600 token.json

# ✓ Not in git (already in .gitignore)
git status  # should NOT show token.json

# ✓ Backed up securely (if needed)
# Copy to encrypted backup, NOT to cloud unless encrypted

# ✓ Regular audits
# Check: https://myaccount.google.com/permissions
# Look for your app, verify it's just you
```

### 🚨 If token.json is Compromised

1. **Revoke access immediately:**
   - Visit: https://myaccount.google.com/permissions
   - Find your app → Remove access

2. **Delete local token:**
   ```bash
   rm token.json
   ```

3. **Re-authenticate:**
   ```bash
   ./run_mailer.sh
   # Login again - creates new token.json
   ```

4. **Monitor sent folder:**
   - Check for unauthorized emails
   - Change Gmail password if needed

---

## Summary

### The Golden Rule

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Login Once → token.json Created → Never Login Again      │
│                                                             │
│   (unless you delete token.json or revoke access)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Quick Reference Table

| Situation | Browser Opens? | Login Needed? | Why |
|-----------|---------------|---------------|-----|
| First run (no token.json) | ✅ Yes | ✅ Yes | Need to create token.json |
| Second run | ❌ No | ❌ No | Using token.json |
| Third run | ❌ No | ❌ No | Using token.json |
| After 1 week | ❌ No | ❌ No | Token auto-refreshes |
| After 1 month | ❌ No | ❌ No | Token auto-refreshes |
| After 1 year | ❌ No | ❌ No | Token auto-refreshes |
| Deleted token.json | ✅ Yes | ✅ Yes | Need to recreate token.json |
| Revoked access in Google | ✅ Yes | ✅ Yes | Need to re-authorize |

### The Magic Behind the Scenes

```python
# What the script does every time:

1. Check if token.json exists
2. If exists:
   a. Load it
   b. Check if access_token is valid
   c. If expired: use refresh_token to get new access_token
   d. Update token.json with new access_token
   e. Continue normally
3. If not exists:
   a. Open browser
   b. User logs in
   c. Create token.json
   d. Continue normally
```

**You only see step 3 once. After that, always step 2!**

---

## Still Having Issues?

See detailed guides:
- `AUTHENTICATION.md` - Complete authentication documentation
- `AUTHENTICATION_FIX_SUMMARY.md` - Technical details of the auth system
- `README.md` - Troubleshooting section
- `QUICKSTART.md` - Step-by-step setup

Or check your setup:
```bash
./run_mailer.sh
# Watch the output messages carefully
# They tell you exactly what's happening
```

