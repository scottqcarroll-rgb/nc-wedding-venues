#!/usr/bin/env python3
"""
Unified Email Agent
Fetches emails from Gmail and/or Yahoo Mail, classifies them with Claude,
and generates an HTML dashboard. Flexible provider support via --gmail and --yahoo flags.
"""

import os
import json
import sys
import webbrowser
from datetime import datetime

from gmail_client import get_authenticated_service as get_gmail_service, fetch_recent_emails as fetch_gmail_emails
from email_classifier import classify_emails
from dashboard import generate_dashboard

LAST_RUN_FILE = 'last_run.json'


def load_last_run_date():
    """Load the last run date from last_run.json."""
    if not os.path.exists(LAST_RUN_FILE):
        return None

    try:
        with open(LAST_RUN_FILE, 'r') as f:
            data = json.load(f)
            return data.get('date')
    except:
        return None


def save_run_date():
    """Save today's date to last_run.json."""
    today = datetime.now().date().isoformat()
    with open(LAST_RUN_FILE, 'w') as f:
        json.dump({'date': today}, f)


def has_already_run_today():
    """Check if the agent has already run today."""
    last_run = load_last_run_date()
    today = datetime.now().date().isoformat()
    return last_run == today


def main():
    """Main orchestration flow."""
    print("[*] Email Agent starting...")

    # Parse CLI flags
    force_run = '--force' in sys.argv
    gmail_only = '--gmail' in sys.argv
    yahoo_only = '--yahoo' in sys.argv

    # Default: check both
    check_gmail = True
    check_yahoo = True
    if gmail_only:
        check_yahoo = False
    elif yahoo_only:
        check_gmail = False

    # Determine title
    if check_gmail and check_yahoo:
        title = "Morning Email Summary"
    elif check_gmail:
        title = "Gmail Morning Summary"
    else:
        title = "Yahoo Morning Summary"

    if has_already_run_today() and not force_run:
        print("[OK] Already ran today. Use --force to run again.")
        return

    all_emails = []

    # Fetch from Gmail
    if check_gmail:
        try:
            print("[*] Authenticating with Gmail...")
            gmail_service = get_gmail_service()
            print("[*] Fetching Gmail emails...")
            gmail_emails = fetch_gmail_emails(gmail_service, hours=24, max_results=50)
            print(f"[*] Fetched {len(gmail_emails)} Gmail emails")
            all_emails.extend(gmail_emails)
        except Exception as e:
            print(f"[WARN] Gmail fetch failed: {e}")
            if yahoo_only:
                raise

    # Fetch from Yahoo
    if check_yahoo:
        try:
            print("[*] Authenticating with Yahoo Mail...")
            from yahoo_client import get_authenticated_service as get_yahoo_service
            from yahoo_client import fetch_recent_emails as fetch_yahoo_emails
            yahoo_service = get_yahoo_service()
            print("[*] Fetching Yahoo emails...")
            yahoo_emails = fetch_yahoo_emails(yahoo_service, hours=24, max_results=50)
            print(f"[*] Fetched {len(yahoo_emails)} Yahoo emails")
            yahoo_service.close()
            all_emails.extend(yahoo_emails)
        except Exception as e:
            print(f"[WARN] Yahoo fetch failed: {e}")
            if gmail_only:
                raise

    if not all_emails:
        print("[OK] No emails to classify. Generating empty dashboard...")
        html = generate_dashboard([], title=title)
        dashboard_path = os.path.abspath('daily_summary.html')
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[*] Dashboard written to {dashboard_path}")
        webbrowser.open(f'file:///{dashboard_path}')
        save_run_date()
        print("[OK] Done!")
        return

    print(f"[*] Classifying {len(all_emails)} emails...")
    classifications = classify_emails(all_emails)

    print("[*] Merging classifications with email data...")
    emails_with_classification = []
    for email in all_emails:
        classification = next((c for c in classifications if c.get('id') == email['id']), None)
        if classification:
            email.update(classification)
        else:
            email['importance'] = 'not_important'
            email['reason'] = 'Classification unavailable'
        emails_with_classification.append(email)

    print("[*] Generating dashboard...")
    html = generate_dashboard(emails_with_classification, title=title)

    dashboard_path = os.path.abspath('daily_summary.html')
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[*] Dashboard written to {dashboard_path}")
    print("[*] Opening dashboard in browser...")
    webbrowser.open(f'file:///{dashboard_path}')

    save_run_date()
    print("[OK] Done! Dashboard opened successfully.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
