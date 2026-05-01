#!/usr/bin/env python3
"""
Gmail Morning Agent
Runs once daily at 8 AM, fetches inbox emails, classifies them with Claude,
and generates an HTML dashboard.
"""

import os
import json
import sys
import webbrowser
from datetime import datetime

from gmail_client import get_authenticated_service, fetch_recent_emails
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
    print("[*] Gmail Morning Agent starting...")

    if has_already_run_today():
        print("[OK] Already ran today. Exiting.")
        return

    try:
        print("[*] Authenticating with Gmail...")
        service = get_authenticated_service()

        print("[*] Fetching recent emails...")
        emails = fetch_recent_emails(service, hours=24, max_results=50)

        if not emails:
            print("[OK] No emails in the last 24 hours. Generating empty dashboard...")
            html = generate_dashboard([])
            dashboard_path = os.path.abspath('daily_summary.html')
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[*] Dashboard written to {dashboard_path}")
            webbrowser.open(f'file:///{dashboard_path}')
            save_run_date()
            print("[OK] Done!")
            return

        print(f"[*] Fetched {len(emails)} emails")

        print("[*] Classifying emails with Claude...")
        classifications = classify_emails(emails)

        print("[*] Merging classifications with email data...")
        emails_with_classification = []
        for email in emails:
            classification = next((c for c in classifications if c.get('id') == email['id']), None)
            if classification:
                email.update(classification)
            else:
                email['importance'] = 'not_important'
                email['reason'] = 'Classification unavailable'
            emails_with_classification.append(email)

        print("[*] Generating dashboard...")
        html = generate_dashboard(emails_with_classification)

        dashboard_path = os.path.abspath('daily_summary.html')
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"[*] Dashboard written to {dashboard_path}")

        print("[*] Opening dashboard in browser...")
        webbrowser.open(f'file:///{dashboard_path}')

        save_run_date()
        print("[OK] Done! Dashboard opened successfully.")

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
