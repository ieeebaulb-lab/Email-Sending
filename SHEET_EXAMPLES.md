# Google Sheet Structure Examples

## Certificate Template - Column Headers

Here's an example structure for your Google Sheet when using the **Certificate Delivery** template:

| Name | Email | CourseTitle | CompletionDate | CertificateDriveLink | CertificateID | OrgName | SupportEmail | Year | VerificationURL | OrgAddress | OrgPhone | TeamOrSignerName | Title |
|------|-------|-------------|----------------|----------------------|---------------|---------|--------------|------|-----------------|------------|----------|------------------|-------|
| John Smith | john@example.com | Advanced Python Programming | March 15, 2025 | https://drive.google.com/file/d/ABC123/view | CERT-2025-001 | IEEE Student Branch | support@ieee.org | 2025 | https://verify.example.com/CERT-2025-001 | 123 Tech St, City, ST 12345 | (555) 123-4567 | Dr. Jane Doe | Program Director |
| Alice Johnson | alice@example.com | Machine Learning Fundamentals | March 20, 2025 | https://drive.google.com/file/d/DEF456/view | CERT-2025-002 | IEEE Student Branch | support@ieee.org | 2025 | https://verify.example.com/CERT-2025-002 | 123 Tech St, City, ST 12345 | (555) 123-4567 | Dr. Jane Doe | Program Director |

### Required Fields
- `Name` - Full name of certificate recipient
- `Email` - Valid email address
- `CourseTitle` - Name of the course/program
- `CompletionDate` - Date completed (any readable format)
- `CertificateDriveLink` - Full Google Drive shareable link
- `CertificateID` - Unique identifier for verification
- `OrgName` - Your organization name
- `SupportEmail` - Contact email for support
- `Year` - Current year (for footer copyright)

### Optional Fields
- `VerificationURL` - URL to verify certificate authenticity
- `OrgAddress` - Physical address for footer
- `OrgPhone` - Contact phone for footer
- `TeamOrSignerName` - Name of person signing off
- `Title` - Title/position of signer

---

## Event Template - Column Headers

Here's an example structure for your Google Sheet when using the **Event Invitation** template:

| Name | Email | OrgName | EventTitle | EventDate | EventTime | EventTimezone | EventLocation | EventDescription | RSVP_URL | CalendarICSURL | SupportEmail | Year | Outcome1 | Outcome2 | Speaker1Name | Speaker1Title | Speaker2Name | Speaker2Title | HeroImageURL | UnsubscribeURL | OrgAddress |
|------|-------|---------|------------|-----------|-----------|---------------|---------------|------------------|----------|----------------|--------------|------|----------|----------|--------------|---------------|--------------|---------------|--------------|----------------|------------|
| John Smith | john@example.com | IEEE Student Branch | Tech Innovation Summit 2025 | Saturday, November 15, 2025 | 9:00 AM | EST | Online via Zoom | Join us for a day of cutting-edge technology discussions, networking, and hands-on workshops. | https://forms.gle/abc123 | https://calendar.example.com/event.ics | events@ieee.org | 2025 | Network with industry leaders | Gain hands-on experience with emerging technologies | Dr. Emily Chen | Chief Technology Officer, TechCorp | Prof. Michael Brown | AI Research Lead, University |  https://example.com/hero.jpg | https://example.com/unsubscribe?id=123 | 123 Tech St, City, ST 12345 |
| Alice Johnson | alice@example.com | IEEE Student Branch | Tech Innovation Summit 2025 | Saturday, November 15, 2025 | 9:00 AM | EST | Online via Zoom | Join us for a day of cutting-edge technology discussions, networking, and hands-on workshops. | https://forms.gle/abc123 | https://calendar.example.com/event.ics | events@ieee.org | 2025 | Network with industry leaders | Gain hands-on experience with emerging technologies | Dr. Emily Chen | Chief Technology Officer, TechCorp | Prof. Michael Brown | AI Research Lead, University | https://example.com/hero.jpg | https://example.com/unsubscribe?id=123 | 123 Tech St, City, ST 12345 |

### Required Fields
- `Name` - Full name of invitee
- `Email` - Valid email address
- `OrgName` - Your organization name
- `EventTitle` - Name of the event
- `EventDate` - Date of event (readable format)
- `EventTime` - Start time
- `EventTimezone` - Timezone abbreviation (EST, PST, etc.)
- `EventLocation` - Physical address or "Online via Zoom"
- `EventDescription` - Brief description (1-3 sentences)
- `RSVP_URL` - Link to registration/RSVP form
- `CalendarICSURL` - Link to download .ics calendar file
- `SupportEmail` - Contact email for questions
- `Year` - Current year (for footer copyright)

### Optional Fields
- `Outcome1` - First key outcome/benefit
- `Outcome2` - Second key outcome/benefit
- `Speaker1Name` - First featured speaker name
- `Speaker1Title` - First speaker title/affiliation
- `Speaker2Name` - Second featured speaker name
- `Speaker2Title` - Second speaker title/affiliation
- `HeroImageURL` - Header image URL (event photo/graphic)
- `UnsubscribeURL` - Link to unsubscribe from future events
- `OrgAddress` - Physical address for footer

---

## Tips for Sheet Setup

### 1. Column Order
- Order doesn't matter - the script will prompt you to map columns
- Use the exact field names above as headers for automatic detection

### 2. Data Validation
- Keep data clean (no extra spaces)
- Use consistent date formats within a column
- Test URLs before importing (especially Drive links)

### 3. Google Drive Links
For certificates, ensure Drive links are:
- Shareable ("Anyone with the link")
- Set to "Viewer" permissions
- Using the full URL (not shortened)

Example: `https://drive.google.com/file/d/1ABC-xyz123_DEF/view?usp=sharing`

### 4. Calendar ICS Files
You can create .ics files using:
- Google Calendar (Create event → More Actions → Publish event)
- Outlook Calendar (Share event → Get link)
- Online generators (search "ICS file generator")
- Store on Google Drive or other hosting

### 5. Personalization
Each row should have unique recipient data:
- Unique `Name` and `Email`
- For certificates: unique `CertificateID` and `CertificateDriveLink`
- Other fields can be identical across rows (e.g., `OrgName`, `Year`)

### 6. Testing
Create a test sheet with 2-3 rows:
- Include your own email addresses
- Use valid but test data
- Run in dry-run mode first
- Check preview carefully before sending

---

## Example Sheet Links

You can create a copy of these example templates:

### Certificate Template
```
Copy this structure or download CSV:
Name,Email,CourseTitle,CompletionDate,CertificateDriveLink,CertificateID,OrgName,SupportEmail,Year,TeamOrSignerName,Title
John Smith,john@example.com,Python Programming,March 15 2025,https://drive.google.com/file/d/test,CERT-001,IEEE,support@ieee.org,2025,Dr. Smith,Director
```

### Event Template
```
Copy this structure or download CSV:
Name,Email,OrgName,EventTitle,EventDate,EventTime,EventTimezone,EventLocation,EventDescription,RSVP_URL,CalendarICSURL,SupportEmail,Year
John Smith,john@example.com,IEEE,Tech Summit,Nov 15 2025,9:00 AM,EST,Online,Join us for tech talks,https://forms.gle/test,https://calendar.test,support@ieee.org,2025
```

---

## Troubleshooting Sheet Issues

### "Missing required field: X"
- Check spelling of column header (case-insensitive)
- Ensure cell is not empty for that recipient
- Map the column correctly during script setup

### "Invalid email format"
- Remove extra spaces
- Check for typos in domain
- Use standard format: name@domain.com

### "Missing CertificateDriveLink" or "Missing RSVP_URL"
- These are critical links - cannot be empty
- Test links open correctly before running script
- For Drive: ensure sharing is enabled

### Empty Cells
- Optional fields can be empty
- Required fields must have values
- Script will skip rows with missing required fields

---

## Best Practices

1. **Start Small** - Test with 2-3 recipients first
2. **Consistent Formatting** - Keep date/time formats consistent
3. **Test Links** - Click every URL before bulk sending
4. **Backup Sheet** - Keep a copy before making changes
5. **Version Control** - Add version column to track resends
6. **Status Tracking** - Add "Sent" column to mark completed rows

