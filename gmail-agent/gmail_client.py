import os
import json
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core.client_options import ClientOptions
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'


def get_authenticated_service():
    """Authenticate and return Gmail API service."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"[ERROR] {CREDENTIALS_FILE} not found.\n"
                    "Please download it from Google Cloud Console:\n"
                    "1. Go to https://console.cloud.google.com\n"
                    "2. Create a project and enable Gmail API\n"
                    "3. Create OAuth 2.0 credentials (Desktop app)\n"
                    "4. Download and save as credentials.json in this directory"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def fetch_recent_emails(service, hours=24, max_results=50):
    """Fetch emails from the last N hours."""
    try:
        query = f'newer_than:{hours}h in:inbox'
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return []

        emails = []
        for msg in messages:
            try:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

                snippet = msg_data.get('snippet', '')[:200]

                emails.append({
                    'id': msg['id'],
                    'from': sender,
                    'subject': subject,
                    'snippet': snippet,
                    'date': date,
                    'is_unread': 'UNREAD' in msg_data.get('labelIds', [])
                })
            except Exception as e:
                print(f"[WARN] Error processing message {msg['id']}: {e}")
                continue

        return emails

    except Exception as e:
        print(f"[ERROR] Error fetching emails: {e}")
        raise


if __name__ == '__main__':
    try:
        service = get_authenticated_service()
        emails = fetch_recent_emails(service)
        print(f"[OK] Fetched {len(emails)} emails")
        for email in emails[:3]:
            print(f"  - {email['from']}: {email['subject']}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
