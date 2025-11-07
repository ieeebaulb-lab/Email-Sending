#!/usr/bin/env python3
"""
Formal Email Mailer with Dual Templates
Sends Certificate Delivery or Event Invitation emails via Gmail API
Reads recipients from Google Sheets
"""

import os
import sys
import csv
import time
import base64
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, List, Optional, Tuple
from io import BytesIO

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠ Warning: Pillow not installed. Certificate generation disabled.")

# OAuth Scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

# ============================================================================
# HTML EMAIL TEMPLATES
# ============================================================================

CERTIFICATE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You for Attending</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, Helvetica, sans-serif;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="640" style="margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 30px; text-align: center; border-bottom: 3px solid #2c5282;">
                            <h1 style="margin: 0; font-size: 26px; color: #1a202c; font-weight: bold;">{OrgName}</h1>
                            <p style="margin: 8px 0 0; font-size: 14px; color: #718096;">Thank You for Attending</p>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; font-size: 16px; color: #2d3748; line-height: 1.6;">Dear {Name},</p>

                            <p style="margin: 0 0 20px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                {ThankYouMessage}
                            </p>

                            <p style="margin: 0 0 30px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                {AttachmentLine}
                            </p>

                            {EventDetailsSection}

                            {ResourcesSection}

                            {FeedbackSection}

                            <p style="margin: 0 0 8px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                If you have any questions or would like to stay in touch, please contact us at
                                <a href="mailto:{SupportEmail}" style="color: #2c5282; text-decoration: none;">{SupportEmail}</a>.
                            </p>

                            <p style="margin: 30px 0 8px; font-size: 16px; color: #2d3748; line-height: 1.6;">Warm regards,</p>
                            <p style="margin: 0; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                <strong>{TeamOrSignerName}</strong><br>
                                {Title}<br>
                                {OrgName}
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f7fafc; border-top: 1px solid #e2e8f0; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0 0 12px; font-size: 13px; color: #718096; line-height: 1.6; text-align: center;">
                                {FooterContact}
                            </p>
                            <p style="margin: 0 0 12px; font-size: 12px; color: #a0aec0; line-height: 1.5; text-align: center;">
                                This message and certificate are intended for {Name}. Please do not share without consent.
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #a0aec0; text-align: center;">
                                &copy; {Year} {OrgName}. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

EVENT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Event Invitation</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, Helvetica, sans-serif;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f5f5f5;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="640" style="margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Hero Image (Optional) -->
                    {HeroImageSection}
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 30px; text-align: center; border-bottom: 3px solid #2c5282;">
                            <h1 style="margin: 0; font-size: 26px; color: #1a202c; font-weight: bold;">{OrgName}</h1>
                            <p style="margin: 8px 0 0; font-size: 14px; color: #718096;">cordially invites you</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; font-size: 16px; color: #2d3748; line-height: 1.6;">Dear {Name},</p>
                            
                            <p style="margin: 0 0 30px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                We are pleased to invite you to attend <strong>{EventTitle}</strong>, hosted by <strong>{OrgName}</strong>.
                            </p>
                            
                            <!-- Event Details Box -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f7fafc; border-left: 4px solid #2c5282; border-radius: 6px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 24px;">
                                        <h2 style="margin: 0 0 20px; font-size: 22px; color: #1a202c;">{EventTitle}</h2>
                                        
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <p style="margin: 0; font-size: 15px; color: #2d3748; line-height: 1.6;">
                                                        <strong>Date:</strong> {EventDate}
                                                    </p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <p style="margin: 0; font-size: 15px; color: #2d3748; line-height: 1.6;">
                                                        <strong>Time:</strong> {EventTime} {EventTimezone}
                                                    </p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <p style="margin: 0; font-size: 15px; color: #2d3748; line-height: 1.6;">
                                                        <strong>Location:</strong> {EventLocation}
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Event Description -->
                            <p style="margin: 0 0 20px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                {EventDescription}
                            </p>
                            
                            {OutcomesSection}
                            
                            {SpeakersSection}
                            
                            <!-- Action Buttons -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-top: 30px;">
                                <tr>
                                    <td align="center" style="padding: 0 0 20px;">
                                        <a href="{RSVP_URL}" 
                                           style="display: inline-block; padding: 16px 48px; background-color: #2c5282; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 6px; margin: 0 8px;">
                                            RSVP Now
                                        </a>
                                        <a href="{CalendarICSURL}" 
                                           style="display: inline-block; padding: 16px 32px; background-color: #ffffff; color: #2c5282; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 6px; border: 2px solid #2c5282; margin: 0 8px;">
                                            Add to Calendar
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding: 0 0 30px;">
                                        <p style="margin: 0; font-size: 13px; color: #718096; line-height: 1.6;">
                                            RSVP: <a href="{RSVP_URL}" style="color: #2c5282; word-break: break-all;">{RSVP_URL}</a><br>
                                            Calendar: <a href="{CalendarICSURL}" style="color: #2c5282; word-break: break-all;">{CalendarICSURL}</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 8px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                We look forward to your participation. Should you have any questions, please contact us at 
                                <a href="mailto:{SupportEmail}" style="color: #2c5282; text-decoration: none;">{SupportEmail}</a>.
                            </p>
                            
                            <p style="margin: 30px 0 8px; font-size: 16px; color: #2d3748; line-height: 1.6;">Kind regards,</p>
                            <p style="margin: 0; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                <strong>{OrgName} Team</strong>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f7fafc; border-top: 1px solid #e2e8f0; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0 0 12px; font-size: 13px; color: #718096; line-height: 1.6; text-align: center;">
                                {FooterContact}
                            </p>
                            {UnsubscribeSection}
                            <p style="margin: 0; font-size: 12px; color: #a0aec0; text-align: center;">
                                &copy; {Year} {OrgName}. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

# ============================================================================
# PLAIN TEXT TEMPLATES
# ============================================================================

CERTIFICATE_TEXT_TEMPLATE = """
{OrgName}
Thank You for Attending

Dear {Name},

{ThankYouMessagePlain}

{AttachmentLinePlain}

{EventDetailsBlock}{ResourcesBlock}{FeedbackBlock}
Warm regards,
{TeamOrSignerName}
{Title}
{OrgName}

---
{FooterContactText}
© {Year} {OrgName}. All rights reserved.
"""

EVENT_TEXT_TEMPLATE = """
{OrgName}
Event Invitation

Dear {Name},

We are pleased to invite you to attend {EventTitle}, hosted by {OrgName}.

EVENT DETAILS
Event: {EventTitle}
Date: {EventDate}
Time: {EventTime} {EventTimezone}
Location: {EventLocation}

DESCRIPTION
{EventDescription}

{OutcomesText}

{SpeakersText}

RSVP
Please confirm your attendance: {RSVP_URL}

ADD TO CALENDAR
{CalendarICSURL}

We look forward to your participation. Should you have any questions, please contact us at {SupportEmail}.

Kind regards,
{OrgName} Team

---
{FooterContactText}
{UnsubscribeText}

© {Year} {OrgName}. All rights reserved.
"""

# ============================================================================
# TEMPLATE CONFIGURATIONS
# ============================================================================

TEMPLATE_CONFIGS = {
    'certificate': {
        'name': 'Thank You for Attending',
        'html_template': CERTIFICATE_HTML_TEMPLATE,
        'text_template': CERTIFICATE_TEXT_TEMPLATE,
        'subject_default': 'Thank You for Attending',
        'required_fields': ['Name', 'Email'],
        'optional_fields': ['EventName', 'CourseTitle', 'EventDate', 'CompletionDate',
                           'EventLocation', 'ResourcesURL', 'ResourcesDescription',
                           'FeedbackURL', 'OrgName', 'SupportEmail', 'Year',
                           'OrgAddress', 'OrgPhone', 'TeamOrSignerName', 'Title']
    },
    'event': {
        'name': 'Upcoming Event Invitation',
        'html_template': EVENT_HTML_TEMPLATE,
        'text_template': EVENT_TEXT_TEMPLATE,
        'subject_default': 'Invitation: {EventTitle} — {EventDate}',
        'required_fields': ['Name', 'Email', 'OrgName', 'EventTitle', 'EventDate', 
                           'EventTime', 'EventTimezone', 'EventLocation', 
                           'EventDescription', 'RSVP_URL', 'CalendarICSURL', 
                           'SupportEmail', 'Year'],
        'optional_fields': ['Outcome1', 'Outcome2', 'Speaker1Name', 'Speaker1Title', 
                           'Speaker2Name', 'Speaker2Title', 'HeroImageURL', 
                           'UnsubscribeURL', 'OrgAddress']
    }
}

# ============================================================================
# AUTHENTICATION
# ============================================================================

def authorize() -> Tuple[any, any]:
    """
    Authorize with Google APIs using OAuth 2.0.
    Returns authenticated service objects for Sheets and Gmail.
    
    Authentication is cached in token.json - you only need to login once!
    The token will automatically refresh when expired.
    """
    creds = None
    
    # Check for existing token
    if os.path.exists('token.json'):
        print("✓ Found existing token.json - loading credentials...")
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            print("✓ Credentials loaded successfully. No login required!\n")
        except Exception as e:
            print(f"⚠ Error loading token.json: {e}")
            print("  Will need to re-authenticate.\n")
            creds = None
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("⟳ Token expired - refreshing automatically...")
            try:
                creds.refresh(Request())
                print("✓ Token refreshed successfully!\n")
            except Exception as e:
                print(f"✗ Token refresh failed: {e}")
                print("  Will need to re-authenticate.\n")
                creds = None
        
        if not creds:
            if not os.path.exists('credentials.json'):
                print("ERROR: credentials.json not found!")
                print("Please download OAuth credentials from Google Cloud Console.")
                print("Visit: https://console.cloud.google.com/apis/credentials")
                sys.exit(1)
            
            print("=" * 70)
            print("FIRST-TIME AUTHENTICATION")
            print("=" * 70)
            print("A browser window will open for you to authorize this app.")
            print("After authorization, you won't need to login again.")
            print("Your credentials will be saved to token.json")
            print("=" * 70)
            input("Press Enter to open browser and continue...")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"\nERROR during authentication: {e}")
                sys.exit(1)
        
        # Save credentials for future use
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("\n✓ Authentication successful!")
            print("✓ Token saved to token.json - you won't need to login again!")
            print("  (Token will auto-refresh when expired)\n")
        except Exception as e:
            print(f"\n⚠ Warning: Could not save token: {e}")
            print("  You may need to re-authenticate next time.\n")
    
    # Build service objects
    sheets_service = build('sheets', 'v4', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    
    return sheets_service, gmail_service

# ============================================================================
# GOOGLE SHEETS
# ============================================================================

def extract_sheet_id(input_string: str) -> str:
    """
    Extract Sheet ID from a URL or return the ID if already provided.
    Handles various Google Sheets URL formats.
    """
    input_string = input_string.strip()
    
    # If it's already just an ID (no slashes), return it
    if '/' not in input_string and 'http' not in input_string:
        return input_string
    
    # Try to extract from URL patterns
    # Pattern 1: /d/SHEET_ID/
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', input_string)
    if match:
        return match.group(1)
    
    # Pattern 2: spreadsheets/d/SHEET_ID
    match = re.search(r'spreadsheets/d/([a-zA-Z0-9-_]+)', input_string)
    if match:
        return match.group(1)
    
    # Pattern 3: key=SHEET_ID
    match = re.search(r'key=([a-zA-Z0-9-_]+)', input_string)
    if match:
        return match.group(1)
    
    # If no pattern matched, return as-is and let it fail with better error
    return input_string

def fetch_rows(sheets_service, sheet_id: str, range_name: str = None) -> Tuple[List[str], List[List[str]]]:
    """
    Fetch rows from Google Sheet.
    If range_name is None, fetches all data automatically.
    Returns (headers, data_rows).
    """
    try:
        if range_name is None:
            # Get sheet metadata to find the first sheet name
            sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            if not sheets:
                print("ERROR: No sheets found in the spreadsheet.")
                sys.exit(1)
            
            # Get the first sheet's title
            first_sheet_name = sheets[0]['properties']['title']
            print(f"📋 Using sheet: '{first_sheet_name}'")
            
            # Fetch all data from the first sheet
            range_name = first_sheet_name
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("ERROR: No data found in sheet.")
            sys.exit(1)
        
        headers = values[0]
        data_rows = values[1:] if len(values) > 1 else []
        
        return headers, data_rows
    
    except HttpError as error:
        print(f"ERROR fetching sheet data: {error}")
        if '404' in str(error):
            print("\nTroubleshooting:")
            print("1. Check that the Sheet ID is correct")
            print("2. Ensure the sheet is shared with your Google account")
            print("3. Verify you have at least 'Viewer' access to the sheet")
        sys.exit(1)

# ============================================================================
# VALIDATION
# ============================================================================

def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_row(row_dict: Dict[str, str], template_key: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a row has all required fields for the selected template.
    Returns (is_valid, error_reason).
    
    Special handling: Name can be provided as single field OR FirstName+LastName combined.
    """
    config = TEMPLATE_CONFIGS[template_key]
    
    # Check required fields
    for field in config['required_fields']:
        # Special case: Name might have been constructed from FirstName+LastName
        if field == 'Name':
            # Check if Name exists (either original or combined)
            if field not in row_dict or not row_dict[field].strip():
                # Also check if we have FirstName and LastName
                has_first = 'FirstName' in row_dict and row_dict['FirstName'].strip()
                has_last = 'LastName' in row_dict and row_dict['LastName'].strip()
                if not (has_first and has_last):
                    return False, f"Missing required field: {field} (or FirstName/LastName)"
        else:
            if field not in row_dict or not row_dict[field].strip():
                return False, f"Missing required field: {field}"
    
    # Validate email format
    email = row_dict.get('Email', '').strip()
    if not is_valid_email(email):
        return False, f"Invalid email format: {email}"
    
    # Template-specific validation
    if template_key == 'event':
        if not row_dict.get('RSVP_URL', '').strip():
            return False, "Missing RSVP_URL"
    
    return True, None

# ============================================================================
# CERTIFICATE GENERATION
# ============================================================================

def detect_horizontal_guideline(template_path: str, dark_threshold: int = 60, 
                                min_fraction: float = 0.4, search_margin: float = 0.15) -> Tuple[Optional[int], float]:
    """Detect a predominantly dark horizontal line near the middle of the template."""
    try:
        with Image.open(template_path) as img:
            gray = img.convert('L')
            width, height = gray.size
            pixels = gray.load()

            start_y = int(height * search_margin)
            end_y = int(height * (1 - search_margin))

            best_y = None
            best_fraction = 0.0

            for y in range(start_y, end_y):
                dark_pixels = sum(1 for x in range(width) if pixels[x, y] <= dark_threshold)
                fraction = dark_pixels / width

                if fraction > best_fraction:
                    best_fraction = fraction
                    best_y = y

            if best_y is not None and best_fraction >= min_fraction:
                return best_y, best_fraction

            return None, best_fraction
    except Exception:
        return None, 0.0


def generate_certificate(template_path: str, name: str, text_position: Optional[Tuple[int, int]], 
                        font_size: int = 80, font_color: str = '#000000', 
                        auto_position: bool = False, detected_line_y: Optional[int] = None,
                        vertical_offset: int = 0) -> BytesIO:
    """
    Generate a certificate by overlaying name on template image.
    Returns BytesIO object containing the PNG image.
    """
    if not PIL_AVAILABLE:
        raise ImportError("Pillow is required for certificate generation. Install with: pip install Pillow")
    
    # Open template image
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fall back to default if not available
    try:
        # Try common font paths
        font_paths = [
            "/usr/share/fonts/truetype/msttcorefonts/ScriptMTBold.ttf",
            "/usr/share/fonts/truetype/scriptmt/ScriptMTBold.ttf",
            "/usr/share/fonts/truetype/scriptmt/script.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/SCRIPTBL.TTF",
            "/Library/Fonts/ScriptMTBold.ttf",
            "/System/Library/Fonts/Supplemental/ScriptMTBold.ttf",
            "C:\\Windows\\Fonts\\SCRIPTBL.TTF",
            "C:\\Windows\\Fonts\\ScriptMTBold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\Arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Convert color hex to RGB
    if font_color.startswith('#'):
        font_color = font_color.lstrip('#')
        rgb_color = tuple(int(font_color[i:i+2], 16) for i in (0, 2, 4))
    else:
        rgb_color = (0, 0, 0)  # Default black
    
    # Prepare text metrics
    text = name.upper()

    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width, text_height = draw.textsize(text, font=font)

    text_x, text_y = 0, 0

    if auto_position:
        if detected_line_y is None:
            detected_line_y, _ = detect_horizontal_guideline(template_path)

        if detected_line_y is not None:
            text_x = max(0, (img.width - text_width) // 2)
            margin = max(5, text_height // 6)
            text_y = max(0, detected_line_y - text_height - margin)
        elif text_position:
            text_x, text_y = text_position
        else:
            text_x = max(0, (img.width - text_width) // 2)
            text_y = max(0, (img.height - text_height) // 2)
    else:
        if not text_position:
            raise ValueError("Manual text positioning selected but no coordinates were provided.")
        text_x, text_y = text_position

    text_y = max(0, min(img.height - text_height, text_y + vertical_offset))

    # Draw text (name in UPPERCASE)
    draw.text((text_x, text_y), text, fill=rgb_color, font=font)
    
    # Save to BytesIO
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    
    return output

# ============================================================================
# EMAIL RENDERING
# ============================================================================

def render_certificate_html(row_dict: Dict[str, str]) -> str:
    """Render thank-you HTML email with dynamic sections and defaults."""
    html = CERTIFICATE_HTML_TEMPLATE

    defaults = {
        'OrgName': 'IEEE BAU',
        'SupportEmail': 'IEEE.BAU.LB@gmail.com',
        'Year': str(datetime.now().year),
        'TeamOrSignerName': 'Mohamad Al Ghoush',
        'Title': ''
    }

    for key, default_value in defaults.items():
        if key not in row_dict or not str(row_dict[key]).strip():
            row_dict[key] = default_value

    # Backwards compatibility with previous column names
    if not str(row_dict.get('EventName', '')).strip() and str(row_dict.get('CourseTitle', '')).strip():
        row_dict['EventName'] = row_dict['CourseTitle'].strip()
    if not str(row_dict.get('EventDate', '')).strip() and str(row_dict.get('CompletionDate', '')).strip():
        row_dict['EventDate'] = row_dict['CompletionDate'].strip()

    event_name = str(row_dict.get('EventName', '')).strip()
    event_date = str(row_dict.get('EventDate', '')).strip()
    event_location = str(row_dict.get('EventLocation', '')).strip()
    org_name = row_dict.get('OrgName', 'our organization')

    if event_name and event_date:
        thank_you_message = (
            f"Thank you for attending <strong>{event_name}</strong> on <strong>{event_date}</strong>. "
            f"Your presence helped make the experience memorable for our community at {org_name}."
        )
    elif event_name:
        thank_you_message = (
            f"Thank you for attending <strong>{event_name}</strong>. "
            "We truly appreciated having you with us."
        )
    else:
        thank_you_message = (
            "Thank you for attending our recent gathering. We truly appreciated having you with us."
        )

    attachment_line = (
        "Your certificate of appreciation is attached to this email as a PNG image. "
        "Feel free to download, print, or share it as you wish."
    )

    # Event details card
    detail_lines: List[str] = []
    if event_name:
        detail_lines.append(
            f'<p style="margin: 0 0 8px; font-size: 14px; color: #4a5568; line-height: 1.6;">'
            f'<strong>Event:</strong> {event_name}</p>'
        )
    if event_date:
        detail_lines.append(
            f'<p style="margin: 0 0 8px; font-size: 14px; color: #4a5568; line-height: 1.6;">'
            f'<strong>Date:</strong> {event_date}</p>'
        )
    if event_location:
        detail_lines.append(
            f'<p style="margin: 0; font-size: 14px; color: #4a5568; line-height: 1.6;">'
            f'<strong>Location:</strong> {event_location}</p>'
        )

    if detail_lines:
        event_details_html = (
            '<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" '
            'style="background-color: #f7fafc; border-radius: 6px; margin-bottom: 30px;">'
            '<tr><td style="padding: 24px;">'
            '<p style="margin: 0 0 12px; font-size: 14px; color: #2d3748; font-weight: bold;">Event Highlights</p>'
            + ''.join(detail_lines) +
            '</td></tr></table>'
        )
    else:
        event_details_html = ''

    # Resources section
    resources_url = str(row_dict.get('ResourcesURL', '')).strip()
    resources_desc = str(row_dict.get('ResourcesDescription', '')).strip()
    if resources_url:
        resources_label = resources_desc or 'Access post-event resources'
        resources_html = (
            '<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" '
            'style="background-color: #edf2f7; border-radius: 6px; margin-bottom: 30px;">'
            '<tr><td style="padding: 24px; text-align: center;">'
            '<p style="margin: 0 0 8px; font-size: 16px; color: #2d3748;">📚 <strong>Keep exploring</strong></p>'
            f'<a href="{resources_url}" style="display: inline-block; margin-top: 12px; padding: 12px 32px; '
            'background-color: #2c5282; color: #ffffff; text-decoration: none; font-size: 15px; border-radius: 6px;">'
            f'{resources_label}</a>'
            '</td></tr></table>'
        )
    else:
        resources_html = ''

    # Feedback section
    feedback_url = str(row_dict.get('FeedbackURL', '')).strip()
    if feedback_url:
        feedback_html = (
            '<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" '
            'style="background-color: #fdf2f8; border-radius: 6px; margin-bottom: 30px;">'
            '<tr><td style="padding: 24px; text-align: center;">'
            '<p style="margin: 0 0 8px; font-size: 16px; color: #2d3748;">💬 <strong>Share your feedback</strong></p>'
            f'<a href="{feedback_url}" style="display: inline-block; margin-top: 12px; padding: 12px 32px; '
            'background-color: #d53f8c; color: #ffffff; text-decoration: none; font-size: 15px; border-radius: 6px;">'
            'Complete the feedback form</a>'
            '</td></tr></table>'
        )
    else:
        feedback_html = ''

    footer_parts = []
    if str(row_dict.get('OrgAddress', '')).strip():
        footer_parts.append(row_dict['OrgAddress'].strip())
    if str(row_dict.get('SupportEmail', '')).strip():
        footer_parts.append(row_dict['SupportEmail'].strip())
    if str(row_dict.get('OrgPhone', '')).strip():
        footer_parts.append(row_dict['OrgPhone'].strip())
    footer_contact = ' • '.join(footer_parts) if footer_parts else 'Stay connected with us'

    html = html.replace('{ThankYouMessage}', thank_you_message)
    html = html.replace('{AttachmentLine}', attachment_line)
    html = html.replace('{EventDetailsSection}', event_details_html)
    html = html.replace('{ResourcesSection}', resources_html)
    html = html.replace('{FeedbackSection}', feedback_html)
    html = html.replace('{FooterContact}', footer_contact)

    for key, value in row_dict.items():
        html = html.replace(f'{{{key}}}', str(value))

    return html

def render_certificate_text(row_dict: Dict[str, str]) -> str:
    """Render thank-you plain text email with defaults for missing fields."""
    text = CERTIFICATE_TEXT_TEMPLATE

    defaults = {
        'OrgName': 'IEEE BAU',
        'SupportEmail': 'IEEE.BAU.LB@gmail.com',
        'Year': str(datetime.now().year),
        'TeamOrSignerName': 'Mohamad Al Ghoush',
        'Title': ''
    }

    for key, default_value in defaults.items():
        if key not in row_dict or not str(row_dict[key]).strip():
            row_dict[key] = default_value

    # Backwards compatibility
    if not str(row_dict.get('EventName', '')).strip() and str(row_dict.get('CourseTitle', '')).strip():
        row_dict['EventName'] = row_dict['CourseTitle'].strip()
    if not str(row_dict.get('EventDate', '')).strip() and str(row_dict.get('CompletionDate', '')).strip():
        row_dict['EventDate'] = row_dict['CompletionDate'].strip()

    event_name = str(row_dict.get('EventName', '')).strip()
    event_date = str(row_dict.get('EventDate', '')).strip()
    event_location = str(row_dict.get('EventLocation', '')).strip()
    org_name = row_dict.get('OrgName', 'our organization')

    if event_name and event_date:
        thank_you_plain = (
            f"Thank you for attending {event_name} on {event_date}. "
            f"Your presence helped make the experience memorable for our community at {org_name}."
        )
    elif event_name:
        thank_you_plain = (
            f"Thank you for attending {event_name}. We truly appreciated having you with us."
        )
    else:
        thank_you_plain = (
            "Thank you for attending our recent gathering. We truly appreciated having you with us."
        )

    attachment_line_plain = (
        "Your certificate of appreciation is attached to this email as a PNG image. "
        "Feel free to download, print, or share it as you wish."
    )

    detail_lines: List[str] = []
    if event_name:
        detail_lines.append(f"Event: {event_name}")
    if event_date:
        detail_lines.append(f"Date: {event_date}")
    if event_location:
        detail_lines.append(f"Location: {event_location}")

    if detail_lines:
        event_details_block = "EVENT DETAILS\n" + "\n".join(detail_lines) + "\n\n"
    else:
        event_details_block = ""

    resources_url = str(row_dict.get('ResourcesURL', '')).strip()
    resources_desc = str(row_dict.get('ResourcesDescription', '')).strip()
    if resources_url:
        resources_label = resources_desc or 'Access post-event resources'
        resources_block = f"RESOURCES\n{resources_label}: {resources_url}\n\n"
    else:
        resources_block = ""

    feedback_url = str(row_dict.get('FeedbackURL', '')).strip()
    if feedback_url:
        feedback_block = f"FEEDBACK\nShare your thoughts: {feedback_url}\n\n"
    else:
        feedback_block = ""

    footer_parts = []
    if str(row_dict.get('OrgAddress', '')).strip():
        footer_parts.append(row_dict['OrgAddress'].strip())
    if str(row_dict.get('SupportEmail', '')).strip():
        footer_parts.append(row_dict['SupportEmail'].strip())
    if str(row_dict.get('OrgPhone', '')).strip():
        footer_parts.append(row_dict['OrgPhone'].strip())
    footer_contact = ' | '.join(footer_parts) if footer_parts else 'Stay connected with us'

    text = text.replace('{ThankYouMessagePlain}', thank_you_plain)
    text = text.replace('{AttachmentLinePlain}', attachment_line_plain)
    text = text.replace('{EventDetailsBlock}', event_details_block)
    text = text.replace('{ResourcesBlock}', resources_block)
    text = text.replace('{FeedbackBlock}', feedback_block)
    text = text.replace('{FooterContactText}', footer_contact)

    for key, value in row_dict.items():
        text = text.replace(f'{{{key}}}', str(value))

    return text

def render_event_html(row_dict: Dict[str, str]) -> str:
    """Render Event HTML with dynamic sections."""
    html = EVENT_HTML_TEMPLATE
    
    # Hero image section
    hero_section = ""
    if row_dict.get('HeroImageURL', '').strip():
        hero_section = f'''<tr>
            <td style="padding: 0;">
                <img src="{row_dict['HeroImageURL']}" alt="Event" style="width: 100%; height: auto; display: block; border-radius: 8px 8px 0 0;" />
            </td>
        </tr>'''
    
    # Outcomes section
    outcomes_html = ""
    outcome1 = row_dict.get('Outcome1', '').strip()
    outcome2 = row_dict.get('Outcome2', '').strip()
    if outcome1 or outcome2:
        outcomes_html = '<p style="margin: 0 0 12px; font-size: 16px; color: #2d3748; line-height: 1.6;"><strong>Key Outcomes:</strong></p><ul style="margin: 0 0 30px; padding-left: 24px; font-size: 16px; color: #2d3748; line-height: 1.8;">'
        if outcome1:
            outcomes_html += f'<li>{outcome1}</li>'
        if outcome2:
            outcomes_html += f'<li>{outcome2}</li>'
        outcomes_html += '</ul>'
    
    # Speakers section
    speakers_html = ""
    speaker1_name = row_dict.get('Speaker1Name', '').strip()
    speaker1_title = row_dict.get('Speaker1Title', '').strip()
    speaker2_name = row_dict.get('Speaker2Name', '').strip()
    speaker2_title = row_dict.get('Speaker2Title', '').strip()
    
    if speaker1_name or speaker2_name:
        speakers_html = '<p style="margin: 0 0 12px; font-size: 16px; color: #2d3748; line-height: 1.6;"><strong>Featured Speakers:</strong></p><ul style="margin: 0 0 30px; padding-left: 24px; font-size: 16px; color: #2d3748; line-height: 1.8;">'
        if speaker1_name:
            speakers_html += f'<li><strong>{speaker1_name}</strong>'
            if speaker1_title:
                speakers_html += f', {speaker1_title}'
            speakers_html += '</li>'
        if speaker2_name:
            speakers_html += f'<li><strong>{speaker2_name}</strong>'
            if speaker2_title:
                speakers_html += f', {speaker2_title}'
            speakers_html += '</li>'
        speakers_html += '</ul>'
    
    # Footer contact
    footer_parts = []
    if row_dict.get('OrgAddress', '').strip():
        footer_parts.append(row_dict['OrgAddress'])
    footer_parts.append(row_dict['SupportEmail'])
    footer_contact = ' • '.join(footer_parts)
    
    # Unsubscribe section
    unsubscribe_html = ""
    if row_dict.get('UnsubscribeURL', '').strip():
        unsubscribe_html = f'''<p style="margin: 0 0 12px; font-size: 12px; color: #a0aec0; line-height: 1.5; text-align: center;">
            <a href="{row_dict['UnsubscribeURL']}" style="color: #a0aec0; text-decoration: underline;">Unsubscribe from event invitations</a>
        </p>'''
    
    # Replace special sections
    html = html.replace('{HeroImageSection}', hero_section)
    html = html.replace('{OutcomesSection}', outcomes_html)
    html = html.replace('{SpeakersSection}', speakers_html)
    html = html.replace('{FooterContact}', footer_contact)
    html = html.replace('{UnsubscribeSection}', unsubscribe_html)
    
    # Replace all placeholders
    for key, value in row_dict.items():
        html = html.replace(f'{{{key}}}', str(value))
    
    return html

def render_event_text(row_dict: Dict[str, str]) -> str:
    """Render Event plain text."""
    text = EVENT_TEXT_TEMPLATE
    
    # Outcomes text
    outcomes_text = ""
    outcome1 = row_dict.get('Outcome1', '').strip()
    outcome2 = row_dict.get('Outcome2', '').strip()
    if outcome1 or outcome2:
        outcomes_text = "KEY OUTCOMES\n"
        if outcome1:
            outcomes_text += f"- {outcome1}\n"
        if outcome2:
            outcomes_text += f"- {outcome2}\n"
    
    # Speakers text
    speakers_text = ""
    speaker1_name = row_dict.get('Speaker1Name', '').strip()
    speaker1_title = row_dict.get('Speaker1Title', '').strip()
    speaker2_name = row_dict.get('Speaker2Name', '').strip()
    speaker2_title = row_dict.get('Speaker2Title', '').strip()
    
    if speaker1_name or speaker2_name:
        speakers_text = "FEATURED SPEAKERS\n"
        if speaker1_name:
            speakers_text += f"- {speaker1_name}"
            if speaker1_title:
                speakers_text += f", {speaker1_title}"
            speakers_text += "\n"
        if speaker2_name:
            speakers_text += f"- {speaker2_name}"
            if speaker2_title:
                speakers_text += f", {speaker2_title}"
            speakers_text += "\n"
    
    # Footer contact
    footer_parts = []
    if row_dict.get('OrgAddress', '').strip():
        footer_parts.append(row_dict['OrgAddress'])
    footer_parts.append(row_dict['SupportEmail'])
    footer_contact = ' | '.join(footer_parts)
    
    # Unsubscribe text
    unsubscribe_text = ""
    if row_dict.get('UnsubscribeURL', '').strip():
        unsubscribe_text = f"Unsubscribe: {row_dict['UnsubscribeURL']}"
    
    text = text.replace('{OutcomesText}', outcomes_text)
    text = text.replace('{SpeakersText}', speakers_text)
    text = text.replace('{FooterContactText}', footer_contact)
    text = text.replace('{UnsubscribeText}', unsubscribe_text)
    
    # Replace all placeholders
    for key, value in row_dict.items():
        text = text.replace(f'{{{key}}}', str(value))
    
    return text

def render_email(row_dict: Dict[str, str], template_key: str) -> Tuple[str, str]:
    """
    Render email HTML and plain text for the given template.
    Returns (html_body, text_body).
    """
    if template_key == 'certificate':
        return render_certificate_html(row_dict), render_certificate_text(row_dict)
    else:
        return render_event_html(row_dict), render_event_text(row_dict)

def render_subject(row_dict: Dict[str, str], template_key: str, custom_subject: Optional[str] = None) -> str:
    """Render email subject with placeholders."""
    if custom_subject:
        subject = custom_subject
    else:
        subject = TEMPLATE_CONFIGS[template_key]['subject_default']

        if template_key == 'certificate':
            event_name = str(row_dict.get('EventName', '')).strip()
            if not event_name:
                event_name = str(row_dict.get('CourseTitle', '')).strip()
            if event_name:
                subject = f"Thank You for Attending {event_name}"
    
    # Replace placeholders
    for key, value in row_dict.items():
        subject = subject.replace(f'{{{key}}}', str(value))
    
    return subject

# ============================================================================
# GMAIL
# ============================================================================

def build_message(to: str, subject: str, html_body: str, text_body: str, 
                 from_address: Optional[str] = None, attachment: Optional[BytesIO] = None,
                 attachment_filename: str = "certificate.png") -> Dict:
    """Build a MIME message for Gmail API with optional attachment."""
    message = MIMEMultipart('mixed') if attachment else MIMEMultipart('alternative')
    message['To'] = to
    message['Subject'] = subject
    if from_address:
        message['From'] = from_address
    
    # Create message body part
    if attachment:
        body_part = MIMEMultipart('alternative')
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        body_part.attach(part1)
        body_part.attach(part2)
        message.attach(body_part)
        
        # Attach certificate image
        img = MIMEImage(attachment.read(), name=attachment_filename)
        img.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
        message.attach(img)
    else:
        # No attachment, just text and HTML
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        message.attach(part1)
        message.attach(part2)
    
    # Encode for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_gmail(gmail_service, message: Dict, user_id: str = 'me') -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Send email via Gmail API.
    Returns (success, message_id, error).
    """
    try:
        sent_message = gmail_service.users().messages().send(
            userId=user_id,
            body=message
        ).execute()
        return True, sent_message['id'], None
    except HttpError as error:
        return False, None, str(error)

# ============================================================================
# LOGGING
# ============================================================================

def init_log(log_path: str):
    """Initialize CSV log file with headers."""
    with open(log_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Email', 'Subject', 'Status', 'MessageId', 'Error', 'Timestamp', 'TemplateUsed'])

def log_result(log_path: str, email: str, subject: str, status: str, 
               message_id: Optional[str], error: Optional[str], template_key: str):
    """Append a result to the CSV log."""
    timestamp = datetime.now().isoformat()
    with open(log_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email, subject, status, message_id or '', error or '', timestamp, template_key])

# ============================================================================
# INTERACTIVE PROMPTS
# ============================================================================

def prompt_sheet_info() -> str:
    """Prompt for Google Sheet URL or ID."""
    print("=== Google Sheet Configuration ===")
    print("You can paste:")
    print("  • Full Google Sheets URL")
    print("  • Just the Sheet ID")
    print()
    
    user_input = input("Enter Google Sheet URL or ID: ").strip()
    
    if not user_input:
        print("ERROR: Sheet URL/ID cannot be empty")
        sys.exit(1)
    
    # Extract ID from URL if needed
    sheet_id = extract_sheet_id(user_input)
    
    # Show what was extracted
    if sheet_id != user_input:
        print(f"✓ Extracted Sheet ID: {sheet_id}")
    
    print()
    return sheet_id

def prompt_template_selection() -> str:
    """Prompt for template selection."""
    print("=== Template Selection ===")
    print("1. Certificate Delivery")
    print("2. Upcoming Event Invitation")
    choice = input("Choose template (1 or 2): ").strip()
    print()
    
    if choice == '1':
        return 'certificate'
    elif choice == '2':
        return 'event'
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

def prompt_column_mapping(headers: List[str], template_key: str) -> Dict[str, int]:
    """
    Prompt user to map required fields to column indices.
    Returns a mapping of field_name -> column_index.
    
    Special handling for Name field:
    - Accepts either "Name" OR "FirstName"+"LastName"
    - Auto-detects and combines if split
    """
    config = TEMPLATE_CONFIGS[template_key]
    all_fields = config['required_fields'] + config['optional_fields']
    
    print(f"=== Column Mapping for {config['name']} ===")
    print(f"Available columns: {', '.join(headers)}")
    print()
    
    mapping = {}
    
    # Special handling for Name field
    # Check if we have FirstName and LastName instead of Name
    has_firstname = any(h.lower() in ['firstname', 'first name', 'first_name'] for h in headers)
    has_lastname = any(h.lower() in ['lastname', 'last name', 'last_name'] for h in headers)
    has_name = any(h.lower() == 'name' for h in headers)
    
    if not has_name and has_firstname and has_lastname:
        print("✓ Detected FirstName and LastName columns - will combine them automatically")
        # Find the indices
        for idx, header in enumerate(headers):
            if header.lower() in ['firstname', 'first name', 'first_name']:
                mapping['FirstName'] = idx
            elif header.lower() in ['lastname', 'last name', 'last_name']:
                mapping['LastName'] = idx
        print()
    
    # Auto-detect and suggest mappings
    for field in all_fields:
        # Skip Name if we're using FirstName/LastName
        if field == 'Name' and 'FirstName' in mapping and 'LastName' in mapping:
            continue
            
        # Try to find exact match (case-insensitive)
        suggested_idx = None
        for idx, header in enumerate(headers):
            if header.lower() == field.lower():
                suggested_idx = idx
                break
        
        is_required = field in config['required_fields']
        req_label = "[REQUIRED]" if is_required else "[Optional]"
        
        if suggested_idx is not None:
            prompt_text = f"{req_label} Map '{field}' (suggested: {headers[suggested_idx]}): "
            response = input(prompt_text).strip()
            if not response:
                mapping[field] = suggested_idx
            else:
                try:
                    mapping[field] = int(response)
                except ValueError:
                    # Try to find by column name
                    for idx, header in enumerate(headers):
                        if header.lower() == response.lower():
                            mapping[field] = idx
                            break
        else:
            if is_required and field != 'Name':  # Name might be split
                prompt_text = f"{req_label} Map '{field}' (column index or name): "
                response = input(prompt_text).strip()
                if response:
                    try:
                        mapping[field] = int(response)
                    except ValueError:
                        for idx, header in enumerate(headers):
                            if header.lower() == response.lower():
                                mapping[field] = idx
                                break
            elif is_required and field == 'Name':
                # Prompt for Name alternatives
                if 'FirstName' not in mapping:
                    prompt_text = f"{req_label} Map '{field}' (or enter 'FirstName' and 'LastName' separately): "
                    response = input(prompt_text).strip()
                    if response:
                        try:
                            mapping[field] = int(response)
                        except ValueError:
                            for idx, header in enumerate(headers):
                                if header.lower() == response.lower():
                                    mapping[field] = idx
                                    break
    
    print()
    return mapping

def prompt_certificate_config() -> Dict:
    """Prompt for certificate template configuration."""
    print("=== Certificate Configuration ===")
    print("The script will generate personalized certificates by adding each person's")
    print("name (in CAPITALS) to your certificate template image.")
    print()
    
    # Get template path
    template_path = input("Enter path to certificate template image (PNG): ").strip()
    
    if not template_path or not os.path.exists(template_path):
        print(f"✗ Error: Template file not found: {template_path}")
        print("Please provide a valid PNG file path.")
        sys.exit(1)
    
    print(f"✓ Template found: {template_path}")
    print()

    auto_detect_input = input("Auto-detect name position from template? (Y/n): ").strip().lower()
    auto_position = auto_detect_input != 'n'
    detected_line_y = None
    coverage = 0.0

    if auto_position:
        detected_line_y, coverage = detect_horizontal_guideline(template_path)
        if detected_line_y is not None:
            print(f"✓ Detected horizontal guideline at Y={detected_line_y} (coverage {coverage:.0%})")
        else:
            print("⚠ Could not detect a clear horizontal guideline. Falling back to manual input.")
            auto_position = False

    text_position = None

    if not auto_position:
        print("Where should the name be placed on the certificate?")
        print("Enter X and Y coordinates (in pixels from top-left corner)")
        print("Example: If name should be at center-ish, try X=400 Y=600")
        print()

        x_pos = input("X position (default: 400): ").strip()
        y_pos = input("Y position (default: 600): ").strip()

        x_val = int(x_pos) if x_pos else 400
        y_val = int(y_pos) if y_pos else 600
        text_position = (x_val, y_val)
    
    vertical_offset_input = input("Vertical offset to adjust name placement (positive = down, negative = up, default: 0): ").strip()
    vertical_offset = int(vertical_offset_input) if vertical_offset_input else 0

    print()
    
    # Get font size
    font_size_input = input("Font size (default: 80): ").strip()
    font_size = int(font_size_input) if font_size_input else 80
    
    # Get font color
    print()
    font_color = input("Font color in hex (default: #000000 for black): ").strip() or "#000000"
    
    print()
    print("✓ Configuration:")
    print(f"  Template: {template_path}")
    if auto_position and detected_line_y is not None:
        print(f"  Auto Position: Placing name above line at Y={detected_line_y} (coverage {coverage:.0%})")
    elif auto_position:
        print("  Auto Position: Enabled (fallback to center)")
    else:
        print(f"  Position: {text_position}")
    if vertical_offset:
        print(f"  Vertical Offset: {vertical_offset}")
    print(f"  Font Size: {font_size}")
    print(f"  Color: {font_color}")
    print()
    
    return {
        'template_path': template_path,
        'text_position': text_position,
        'font_size': font_size,
        'font_color': font_color,
        'auto_position': auto_position,
        'detected_line_y': detected_line_y,
        'vertical_offset': vertical_offset
    }

def prompt_options() -> Dict:
    """Prompt for send options."""
    print("=== Send Options ===")
    
    dry_run_input = input("Dry-run mode? (Y/n): ").strip().lower()
    dry_run = dry_run_input != 'n'
    
    throttle_input = input("Throttle seconds between sends (default: 0.8): ").strip()
    throttle = float(throttle_input) if throttle_input else 0.8
    
    from_address = input("From address override (blank for 'me'): ").strip() or None
    
    filter_email = input("Filter to only this email (blank for all): ").strip() or None
    
    log_path = input("CSV log path (default: send_log.csv): ").strip() or "send_log.csv"
    
    custom_subject = input("Custom subject line (blank for default, use {placeholders}): ").strip() or None
    
    print()
    
    return {
        'dry_run': dry_run,
        'throttle': throttle,
        'from_address': from_address,
        'filter_email': filter_email,
        'log_path': log_path,
        'custom_subject': custom_subject
    }

def preview_messages(rows_data: List[Dict[str, str]], template_key: str, 
                    custom_subject: Optional[str] = None, max_preview: int = 3):
    """Preview sample messages."""
    print("=== Message Preview ===")
    
    for i, row_dict in enumerate(rows_data[:max_preview]):
        is_valid, error = validate_row(row_dict, template_key)
        if not is_valid:
            continue
        
        to_email = row_dict.get('Email', 'N/A')
        subject = render_subject(row_dict, template_key, custom_subject)
        html_body, text_body = render_email(row_dict, template_key)
        
        print(f"\n--- Sample {i+1} ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body (first 200 chars): {text_body[:200]}...")
        
        # Show key links
        if template_key == 'event':
            rsvp = row_dict.get('RSVP_URL', 'N/A')
            print(f"RSVP Link: {rsvp}")
    
    print()

def confirm_send() -> bool:
    """Confirm before sending."""
    response = input("Proceed with sending? (Y/n): ").strip().lower()
    print()
    return response != 'n'

# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def main():
    """Main execution flow."""
    print("=" * 70)
    print("FORMAL EMAIL MAILER WITH DUAL TEMPLATES")
    print("=" * 70)
    print()
    
    # Step 1: Authenticate
    print("Step 1: Authentication")
    sheets_service, gmail_service = authorize()
    
    # Step 2: Get sheet info
    print("Step 2: Sheet Configuration")
    sheet_id = prompt_sheet_info()
    
    # Step 3: Fetch data (auto-detects first sheet and fetches all data)
    print("Step 3: Fetching data from sheet...")
    headers, data_rows = fetch_rows(sheets_service, sheet_id, None)
    print(f"✓ Fetched {len(data_rows)} rows with {len(headers)} columns\n")
    
    # Step 4: Select template
    print("Step 4: Template Selection")
    template_key = prompt_template_selection()
    
    # Step 5: Column mapping
    print("Step 5: Column Mapping")
    field_mapping = prompt_column_mapping(headers, template_key)
    
    # Step 5.5: Get certificate configuration for certificate template
    cert_config = None
    if template_key == 'certificate':
        print("Step 5.5: Certificate Configuration")
        cert_config = prompt_certificate_config()
    
    # Convert rows to dictionaries
    rows_data = []
    for row in data_rows:
        row_dict = {}
        for field, col_idx in field_mapping.items():
            if col_idx < len(row):
                row_dict[field] = row[col_idx].strip()
            else:
                row_dict[field] = ''
        
        # Combine FirstName and LastName into Name if needed
        if 'FirstName' in row_dict and 'LastName' in row_dict and 'Name' not in row_dict:
            first = row_dict.get('FirstName', '').strip()
            last = row_dict.get('LastName', '').strip()
            row_dict['Name'] = f"{first} {last}".strip()
        
        rows_data.append(row_dict)
    
    # Step 6: Options
    print("Step 6: Configuration")
    options = prompt_options()
    
    # Filter by email if specified
    if options['filter_email']:
        rows_data = [r for r in rows_data if r.get('Email', '').lower() == options['filter_email'].lower()]
        print(f"Filtered to {len(rows_data)} rows matching {options['filter_email']}\n")
    
    # Step 7: Preview
    print("Step 7: Preview")
    preview_messages(rows_data, template_key, options['custom_subject'])
    
    # Step 8: Confirm
    print("Step 8: Confirmation")
    if not confirm_send():
        print("Operation cancelled by user.")
        sys.exit(0)
    
    # Step 9: Send
    print("Step 9: Sending emails")
    print("-" * 70)
    
    # Initialize log
    init_log(options['log_path'])
    
    # Counters
    counts = {'sent': 0, 'failed': 0, 'skipped': 0, 'dry_run': 0}
    
    for idx, row_dict in enumerate(rows_data, 1):
        email = row_dict.get('Email', '').strip()
        
        # Validate
        is_valid, error_reason = validate_row(row_dict, template_key)
        if not is_valid:
            print(f"[{idx}/{len(rows_data)}] SKIPPED {email}: {error_reason}")
            log_result(options['log_path'], email, '', 'SKIPPED', None, error_reason, template_key)
            counts['skipped'] += 1
            continue
        
        # Render
        subject = render_subject(row_dict, template_key, options['custom_subject'])
        html_body, text_body = render_email(row_dict, template_key)
        
        # Generate certificate if needed
        certificate_attachment = None
        if template_key == 'certificate' and cert_config:
            try:
                name = row_dict.get('Name', 'Unknown')
                certificate_attachment = generate_certificate(
                    cert_config['template_path'],
                    name,
                    cert_config.get('text_position'),
                    cert_config['font_size'],
                    cert_config['font_color'],
                    auto_position=cert_config.get('auto_position', False),
                    detected_line_y=cert_config.get('detected_line_y'),
                    vertical_offset=cert_config.get('vertical_offset', 0)
                )
                attachment_filename = f"certificate_{name.upper().replace(' ', '_')}.png"
            except Exception as e:
                print(f"⚠ Warning: Could not generate certificate for {name}: {e}")
                attachment_filename = "certificate.png"
        else:
            attachment_filename = "certificate.png"
        
        # Build message
        message = build_message(email, subject, html_body, text_body, options['from_address'], 
                               certificate_attachment, attachment_filename)
        
        # Send or dry-run
        if options['dry_run']:
            print(f"[{idx}/{len(rows_data)}] DRY-RUN {email}: {subject[:50]}...")
            log_result(options['log_path'], email, subject, 'DRY-RUN', None, None, template_key)
            counts['dry_run'] += 1
        else:
            success, message_id, error = send_gmail(gmail_service, message)
            if success:
                print(f"[{idx}/{len(rows_data)}] SENT {email}: {subject[:50]}...")
                log_result(options['log_path'], email, subject, 'SENT', message_id, None, template_key)
                counts['sent'] += 1
            else:
                print(f"[{idx}/{len(rows_data)}] FAILED {email}: {error}")
                log_result(options['log_path'], email, subject, 'FAILED', None, error, template_key)
                counts['failed'] += 1
        
        # Throttle
        if idx < len(rows_data):
            time.sleep(options['throttle'])
    
    # Step 10: Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Rows Processed: {len(rows_data)}")
    if options['dry_run']:
        print(f"Dry-Run: {counts['dry_run']}")
    else:
        print(f"Sent: {counts['sent']}")
        print(f"Failed: {counts['failed']}")
    print(f"Skipped: {counts['skipped']}")
    print(f"Log saved to: {options['log_path']}")
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

