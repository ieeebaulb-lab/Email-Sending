# Formal Email Mailer with Dual Templates

A Python CLI tool for sending professional HTML emails via Gmail API with two formal templates: **Certificate Delivery** and **Upcoming Event Invitation**. Recipients are read from Google Sheets with full validation, logging, and throttling support.

> **🚀 New here?** Start with `START_HERE.md` or `QUICKSTART.md` for fast setup!
>
> **🔑 Authentication:** You only login ONCE - credentials are saved in `token.json` and auto-refresh. See `AUTHENTICATION.md` if you have login issues.

## Features

- **Two Professional Templates**
  - Certificate Delivery (with Google Drive links)
  - Event Invitation (with RSVP and calendar integration)
- **Interactive CLI** - Runtime configuration with sensible defaults
- **Google Sheets Integration** - Read recipient data with flexible column mapping
- **Gmail API** - OAuth-authenticated sending
- **Validation** - Required field checking, email format validation
- **Dry-Run Mode** - Preview emails without sending
- **CSV Logging** - Track all send attempts with timestamps
- **Throttling** - Configurable delays between sends
- **Formal Styling** - Table-based HTML optimized for Gmail/Outlook

## Prerequisites

1. **Python 3.7+**
2. **Google Cloud Project** with:
   - Gmail API enabled
   - Google Sheets API enabled
   - OAuth 2.0 credentials (Desktop app)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Gmail API** and **Google Sheets API**
4. Create **OAuth 2.0 Client ID** credentials (Desktop application)
5. Download credentials as `credentials.json`
6. Place `credentials.json` in the same directory as the script

**Note:** You only need to login once! After first authentication, your credentials are saved in `token.json` and automatically refreshed. See `AUTHENTICATION.md` for details.

### 3. Prepare Your Google Sheet

Create a Google Sheet with your recipient data. Required columns depend on the template:

#### Certificate Template - Required Columns
- `Name` - Recipient's full name
- `Email` - Recipient's email address
- `CourseTitle` - Name of the completed course
- `CompletionDate` - Date of completion
- `CertificateDriveLink` - Google Drive shareable link to certificate
- `CertificateID` - Unique certificate identifier
- `OrgName` - Organization name
- `SupportEmail` - Support contact email
- `Year` - Current year (for copyright)

#### Certificate Template - Optional Columns
- `VerificationURL` - URL to verify certificate
- `OrgAddress` - Organization address
- `OrgPhone` - Organization phone
- `TeamOrSignerName` - Name of signer
- `Title` - Signer's title

#### Event Template - Required Columns
- `Name` - Recipient's full name
- `Email` - Recipient's email address
- `OrgName` - Organization name
- `EventTitle` - Name of the event
- `EventDate` - Event date
- `EventTime` - Event time
- `EventTimezone` - Timezone (e.g., EST, PST)
- `EventLocation` - Physical or virtual location
- `EventDescription` - Brief description
- `RSVP_URL` - Link to RSVP form
- `CalendarICSURL` - Link to calendar file
- `SupportEmail` - Support contact email
- `Year` - Current year (for copyright)

#### Event Template - Optional Columns
- `Outcome1` - First expected outcome
- `Outcome2` - Second expected outcome
- `Speaker1Name` - First speaker name
- `Speaker1Title` - First speaker title
- `Speaker2Name` - Second speaker name
- `Speaker2Title` - Second speaker title
- `HeroImageURL` - Header image URL
- `UnsubscribeURL` - Unsubscribe link
- `OrgAddress` - Organization address

## Usage

### Run the Script

```bash
python mailer_dual_template.py
```

### Interactive Flow

The script will guide you through:

1. **Authentication** - OAuth flow (first run only)
2. **Sheet Configuration** - Enter Sheet ID and range
3. **Template Selection** - Choose Certificate or Event template
4. **Column Mapping** - Map spreadsheet columns to template fields
5. **Send Options** - Configure dry-run, throttling, filters
6. **Preview** - Review sample messages
7. **Confirmation** - Approve before sending
8. **Execution** - Send emails with progress tracking
9. **Summary** - View results and log location

### Example Session

```
=== Google Sheet Configuration ===
Enter Google Sheet ID: 1abc123xyz...
Enter range (default: Sheet1!A1:Z1000): Sheet1!A1:Z100

=== Template Selection ===
1. Certificate Delivery
2. Upcoming Event Invitation
Choose template (1 or 2): 1

=== Send Options ===
Dry-run mode? (Y/n): y
Throttle seconds (default: 0.8): 1
From address override (blank for 'me'): 
Filter to only this email (blank for all): 
CSV log path (default: send_log.csv): 
Custom subject line (blank for default): 

[Preview and confirmation steps...]

[1/50] DRY-RUN john@example.com: Certificate of Completion — Python...
[2/50] DRY-RUN jane@example.com: Certificate of Completion — Python...
...
```

## Template Details

### Certificate Delivery

**Subject**: "Certificate of Completion — {CourseTitle}"

**Features**:
- Formal congratulatory message
- Primary "View Certificate" CTA button
- Certificate details box (ID, issuer, date)
- Optional verification URL
- Professional sign-off
- Privacy notice

**Use Cases**: Course completions, training programs, certifications

### Event Invitation

**Subject**: "Invitation: {EventTitle} — {EventDate}"

**Features**:
- Optional hero image
- Scannable event details box
- Event description with optional outcomes
- Optional speakers section
- Dual CTAs: RSVP + Add to Calendar
- Optional unsubscribe link

**Use Cases**: Conferences, webinars, workshops, networking events

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| Dry-run | Preview without sending | Yes |
| Throttle | Seconds between sends | 0.8 |
| From Address | Override sender | 'me' |
| Filter Email | Test with single email | None |
| Log Path | CSV results file | send_log.csv |
| Custom Subject | Override default subject | Template default |

## Logging

All send attempts are logged to CSV with columns:

- `Email` - Recipient address
- `Subject` - Email subject line
- `Status` - SENT / FAILED / SKIPPED / DRY-RUN
- `MessageId` - Gmail message ID (if sent)
- `Error` - Error reason (if failed/skipped)
- `Timestamp` - ISO format timestamp
- `TemplateUsed` - certificate or event

## Troubleshooting

### "credentials.json not found"
Download OAuth credentials from Google Cloud Console as Desktop app type.

### "Access blocked: Authorization Error"
Ensure both Gmail API and Sheets API are enabled in your Google Cloud project.

### "Invalid grant" or token errors
Delete `token.json` and re-authenticate.

### Being asked to login every time
The script saves your authentication in `token.json` - you should only login once! If you're being asked repeatedly:
1. Check if `token.json` exists in the script directory
2. Check file permissions: `chmod 600 token.json`
3. See `AUTHENTICATION.md` for detailed troubleshooting

### Missing required fields
Check column mapping - field names are case-sensitive during mapping.

### Emails not sending (dry-run works)
Verify Gmail API scope includes `gmail.send`.

## Best Practices

1. **Always test with dry-run first**
2. **Use throttling** (0.5-1 second) to avoid rate limits
3. **Validate your sheet** before running on large datasets
4. **Filter to single email** for initial testing
5. **Keep logs** for audit trails
6. **Use meaningful certificate IDs** for verification
7. **Test links** in your sheet (Drive links, RSVP URLs)

## Security Notes

- OAuth tokens are stored in `token.json` - keep secure
- Never commit `credentials.json` or `token.json` to version control
- Certificate links should use Google Drive's "Anyone with link" permission
- Consider adding `.gitignore` entries for sensitive files

## Limitations

- Gmail API has sending limits (500/day for standard accounts, 2000/day for Google Workspace)
- Large batches should be split across multiple days
- HTML rendering may vary by email client
- Certificate PDF generation is not implemented (assumes pre-generated links)

## Future Enhancements

The script includes scaffolding for:
- Automatic certificate PDF generation
- Overlay name/date/ID on base certificate template
- Auto-upload to Google Drive with shareable links

## License

This script is provided as-is for internal organizational use.

## Support

For issues or questions, refer to:
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
