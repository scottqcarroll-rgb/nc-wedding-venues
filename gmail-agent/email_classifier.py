import json
import os
from anthropic import Anthropic

client = Anthropic()

SYSTEM_PROMPT = """You are an email importance classifier. Your job is to analyze emails and determine if they are "important" or "not_important".

An email is IMPORTANT if:
- It requires action (reply needed, deadline, payment, appointment, decision needed)
- It's from a known contact or organization the user actively engages with
- It contains financial, legal, medical, or time-sensitive information
- It's personal communication (not automated/marketing)

An email is NOT IMPORTANT if:
- It's a promotional/marketing email
- It's automated notification (social media, app updates, etc.)
- It's newsletter or digest content
- No action is required
- It's spam or low-priority

You will receive a numbered list of emails as JSON objects. For each email, respond with:
1. The email ID
2. "important" or "not_important"
3. A one-sentence reason for your classification

Return your response as a JSON array with this format:
[
  {"id": "email_id_here", "importance": "important", "reason": "One sentence reason."},
  {"id": "email_id_here", "importance": "not_important", "reason": "One sentence reason."}
]

Only return the JSON array, no other text."""


def classify_emails(emails):
    """Use Claude to classify emails as important or not important."""
    if not emails:
        return []

    email_list = "\n".join([
        f"{i+1}. {json.dumps(email)}"
        for i, email in enumerate(emails)
    ])

    user_message = f"""Please classify these emails:

{email_list}"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        response_text = response.content[0].text
        classifications = json.loads(response_text)

        return classifications

    except json.JSONDecodeError as e:
        print(f"[WARN] Error parsing Claude response: {e}")
        return [{"id": e.get('id', '?'), "importance": "not_important", "reason": "Classification unavailable"} for e in emails]
    except Exception as e:
        print(f"[ERROR] Error classifying emails: {e}")
        raise


if __name__ == '__main__':
    test_emails = [
        {
            "id": "msg1",
            "from": "boss@company.com",
            "subject": "Project deadline moved to Friday",
            "snippet": "The client requested we move the deadline...",
            "date": "2024-01-15"
        },
        {
            "id": "msg2",
            "from": "newsletter@retailer.com",
            "subject": "50% off everything this weekend!",
            "snippet": "Limited time offer from your favorite retailer...",
            "date": "2024-01-15"
        }
    ]

    try:
        results = classify_emails(test_emails)
        print("[OK] Classifications:")
        for r in results:
            print(f"  {r['id']}: {r['importance']} - {r['reason']}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
