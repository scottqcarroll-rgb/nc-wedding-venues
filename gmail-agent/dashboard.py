import json
from datetime import datetime

def generate_dashboard(emails_with_classification, title="Morning Email Summary"):
    """Generate a self-contained HTML dashboard from classified emails."""

    important = [e for e in emails_with_classification if e.get('importance') == 'important']
    not_important = [e for e in emails_with_classification if e.get('importance') == 'not_important']

    today = datetime.now().strftime('%A, %B %d, %Y')
    now = datetime.now().strftime('%I:%M %p')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #0f1117;
            color: #e2e8f0;
            line-height: 1.6;
            padding: 32px 16px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: linear-gradient(135deg, #1a1f2e 0%, #131720 100%);
            border: 1px solid #2d3748;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 24px;
            flex-wrap: wrap;
        }}

        .header-left h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #f7fafc;
        }}

        .header-date {{
            color: #a0aec0;
            font-size: 14px;
            letter-spacing: 0.05em;
        }}

        .stats {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .stat {{
            background: #131720;
            border: 1px solid #2d3748;
            border-radius: 12px;
            padding: 16px 24px;
            text-align: center;
            min-width: 120px;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: 900;
            margin-bottom: 4px;
        }}

        .stat-important .stat-value {{
            color: #68d391;
        }}

        .stat-notimportant .stat-value {{
            color: #a0aec0;
        }}

        .stat-total .stat-value {{
            color: #76e4f7;
        }}

        .stat-label {{
            font-size: 12px;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #718096;
        }}

        .content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }}

        .column h2 {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #2d3748;
        }}

        .column-important h2 {{
            color: #68d391;
            border-bottom-color: #68d391;
        }}

        .column-notimportant h2 {{
            color: #a0aec0;
            border-bottom-color: #4a5568;
        }}

        .email-card {{
            background: #1a1f2e;
            border: 1px solid #2d3748;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            transition: all 0.2s ease;
        }}

        .column-important .email-card {{
            border-left: 3px solid #68d391;
        }}

        .column-important .email-card:hover {{
            border-color: #68d391;
            box-shadow: 0 0 20px rgba(104, 211, 145, 0.2);
        }}

        .column-notimportant .email-card {{
            border-left: 3px solid #4a5568;
            opacity: 0.8;
        }}

        .column-notimportant .email-card:hover {{
            opacity: 1;
            border-color: #718096;
        }}

        .email-from {{
            font-size: 13px;
            color: #a0aec0;
            margin-bottom: 6px;
            word-break: break-word;
        }}

        .email-subject {{
            font-size: 15px;
            font-weight: 700;
            color: #f7fafc;
            margin-bottom: 8px;
            word-break: break-word;
        }}

        .email-snippet {{
            font-size: 13px;
            color: #718096;
            margin-bottom: 12px;
            line-height: 1.5;
            word-break: break-word;
        }}

        .email-reason {{
            font-size: 12px;
            font-style: italic;
            padding: 8px 12px;
            border-radius: 6px;
            background: #131720;
            color: #cbd5e0;
            word-break: break-word;
        }}

        .column-important .email-reason {{
            background: rgba(104, 211, 145, 0.1);
            color: #68d391;
        }}

        .column-notimportant .email-reason {{
            background: rgba(113, 128, 150, 0.1);
            color: #a0aec0;
        }}

        .empty {{
            text-align: center;
            padding: 32px;
            color: #718096;
        }}

        .footer {{
            text-align: center;
            color: #718096;
            font-size: 12px;
            border-top: 1px solid #2d3748;
            padding-top: 24px;
            margin-top: 32px;
        }}

        .badge {{
            display: inline-block;
            background: #2d3748;
            color: #e2e8f0;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            margin-left: 8px;
        }}

        .source-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-right: 8px;
            text-transform: uppercase;
        }}

        .source-gmail {{
            background: rgba(118, 228, 247, 0.15);
            color: #76e4f7;
            border: 1px solid #76e4f7;
        }}

        .source-yahoo {{
            background: rgba(183, 148, 244, 0.15);
            color: #b794f4;
            border: 1px solid #b794f4;
        }}

        @media (max-width: 768px) {{
            .content {{
                grid-template-columns: 1fr;
            }}

            .header {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .stats {{
                width: 100%;
                justify-content: space-between;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <h1>📧 {title}</h1>
                <div class="header-date">{today}</div>
            </div>
            <div class="stats">
                <div class="stat stat-total">
                    <div class="stat-value">{len(emails_with_classification)}</div>
                    <div class="stat-label">Total</div>
                </div>
                <div class="stat stat-important">
                    <div class="stat-value">{len(important)}</div>
                    <div class="stat-label">Important</div>
                </div>
                <div class="stat stat-notimportant">
                    <div class="stat-value">{len(not_important)}</div>
                    <div class="stat-label">Not Important</div>
                </div>
            </div>
        </div>

        <div class="content">
            <div class="column column-important">
                <h2>⭐ Important</h2>
                {_render_email_cards(important) if important else '<div class="empty">No important emails</div>'}
            </div>

            <div class="column column-notimportant">
                <h2>📰 Not Important</h2>
                {_render_email_cards(not_important) if not_important else '<div class="empty">No unimportant emails</div>'}
            </div>
        </div>

        <div class="footer">
            <p>Generated at {now} on {today}</p>
            <p>Powered by Claude <span class="badge">Haiku</span></p>
        </div>
    </div>
</body>
</html>"""

    return html


def _render_email_cards(emails):
    """Render email cards as HTML."""
    cards = []
    for email in emails:
        subject = email.get('subject', 'No Subject')
        from_addr = email.get('from', 'Unknown')
        snippet = email.get('snippet', '')
        reason = email.get('reason', '')
        source = email.get('source', 'Unknown')

        # Determine source badge class
        source_class = 'source-gmail' if source == 'Gmail' else 'source-yahoo'

        card = f"""
            <div class="email-card">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span class="source-badge {source_class}">{_escape_html(source)}</span>
                </div>
                <div class="email-from">{_escape_html(from_addr)}</div>
                <div class="email-subject">{_escape_html(subject)}</div>
                <div class="email-snippet">{_escape_html(snippet)}</div>
                <div class="email-reason">{_escape_html(reason)}</div>
            </div>
        """
        cards.append(card)

    return "\n".join(cards)


def _escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


if __name__ == '__main__':
    test_data = [
        {
            "id": "msg1",
            "from": "boss@company.com",
            "subject": "Project deadline moved to Friday",
            "snippet": "The client requested we move the deadline up...",
            "importance": "important",
            "reason": "Action required from your manager."
        },
        {
            "id": "msg2",
            "from": "newsletter@retailer.com",
            "subject": "50% off everything this weekend!",
            "snippet": "Limited time offer from your favorite retailer...",
            "importance": "not_important",
            "reason": "Promotional email from a retailer."
        }
    ]

    html = generate_dashboard(test_data)
    with open('daily_summary.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("[OK] Dashboard written to daily_summary.html")
