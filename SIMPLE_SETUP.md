# Simple Setup - Name and Email Only

## ✅ Perfect! Your Sheet Only Needs:

| Name | Email |
|------|-------|
| John Smith | john@example.com |
| Alice Johnson | alice@example.com |
| Bob Wilson | bob@example.com |

**That's it!** Just Name and Email columns.

---

## 🚀 How It Works Now

### Step 1: Run the Script
```bash
./run_mailer.sh
```

### Step 2: Paste Your Sheet URL
```
Enter Google Sheet URL or ID: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
```

### Step 3: Choose Template
```
Choose template:
1. Certificate Delivery  ← Choose this
```

### Step 4: Map Columns
```
[REQUIRED] Map 'Name': Name          ← Press Enter
[REQUIRED] Map 'Email': Email        ← Press Enter
```

**That's it!** No other fields required!

### Step 5: Enter Base Certificate Link
```
=== Certificate Configuration ===
Enter the base certificate link/URL.
The person's name will be added to this link automatically.

Enter base certificate link: https://your-certificate-site.com/view/
```

### Step 6: Configure and Send
- Dry-run? → **Y** (test first!)
- Continue through other prompts...

---

## 🎯 What Happens

### Your Input:
**Google Sheet:**
| Name | Email |
|------|-------|
| John Smith | john@example.com |
| Alice Johnson | alice@example.com |

**Base Certificate Link:**
```
https://certificate.example.com/view/
```

### What Script Creates:

**For John Smith:**
- Email to: `john@example.com`
- Certificate Link: `https://certificate.example.com/view/JOHN_SMITH`
- Email says: "Dear John Smith, Congratulations on your achievement!..."

**For Alice Johnson:**
- Email to: `alice@example.com`
- Certificate Link: `https://certificate.example.com/view/ALICE_JOHNSON`
- Email says: "Dear Alice Johnson, Congratulations on your achievement!..."

---

## 📝 Name Formatting

Names are automatically:
- ✅ **CAPITALIZED** (John Smith → JOHN SMITH)
- ✅ **Spaces replaced with underscores** (JOHN SMITH → JOHN_SMITH)
- ✅ **Appended to your base link**

### Examples:

| Name in Sheet | Formatted in Link |
|---------------|-------------------|
| John Smith | JOHN_SMITH |
| Alice-Marie Johnson | ALICE-MARIE_JOHNSON |
| Bob | BOB |
| María García | MARíA_GARCíA |

---

## 🔗 Link Structure Examples

### If Base Link Ends with `/`:
```
Base: https://certificate.com/view/
Name: John Smith
Result: https://certificate.com/view/JOHN_SMITH
```

### If Base Link Doesn't End with `/`:
```
Base: https://certificate.com/view
Name: John Smith  
Result: https://certificate.com/view/JOHN_SMITH
```

**Script handles both automatically!** ✅

---

## 📧 Email Preview

### Subject:
```
Certificate of Completion
```

### Body:
```
Dear John Smith,

Congratulations on your achievement! We are pleased to provide 
your official certificate of completion.

Your certificate is securely hosted and accessible via the link below:

[View Certificate] → https://certificate.com/view/JOHN_SMITH

Certificate Details:
Certificate ID: N/A
Issued by: Our Organization
Completion Date: recently

...
```

---

## 🎨 What Gets Auto-Filled

Since you only have Name and Email, the script uses defaults for:

| Field | Default Value |
|-------|---------------|
| OrgName | "Our Organization" |
| CompletionDate | "recently" |
| CertificateID | "N/A" |
| SupportEmail | "support@example.com" |
| Year | Current year (2025) |
| TeamOrSignerName | "The Team" |

**Want to customize these?** You can add optional columns to your sheet later!

---

## 💡 Optional: Add More Columns Later

### Minimal (Current):
| Name | Email |
|------|-------|

### With Organization Name:
| Name | Email | OrgName |
|------|-------|---------|
| John | john@example.com | IEEE |

### With Date:
| Name | Email | CompletionDate |
|------|-------|----------------|
| John | john@example.com | November 3, 2025 |

### Full Details:
| Name | Email | OrgName | CompletionDate | CourseTitle | CertificateID |
|------|-------|---------|----------------|-------------|---------------|
| John | john@example.com | IEEE | Nov 3 2025 | Python 101 | CERT-001 |

**Add columns as needed - all optional!**

---

## ⚡ Quick Commands

### First Run (Setup + Test)
```bash
./run_mailer.sh
# Follow prompts
# Use dry-run to test
```

### Second Run (Send for Real)
```bash
./run_mailer.sh
# Same certificate link
# Dry-run? → n (send for real)
```

---

## 🎯 Summary

**You provide:**
1. Google Sheet with Name + Email
2. Base certificate link

**Script creates:**
1. Personalized certificate links (with CAPITALIZED names)
2. Professional emails
3. Sends to each person

**Minimal setup, maximum automation!** 🚀

