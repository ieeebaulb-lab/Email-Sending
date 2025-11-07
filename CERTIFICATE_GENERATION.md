# Certificate Generation with Name Overlay

## 🎯 What This Does

The script now **generates personalized certificates** for each person by:
1. Taking your **base certificate template** (PNG image)
2. Adding each person's **NAME IN CAPITALS** on it
3. **Attaching the certificate PNG directly** to the email (no links!)

---

## 📋 What You Need

### 1. Certificate Template (PNG)
A base certificate image file, like:

```
┌─────────────────────────────────────┐
│                                     │
│      CERTIFICATE OF COMPLETION      │
│                                     │
│        This certifies that          │
│                                     │
│        ___________________          │  ← Name goes here
│                                     │
│     has successfully completed      │
│        [Your Program Name]          │
│                                     │
└─────────────────────────────────────┘
```

**File format:** PNG (recommended 1920x1080 or similar)

### 2. Google Sheet with Names & Emails

| Name | Email |
|------|-------|
| John Smith | john@example.com |
| Alice Johnson | alice@example.com |

That's it! Just 2 columns.

---

## 🚀 How To Use

### Step 1: Run the Script
```bash
./run_mailer.sh
```

### Step 2: Follow Normal Steps
- Paste your Google Sheet URL
- Choose Certificate template
- Map Name and Email columns

### Step 3: Certificate Configuration (NEW!)

```
=== Certificate Configuration ===
Enter path to certificate template image (PNG): /path/to/certificate_template.png

Where should the name be placed on the certificate?
X position (default: 400): 500
Y position (default: 600): 650

Font size (default: 80): 100

Font color in hex (default: #000000 for black): #2C3E50
```

### Step 4: Continue as Normal
- Configure dry-run, etc.
- Send!

---

## 📐 Finding the Right Position

### Method 1: Trial and Error
1. Run with dry-run mode
2. Check the generated certificate
3. Adjust X/Y values
4. Repeat

### Method 2: Use Image Editor
1. Open your template in an image editor (GIMP, Photoshop, Paint)
2. Hover mouse where you want the name
3. Check coordinates shown in editor
4. Use those X/Y values

### Coordinate System:
```
(0, 0) ─────────────> X
  │
  │
  │
  ▼
  Y

Example positions:
- Top-left corner: (0, 0)
- Center-ish: (400, 600)
- Bottom-right: (1500, 1000)
```

---

## 🎨 Customization Options

### Font Size
- **Small**: 40-60 (for long names or small space)
- **Medium**: 80-100 (good default)
- **Large**: 120-150 (for prominent display)

### Font Color
Use hex codes:
- **Black**: `#000000`
- **Dark Blue**: `#2C3E50`
- **Gold**: `#FFD700`
- **Red**: `#C0392B`
- **Green**: `#27AE60`

---

## 📧 What Recipients Get

### Email Content:
```
Subject: Certificate of Completion

Dear John Smith,

Congratulations on your achievement!...

📎 Certificate attached to this email

[Attachment: certificate_JOHN_SMITH.png]
```

### Certificate File:
- Filename: `certificate_JOHN_SMITH.png`
- Content: Your template with "JOHN SMITH" printed on it
- Format: PNG image (can print, share, post)

---

## 💡 Examples

### Example 1: Simple Center Placement

**Template:** 1920x1080 certificate with blank line in center
**Configuration:**
```
X position: 960  (half of width)
Y position: 650
Font size: 90
Color: #000000
```

**Result:** Name appears centered at Y=650

### Example 2: Off-Center Elegant

**Template:** Formal certificate with signature line at bottom
**Configuration:**
```
X position: 400
Y position: 850
Font size: 70
Color: #2C3E50 (dark blue)
```

**Result:** Name in dark blue above signature line

---

## 🎯 Name Formatting

Names are automatically:
- ✅ **CAPITALIZED** (John Smith → JOHN SMITH)
- ✅ **Positioned exactly** where you specify
- ✅ **Same font size** for all recipients
- ✅ **Same color** for all recipients

---

## 🔧 Troubleshooting

### "Template file not found"
- Check the file path is correct
- Use absolute path: `/home/user/certificate.png`
- Or relative: `./certificate_template.png`

### Name doesn't appear on certificate
- Check X/Y coordinates are within image bounds
- Try increasing font size
- Check font color contrasts with background

### Name is cut off
- Reduce font size
- Adjust X position
- Use shorter name format

### Font looks bad
- The script uses system fonts automatically
- On Linux: Uses DejaVu Sans Bold
- Falls back to default font if needed

### Certificate quality is poor
- Use high-resolution template (1920x1080 or higher)
- Save template as PNG, not JPG
- Ensure template has good quality

---

## 📊 File Sizes

| Recipients | Approx. Email Size | Time to Send |
|------------|-------------------|--------------|
| 1 person | ~500KB | Instant |
| 10 people | ~5MB total | ~10 seconds |
| 50 people | ~25MB total | ~1 minute |
| 100 people | ~50MB total | ~2 minutes |

**Note:** Each certificate PNG is typically 200-500KB

---

## ⚡ Quick Reference

### Minimal Setup:
1. Certificate template PNG
2. Google Sheet with Name + Email
3. Run script
4. Provide template path + coordinates
5. Done!

### What Happens:
1. Script loads your template
2. For each person:
   - Adds their name (CAPS) to template
   - Saves as PNG
   - Attaches to email
   - Sends
3. Recipients get personalized certificates!

---

## 🎓 Tips

1. **Test First**: Use dry-run with your own email to verify positioning
2. **High Resolution**: Use at least 1920x1080 template
3. **Contrast**: Ensure text color contrasts well with background
4. **Simple Template**: Less clutter = easier to position text
5. **Backup**: Keep original template file safe

---

## 🚀 Next Steps

Ready to send certificates?

```bash
./run_mailer.sh
```

Follow the prompts and your certificates will be generated and sent automatically! 🎉


