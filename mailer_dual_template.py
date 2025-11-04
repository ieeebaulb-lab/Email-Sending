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
from typing import Dict, List, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
    <title>Certificate of Completion</title>
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
                            <p style="margin: 8px 0 0; font-size: 14px; color: #718096;">Certificate Delivery</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 20px; font-size: 16px; color: #2d3748; line-height: 1.6;">Dear {Name},</p>
                            
                            <p style="margin: 0 0 20px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                Congratulations on successfully completing <strong>{CourseTitle}</strong> on <strong>{CompletionDate}</strong>. 
                                We are pleased to confirm your achievement and provide your official certificate of completion.
                            </p>
                            
                            <p style="margin: 0 0 30px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                Your certificate is securely hosted and accessible via the link below:
                            </p>
                            
                            <!-- Certificate Button -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td align="center" style="padding: 0 0 30px;">
                                        <a href="{CertificateDriveLink}" 
                                           style="display: inline-block; padding: 16px 48px; background-color: #2c5282; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 6px; border: none;">
                                            View Certificate
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding: 0 0 30px;">
                                        <p style="margin: 0; font-size: 14px; color: #718096;">
                                            If the button does not work, copy this link:<br>
                                            <a href="{CertificateDriveLink}" style="color: #2c5282; word-break: break-all;">{CertificateDriveLink}</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Verification Details -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f7fafc; border-radius: 6px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 24px;">
                                        <p style="margin: 0 0 12px; font-size: 14px; color: #2d3748; font-weight: bold;">Certificate Details</p>
                                        <p style="margin: 0 0 8px; font-size: 14px; color: #4a5568; line-height: 1.6;">
                                            <strong>Certificate ID:</strong> {CertificateID}
                                        </p>
                                        <p style="margin: 0 0 8px; font-size: 14px; color: #4a5568; line-height: 1.6;">
                                            <strong>Issued by:</strong> {OrgName}
                                        </p>
                                        <p style="margin: 0 0 8px; font-size: 14px; color: #4a5568; line-height: 1.6;">
                                            <strong>Completion Date:</strong> {CompletionDate}
                                        </p>
                                        {VerificationSection}
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 20px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                <strong>Next Steps:</strong>
                            </p>
                            <ul style="margin: 0 0 30px; padding-left: 24px; font-size: 16px; color: #2d3748; line-height: 1.8;">
                                <li>Download and save your certificate for your records</li>
                                <li>Add this achievement to your professional profile (LinkedIn, resume, etc.)</li>
                                <li>Request a printed copy if needed by contacting our support team</li>
                            </ul>
                            
                            <p style="margin: 0 0 8px; font-size: 16px; color: #2d3748; line-height: 1.6;">
                                Should you have any questions or require assistance, please contact us at 
                                <a href="mailto:{SupportEmail}" style="color: #2c5282; text-decoration: none;">{SupportEmail}</a>.
                            </p>
                            
                            <p style="margin: 30px 0 8px; font-size: 16px; color: #2d3748; line-height: 1.6;">Kind regards,</p>
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
                                This message and certificate link are intended for {Name}. Please do not share without consent.
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
Certificate Delivery

Dear {Name},

Congratulations on successfully completing {CourseTitle} on {CompletionDate}. We are pleased to confirm your achievement and provide your official certificate of completion.

Your certificate is securely hosted and accessible via the following link:
{CertificateDriveLink}

CERTIFICATE DETAILS
Certificate ID: {CertificateID}
Issued by: {OrgName}
Completion Date: {CompletionDate}
{VerificationText}

NEXT STEPS
- Download and save your certificate for your records
- Add this achievement to your professional profile (LinkedIn, resume, etc.)
- Request a printed copy if needed by contacting our support team

Should you have any questions or require assistance, please contact us at {SupportEmail}.

Kind regards,
{TeamOrSignerName}
{Title}
{OrgName}

---
{FooterContactText}
This message and certificate link are intended for {Name}. Please do not share without consent.

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
        'name': 'Certificate Delivery',
        'html_template': CERTIFICATE_HTML_TEMPLATE,
        'text_template': CERTIFICATE_TEXT_TEMPLATE,
        'subject_default': 'Certificate of Completion — {CourseTitle}',
        'required_fields': ['Name', 'Email', 'CourseTitle', 'CompletionDate', 
                           'CertificateDriveLink', 'CertificateID', 'OrgName', 
                           'SupportEmail', 'Year'],
        'optional_fields': ['VerificationURL', 'OrgAddress', 'OrgPhone', 
                           'TeamOrSignerName', 'Title']
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

def fetch_rows(sheets_service, sheet_id: str, range_name: str) -> Tuple[List[str], List[List[str]]]:
    """
    Fetch rows from Google Sheet.
    Returns (headers, data_rows).
    """
    try:
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
    """
    config = TEMPLATE_CONFIGS[template_key]
    
    # Check required fields
    for field in config['required_fields']:
        if field not in row_dict or not row_dict[field].strip():
            return False, f"Missing required field: {field}"
    
    # Validate email format
    email = row_dict.get('Email', '').strip()
    if not is_valid_email(email):
        return False, f"Invalid email format: {email}"
    
    # Template-specific validation
    if template_key == 'certificate':
        if not row_dict.get('CertificateDriveLink', '').strip():
            return False, "Missing CertificateDriveLink"
    
    elif template_key == 'event':
        if not row_dict.get('RSVP_URL', '').strip():
            return False, "Missing RSVP_URL"
    
    return True, None

# ============================================================================
# EMAIL RENDERING
# ============================================================================

def render_certificate_html(row_dict: Dict[str, str]) -> str:
    """Render Certificate HTML with dynamic sections."""
    html = CERTIFICATE_HTML_TEMPLATE
    
    # Verification section
    verification_html = ""
    if row_dict.get('VerificationURL', '').strip():
        verification_html = f'''<p style="margin: 0; font-size: 14px; color: #4a5568; line-height: 1.6;">
            <strong>Verify at:</strong> <a href="{row_dict['VerificationURL']}" style="color: #2c5282;">{row_dict['VerificationURL']}</a>
        </p>'''
    
    # Footer contact
    footer_parts = []
    if row_dict.get('OrgAddress', '').strip():
        footer_parts.append(row_dict['OrgAddress'])
    footer_parts.append(row_dict['SupportEmail'])
    if row_dict.get('OrgPhone', '').strip():
        footer_parts.append(row_dict['OrgPhone'])
    footer_contact = ' • '.join(footer_parts)
    
    # Replace special sections
    html = html.replace('{VerificationSection}', verification_html)
    html = html.replace('{FooterContact}', footer_contact)
    
    # Replace all placeholders
    for key, value in row_dict.items():
        html = html.replace(f'{{{key}}}', str(value))
    
    return html

def render_certificate_text(row_dict: Dict[str, str]) -> str:
    """Render Certificate plain text."""
    text = CERTIFICATE_TEXT_TEMPLATE
    
    # Verification text
    verification_text = ""
    if row_dict.get('VerificationURL', '').strip():
        verification_text = f"Verify at: {row_dict['VerificationURL']}"
    
    # Footer contact
    footer_parts = []
    if row_dict.get('OrgAddress', '').strip():
        footer_parts.append(row_dict['OrgAddress'])
    footer_parts.append(row_dict['SupportEmail'])
    if row_dict.get('OrgPhone', '').strip():
        footer_parts.append(row_dict['OrgPhone'])
    footer_contact = ' | '.join(footer_parts)
    
    text = text.replace('{VerificationText}', verification_text)
    text = text.replace('{FooterContactText}', footer_contact)
    
    # Replace all placeholders
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
    
    # Replace placeholders
    for key, value in row_dict.items():
        subject = subject.replace(f'{{{key}}}', str(value))
    
    return subject

# ============================================================================
# GMAIL
# ============================================================================

def build_message(to: str, subject: str, html_body: str, text_body: str, 
                 from_address: Optional[str] = None) -> Dict:
    """Build a MIME message for Gmail API."""
    message = MIMEMultipart('alternative')
    message['To'] = to
    message['Subject'] = subject
    if from_address:
        message['From'] = from_address
    
    # Attach plain text and HTML parts
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

def prompt_sheet_info() -> Tuple[str, str]:
    """Prompt for Google Sheet ID and range."""
    print("=== Google Sheet Configuration ===")
    sheet_id = input("Enter Google Sheet ID (from URL between /d/ and /edit): ").strip()
    range_name = input("Enter range (default: Sheet1!A1:Z1000): ").strip() or "Sheet1!A1:Z1000"
    print()
    return sheet_id, range_name

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
    """
    config = TEMPLATE_CONFIGS[template_key]
    all_fields = config['required_fields'] + config['optional_fields']
    
    print(f"=== Column Mapping for {config['name']} ===")
    print(f"Available columns: {', '.join(headers)}")
    print()
    
    mapping = {}
    
    # Auto-detect and suggest mappings
    for field in all_fields:
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
            if is_required:
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
    
    print()
    return mapping

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
        if template_key == 'certificate':
            link = row_dict.get('CertificateDriveLink', 'N/A')
            print(f"Certificate Link: {link}")
        else:
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
    sheet_id, range_name = prompt_sheet_info()
    
    # Step 3: Fetch data
    print("Step 3: Fetching data from sheet...")
    headers, data_rows = fetch_rows(sheets_service, sheet_id, range_name)
    print(f"✓ Fetched {len(data_rows)} rows with {len(headers)} columns\n")
    
    # Step 4: Select template
    print("Step 4: Template Selection")
    template_key = prompt_template_selection()
    
    # Step 5: Column mapping
    print("Step 5: Column Mapping")
    field_mapping = prompt_column_mapping(headers, template_key)
    
    # Convert rows to dictionaries
    rows_data = []
    for row in data_rows:
        row_dict = {}
        for field, col_idx in field_mapping.items():
            if col_idx < len(row):
                row_dict[field] = row[col_idx].strip()
            else:
                row_dict[field] = ''
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
        
        # Build message
        message = build_message(email, subject, html_body, text_body, options['from_address'])
        
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

