# Unified Email Agent Skill

Check your Gmail and/or Yahoo Mail inbox, classify emails as important or not important, and display a beautiful unified dashboard.

## Syntax

```
/email-agent [--gmail] [--yahoo] [--force]
```

### Flags

- **No flags** (default): Check both Gmail and Yahoo Mail accounts
- `--gmail`: Check Gmail only
- `--yahoo`: Check Yahoo Mail only  
- `--force`: Ignore daily guard, fetch fresh emails now

### Examples

```
/email-agent              # Check both Gmail + Yahoo
/email-agent --gmail      # Gmail only
/email-agent --yahoo      # Yahoo only
/email-agent --force      # Force refresh all accounts
/email-agent --gmail --force  # Force refresh Gmail only
```

## What It Does

1. **Authenticates** with your Gmail and/or Yahoo Mail account(s)
2. **Fetches** emails from the last 24 hours (max 50 per account)
3. **Classifies** each email as important or not important using rule-based keywords
4. **Generates** a beautiful HTML dashboard showing both accounts
5. **Opens** the dashboard in your default browser

**Email Source Badges:** Each card shows which account the email came from (Gmail in cyan, Yahoo in purple)

### Classification Rules

**Important if:**
- Urgent, ASAP, critical, deadline, due date
- Meeting, appointment, scheduled call
- Invoice, payment, receipt, contract
- Action required, confirmation, approval needed
- From boss/manager, work project assignment

**Not Important if:**
- Newsletter, digest, marketing email
- Promotional, sale, discount, limited time offer
- Social media notification (liked, followed, commented)
- Automated notification (do not reply)
- Unsubscribe link present

## Prerequisites

### Gmail Setup (One-Time)

1. Go to https://console.cloud.google.com
2. Create new project → enable Gmail API
3. Create OAuth2 credentials (Desktop app)
4. Add `http://localhost:8080/` as authorized redirect URI
5. Download credentials → save as `gmail-agent/credentials.json`

### Yahoo Mail Setup (One-Time)

1. Get your BellSouth/Yahoo email address and password
2. Edit `gmail-agent/.env` and add:
   ```
   YAHOO_EMAIL=youremail@bellsouth.net
   YAHOO_PASSWORD=your-regular-password
   ```
3. (If password doesn't work, you may need to enable IMAP access in Yahoo account settings at https://login.yahoo.com → Account Info → Security)

## Files & Directories

| File | Purpose |
|---|---|
| `gmail-agent/email_agent.py` | Main unified orchestrator |
| `gmail-agent/gmail_client.py` | Gmail OAuth2 + fetch |
| `gmail-agent/yahoo_client.py` | Yahoo IMAP + fetch |
| `gmail-agent/email_classifier.py` | Keyword-based classifier |
| `gmail-agent/dashboard.py` | HTML dashboard generator |
| `gmail-agent/credentials.json` | Google OAuth credentials (gitignored) |
| `gmail-agent/.env` | Yahoo credentials (gitignored) |
| `gmail-agent/daily_summary.html` | Generated dashboard |

## The Unified Dashboard

**Unified mode (both accounts):** "Morning Email Summary"
- Shows emails from both Gmail and Yahoo
- Source badge on each card (Gmail = cyan, Yahoo = purple)
- Two columns: Important | Not Important

**Gmail only:** "Gmail Morning Summary"
**Yahoo only:** "Yahoo Morning Summary"

Features:
- Dark theme, matches your venue dossiers
- Responsive design (stacks on mobile)
- Self-contained HTML (no external dependencies)
- Sender, subject, snippet, and AI classification reason per email

## Scheduling

Run automatically at 8:00 AM daily via Windows Task Scheduler:

```powershell
cd "C:\Users\scarroll\OneDrive\Desktop\Claude_Code\gmail-agent"
schtasks /create /xml "task_scheduler.xml" /tn "GmailMorningAgent"
```

To run for both accounts, edit `task_scheduler.xml` and change:
```xml
<Arguments>email_agent.py</Arguments>
```

Verify it's scheduled:
```powershell
schtasks /query /tn "GmailMorningAgent"
```

## Cost

**Completely free!** Uses rule-based keyword classification with no API calls.

## Troubleshooting

### "credentials.json not found" (Gmail)

Download OAuth credentials from Google Cloud Console and save to `gmail-agent/credentials.json`.

### "Yahoo credentials not found"

Add to `gmail-agent/.env`:
```
YAHOO_EMAIL=youremail@bellsouth.net
YAHOO_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

**Reminder:** Yahoo App Password is NOT your regular Yahoo password. Generate it at Account Security → App Passwords.

### One provider fails, the other succeeds

If Gmail auth fails but you have Yahoo credentials, the agent will show only Yahoo emails with a warning. Same for the reverse. This is intentional — it won't fail completely if one account is unavailable.

To make one provider required, remove the `--gmail` or `--yahoo` flag to re-enable both.

### Browser doesn't open

The dashboard was still generated. Check:
- `gmail-agent/daily_summary.html` exists
- Try opening it manually in your browser

## Related

- `/gmail-agent` — Legacy Gmail-only skill (still supported)
- Windows Task Scheduler — Schedule daily runs
- Claude Code — This IDE
