# Authentication Guide

## How Authentication Works

The script uses **OAuth 2.0** to securely access your Google Sheets and Gmail. You only need to login **ONCE** - credentials are saved locally and automatically refreshed.

## Files Explained

### `credentials.json` (Required)
- Downloaded from Google Cloud Console
- Contains your OAuth client ID and secret
- Used for initial authentication
- **Keep local, don't commit to git**

### `token.json` (Auto-generated)
- Created automatically after first login
- Contains your access token and refresh token
- **This is the key** - keeps you logged in between runs
- Auto-refreshes when expired (tokens last ~7 days before needing refresh)
- **Keep local, don't commit to git**

## First Run

When you run the script for the first time:

```bash
python mailer_dual_template.py
```

You'll see:
```
======================================================================
FIRST-TIME AUTHENTICATION
======================================================================
A browser window will open for you to authorize this app.
After authorization, you won't need to login again.
Your credentials will be saved to token.json
======================================================================
Press Enter to open browser and continue...
```

1. Press Enter
2. Browser opens → Select your Google account
3. Click "Allow" to grant permissions
4. Browser shows "Success" → close it
5. Script continues with `token.json` saved

## Subsequent Runs

Every time after the first run:

```bash
python mailer_dual_template.py
```

You'll see:
```
✓ Found existing token.json - loading credentials...
✓ Credentials loaded successfully. No login required!
```

**No browser window, no login needed!** 🎉

## Token Auto-Refresh

If your token expires (usually after 7 days of inactivity):

```
⟳ Token expired - refreshing automatically...
✓ Token refreshed successfully!
```

This happens silently in the background. You still don't need to login!

## Why You Might Need to Re-Login

You'll only need to re-authenticate if:

1. **You deleted `token.json`** - Don't delete this file!
2. **Token refresh failed** - Rare, usually due to network issues
3. **You revoked access** - Through Google account settings
4. **Scopes changed** - If the script is updated to need new permissions

## Troubleshooting

### "Need to login every time"

**Check this:**
```bash
ls -la token.json
```

- If file doesn't exist → authentication didn't save properly
- If file exists but you're still asked to login → token might be corrupted

**Solution:**
```bash
# Delete the token and re-authenticate once
rm token.json
python mailer_dual_template.py
# Login when prompted - this time it should save properly
```

### "Token refresh failed"

**Causes:**
- Network issues
- Revoked access in Google account
- Expired refresh token (rare, usually after months)

**Solution:**
```bash
rm token.json
python mailer_dual_template.py
```

### "credentials.json not found"

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Select your project
3. Create OAuth 2.0 Client ID (Application type: Desktop)
4. Download as `credentials.json`
5. Place in script directory

### File permissions issue

If running on Linux/Mac, ensure proper permissions:
```bash
chmod 600 token.json credentials.json
```

## Security Notes

### ✅ Safe Practices

- Keep both files local only
- Add them to `.gitignore` (already done)
- Don't share `token.json` or `credentials.json`
- Store backups in secure location only

### ⚠️ What Each File Can Do

**credentials.json:**
- Can be used to request access on your behalf
- If leaked: someone could start OAuth flow pretending to be your app
- Not dangerous alone (still needs user to approve)

**token.json:**
- Provides FULL access to granted permissions (Sheets read, Gmail send)
- If leaked: someone can read your sheets and send emails as you
- **More sensitive than credentials.json**

### 🔒 Best Security

1. **Use a dedicated Google Account** for sending (not your personal account)
2. **Enable 2FA** on the Google account
3. **Regularly review** authorized apps: https://myaccount.google.com/permissions
4. **Monitor** Gmail sent folder for unauthorized sends

## Advanced: Service Account (No Interactive Login)

If you need completely automated/server usage with **zero interactive login**:

See `SERVICE_ACCOUNT_SETUP.md` for instructions on using a service account instead of OAuth.

**Pros:**
- No browser interaction needed
- No token expiration worries
- Perfect for cron jobs/servers

**Cons:**
- More complex setup
- Needs domain-wide delegation for Gmail
- Or separate service account email setup

## Quick Reference

| Scenario | File Needed | What Happens |
|----------|-------------|--------------|
| First run | `credentials.json` | Browser opens, login required, creates `token.json` |
| Normal run | `token.json` | Loads token, no login needed |
| Token expired | `token.json` | Auto-refreshes silently |
| Token corrupted | `credentials.json` | Delete `token.json`, re-login once |
| Both missing | `credentials.json` | Download from Google Cloud Console |

## Summary

**You should only need to login ONCE when you first run the script.**

After that, `token.json` keeps you authenticated and auto-refreshes. The script is designed for convenience - no repeated logins!

If you're being asked to login every time, something is wrong with file saving/permissions. Check the troubleshooting section above.


