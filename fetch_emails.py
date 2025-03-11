from googleapiclient.discovery import build
from db.db import save_email, session, Email
from authenticate import authenticate
from datetime import datetime
from email.utils import parseaddr

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def fetch_emails():
    # fetch emails from gmail based on user input and save them to db
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    total_to_fetch = int(input("Enter total number of emails to fetch: "))
    all_messages = []
    page_token = None

    while len(all_messages) < total_to_fetch:
        remaining = total_to_fetch - len(all_messages)

        kwargs = {'userId': 'me', 'maxResults': remaining, 'q': ''}
        if page_token:
            kwargs['pageToken'] = page_token

        response = service.users().messages().list(**kwargs).execute()
        messages = response.get('messages', [])
        all_messages.extend(messages)

        print(f"Fetched {len(messages)} messages in this page. Total collected: {len(all_messages)}")

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    if not all_messages:
        print("No new emails found.")
        return

    print(f"Total fetched messages: {len(all_messages)}")

    for msg in all_messages:
        msg_id = msg['id']

        # Avoid duplicates: skip if already in database
        if session.query(Email).filter_by(message_id=msg_id).first():
            print(f"Email already exists in DB: {msg_id}")
            continue

        # Fetch full email details
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])

        # Extract Subject, Sender, and To
        subject = ""
        sender = ""
        to_field = ""
        for header in headers:
            header_name = header['name'].lower()
            if header_name == 'subject':
                subject = header.get('value', '')
            elif header_name == 'from':
                sender = header.get('value', '')
                sender = parseaddr(sender)[1]
            elif header_name == 'to':
                to_field = header.get('value', '')
                to_field = parseaddr(to_field)[1]

        internal_date = message.get('internalDate')
        if internal_date:
            internal_date = datetime.fromtimestamp(int(internal_date) / 1000)

        email_info = {
            "message_id": msg_id,
            "sender": sender or "Unknown",
            "subject": subject or "No Subject",
            "to": to_field or "Unknown",
            "date": internal_date,
            "snippet": message.get('snippet', "")
        }

        save_email(email_info)

    print("All emails saved successfully!")

if __name__ == "__main__":
    fetch_emails()
