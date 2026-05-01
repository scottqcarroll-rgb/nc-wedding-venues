# Gmail Morning Agent

A daily Gmail monitor that uses Claude AI to classify emails as important or not important, and generates a beautiful HTML dashboard.

## Features

- ✓ Runs once daily at 8:00 AM (via Windows Task Scheduler)
- ✓ Fetches emails from the last 24 hours
- ✓ Uses Claude Haiku to classify emails intelligently
- ✓ Generates a self-contained HTML dashboard
- ✓ Auto-opens dashboard in your default browser
- ✓ Prevents duplicate runs on the same day

## Setup

### 1. Google Cloud Console Setup (one-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the **Gmail API**
4. Create **OAuth 2.0 credentials** (Desktop application)
5. Download the credentials file and save it as `credentials.json` in this directory

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Set Your Anthropic API Key

Ensure your `ANTHROPIC_API_KEY` environment variable is set:

```powershell
$env:ANTHROPIC_API_KEY = "your-key-here"
```

Or add it to your system environment variables permanently.

### 4. Test the Agent

Run the agent manually to test:

```powershell
python gmail_agent.py
```

This will:
- Authenticate with Gmail (browser popup on first run)
- Fetch your inbox emails from the last 24 hours
- Classify them with Claude
- Generate and open the dashboard

### 5. Schedule Daily Runs

To run the agent at 8:00 AM every day, register the Windows Task Scheduler task (requires admin):

```powershell
schtasks /create /xml "task_scheduler.xml" /tn "GmailMorningAgent"
```

To verify it was registered:

```powershell
schtasks /query /tn "GmailMorningAgent"
```

To manually trigger it:

```powershell
schtasks /run /tn "GmailMorningAgent"
```

To remove the scheduled task:

```powershell
schtasks /delete /tn "GmailMorningAgent" /f
```

## Files

| File | Purpose |
|---|---|
| `gmail_agent.py` | Main orchestrator (entry point) |
| `gmail_client.py` | Gmail OAuth2 authentication and email fetching |
| `email_classifier.py` | Claude API email classification |
| `dashboard.py` | HTML dashboard generator |
| `requirements.txt` | Python dependencies |
| `task_scheduler.xml` | Windows Task Scheduler configuration |
| `.gitignore` | Excludes secrets and generated files |
| `last_run.json` | Tracks last run date (prevents duplicates) |
| `daily_summary.html` | Generated dashboard (created daily) |

## How It Works

1. **Guard Check** — If the agent has already run today, it exits early
2. **Gmail Auth** — Authenticates with Gmail using OAuth2 (stored token)
3. **Email Fetch** — Retrieves emails from the last 24 hours, max 50
4. **AI Classification** — Sends all emails to Claude in one API call with prompt caching
5. **Dashboard Generation** — Creates a self-contained HTML file
6. **Browser Open** — Auto-opens the dashboard in your default browser
7. **Date Lock** — Saves today's date to prevent re-running

## Troubleshooting

### "credentials.json not found"

Download OAuth credentials from Google Cloud Console and place in this directory.

### "Classification unavailable" on all emails

Check that your `ANTHROPIC_API_KEY` is set and valid.

### Task Scheduler not running

- Check that the working directory path in `task_scheduler.xml` matches your actual installation
- Verify the task is enabled: `schtasks /query /tn "GmailMorningAgent" /v`
- Check Windows Task Scheduler app for error details

### Emails not showing up

- Gmail API may need additional permissions — try re-authorizing by deleting `token.json` and running `python gmail_agent.py` again
- Verify your Gmail account has IMAP enabled

## Cost

The agent uses Claude Haiku (cheapest tier) with prompt caching enabled:
- System prompt cached (stable, reused daily)
- One API call per run (batch classification)
- Typical cost: < $0.001 per day

## License

MIT
