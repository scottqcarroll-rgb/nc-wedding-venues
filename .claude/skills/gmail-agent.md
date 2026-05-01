# Gmail Morning Agent Skill

Check your Gmail inbox, classify emails as important or not important, and display a beautiful dashboard.

## Syntax

```
/gmail-agent [--force]
```

- No arguments: Run if not already run today (checks `last_run.json`)
- `--force`: Ignore daily guard, fetch and classify fresh emails now

## What It Does

1. **Authenticates** with your Gmail account via OAuth2 (browser popup on first run)
2. **Fetches** emails from the last 24 hours (max 50)
3. **Classifies** each email as important or not important using rule-based keywords
4. **Generates** a beautiful HTML dashboard
5. **Opens** the dashboard in your default browser

**Important vs Not Important Signals:**

- **Important**: Urgent, deadline, payment, meeting, action required, project assignment, from boss/management
- **Not Important**: Newsletter, promotional, social media notifications, marketing emails, automated alerts

## Prerequisites (One-Time Setup)

### 1. Google Cloud Console Setup

1. Go to https://console.cloud.google.com
2. Create a new project → enable Gmail API
3. Create OAuth2 credentials (Desktop app type)
4. Add `http://localhost:8080/` as authorized redirect URI
5. Download credentials → save as `gmail-agent/credentials.json`

### 2. Anthropic API Key (Optional)

If you want to use Claude for classification instead of rule-based keywords:
1. Go to https://console.anthropic.com/account/keys
2. Copy your API key
3. Edit `gmail-agent/.env` and paste it

(Currently using free rule-based classification by default.)

## Files & Directories

- `gmail-agent/gmail_agent.py` — Main runner
- `gmail-agent/gmail_client.py` — Gmail OAuth2 + fetch
- `gmail-agent/email_classifier.py` — Keyword-based classifier
- `gmail-agent/dashboard.py` — HTML dashboard generator
- `gmail-agent/credentials.json` — Google OAuth credentials (gitignored)
- `gmail-agent/token.json` — OAuth token (auto-refreshed, gitignored)
- `gmail-agent/last_run.json` — Tracks last run date
- `gmail-agent/daily_summary.html` — Generated dashboard (overwritten daily)

## Usage Examples

**Run with daily guard (won't re-run if already ran today):**
```
/gmail-agent
```

**Force a fresh fetch right now:**
```
/gmail-agent --force
```

**Schedule daily at 8 AM via Windows Task Scheduler:**
```powershell
cd gmail-agent
schtasks /create /xml "task_scheduler.xml" /tn "GmailMorningAgent"
```

**Verify it's scheduled:**
```powershell
schtasks /query /tn "GmailMorningAgent"
```

**Remove from Task Scheduler:**
```powershell
schtasks /delete /tn "GmailMorningAgent" /f
```

## The Dashboard

Generated HTML file with:
- **Header**: Date, total email count, important/not-important breakdown
- **Two columns**: Important (green) | Not Important (gray)
- **Email cards**: Sender, subject, snippet, AI classification reason
- **Responsive**: Stacks to single column on mobile
- **Self-contained**: No external dependencies, works offline

## Troubleshooting

### "credentials.json not found"
Download OAuth credentials from Google Cloud Console and save to `gmail-agent/credentials.json`.

### Browser pops up asking to authorize on first run
That's normal! You're authorizing your own app to read your Gmail. Click **Allow**. The token is then auto-refreshed daily.

### Dashboard opens but shows no emails
1. Check that you have emails in your inbox from the last 24 hours
2. Try `--force` to bypass the daily guard

### Task Scheduler not running
- Verify the task is registered: `schtasks /query /tn "GmailMorningAgent"`
- Check that the working directory path in `task_scheduler.xml` is correct
- Look in Windows Task Scheduler app for error details

## Cost

**Completely free!** Uses rule-based keyword classification with no API calls.

If you switch to Claude classification (edit `.env`), cost is minimal:
- Claude Haiku: ~$0.0005 per 1K input tokens
- Typical email batch: < $0.001 per run
- With prompt caching: ~30% cheaper on repeat runs

## Examples

**Check your email right now:**
```
/gmail-agent
```

**Force a fresh check (ignore daily limit):**
```
/gmail-agent --force
```

**Schedule for automated daily checks:**
```
Set up Windows Task Scheduler as described above
```

## Related

- `venue-dossier` — Researches wedding venues
- Windows Task Scheduler — Schedule daily runs
- Claude Code — This IDE
