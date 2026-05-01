import os
import imaplib
import email
from datetime import datetime, timedelta
from pathlib import Path

YAHOO_IMAP_HOST = 'imap.mail.yahoo.com'
YAHOO_IMAP_PORT = 993


def load_yahoo_credentials():
    """Load Yahoo email and password from .env file."""
    yahoo_email = os.environ.get('YAHOO_EMAIL')
    yahoo_password = os.environ.get('YAHOO_PASSWORD')

    if not yahoo_email or not yahoo_password:
        # Try reading from .env file
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith('YAHOO_EMAIL='):
                        yahoo_email = line.split('=', 1)[1].strip()
                    elif line.startswith('YAHOO_PASSWORD='):
                        yahoo_password = line.split('=', 1)[1].strip()

    if not yahoo_email or not yahoo_password:
        raise ValueError(
            "[ERROR] Yahoo credentials not found.\n"
            "Set YAHOO_EMAIL and YAHOO_PASSWORD in .env:\n"
            "YAHOO_EMAIL=youremail@bellsouth.net\n"
            "YAHOO_PASSWORD=your-regular-password"
        )

    return yahoo_email, yahoo_password


def get_authenticated_service():
    """Authenticate with Yahoo IMAP and return connection."""
    try:
        yahoo_email, yahoo_password = load_yahoo_credentials()

        conn = imaplib.IMAP4_SSL(YAHOO_IMAP_HOST, YAHOO_IMAP_PORT)
        conn.login(yahoo_email, yahoo_password)

        return conn

    except imaplib.IMAP4.error as e:
        raise ValueError(
            f"[ERROR] Failed to connect to Yahoo IMAP: {e}\n"
            "Check that:\n"
            "1. YAHOO_EMAIL is correct\n"
            "2. YAHOO_APP_PASSWORD is valid (not your regular password)\n"
            "3. App Password is for 'Mail' application"
        )
    except Exception as e:
        raise ValueError(f"[ERROR] Yahoo IMAP auth failed: {e}")


def fetch_recent_emails(service, hours=24, max_results=50):
    """Fetch recent emails from Yahoo IMAP."""
    try:
        # Select INBOX
        service.select('INBOX')

        # Calculate cutoff date (RFC 2822 format)
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff.strftime('%d-%b-%Y')

        # Search for emails since cutoff date
        status, msg_ids = service.search(None, f'SINCE {cutoff_str}')

        if status != 'OK':
            return []

        # Get message IDs
        msg_list = msg_ids[0].split()[-max_results:]  # Limit to max_results, get newest

        if not msg_list:
            return []

        emails = []

        for msg_id in msg_list:
            try:
                # Fetch the full message
                status, msg_data = service.fetch(msg_id, '(RFC822)')

                if status != 'OK':
                    continue

                msg_bytes = msg_data[0][1]
                msg_obj = email.message_from_bytes(msg_bytes)

                # Extract headers
                subject = msg_obj.get('Subject', 'No Subject')
                from_addr = msg_obj.get('From', 'Unknown')
                date = msg_obj.get('Date', '')

                # Extract plaintext snippet
                snippet = _extract_snippet(msg_obj)

                # Check if unread (absence of \Seen flag)
                status, flags = service.fetch(msg_id, '(FLAGS)')
                is_unread = False
                if status == 'OK' and flags:
                    flags_str = flags[0].decode() if isinstance(flags[0], bytes) else flags[0]
                    is_unread = b'\\Seen' not in flags[0] if isinstance(flags[0], bytes) else '\\Seen' not in flags_str

                emails.append({
                    'id': msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                    'from': from_addr,
                    'subject': subject,
                    'snippet': snippet[:200],
                    'date': date,
                    'is_unread': is_unread,
                    'source': 'Yahoo'
                })

            except Exception as e:
                print(f"[WARN] Error processing Yahoo message {msg_id}: {e}")
                continue

        return emails

    except Exception as e:
        print(f"[ERROR] Error fetching Yahoo emails: {e}")
        raise


def _extract_snippet(msg_obj):
    """Extract plaintext snippet from email message."""
    snippet = ''

    # Try to get plaintext part
    if msg_obj.is_multipart():
        for part in msg_obj.walk():
            if part.get_content_type() == 'text/plain':
                try:
                    snippet = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                except:
                    continue
    else:
        try:
            snippet = msg_obj.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            snippet = msg_obj.get_payload()

    # Clean up snippet
    snippet = snippet.replace('\r\n', ' ').replace('\n', ' ').strip()

    return snippet


if __name__ == '__main__':
    try:
        conn = get_authenticated_service()
        emails = fetch_recent_emails(conn, hours=24, max_results=10)
        print(f"[OK] Fetched {len(emails)} Yahoo emails")
        for email_data in emails[:3]:
            print(f"  - {email_data['from']}: {email_data['subject']}")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Error: {e}")
