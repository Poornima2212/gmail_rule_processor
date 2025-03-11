from googleapiclient.errors import HttpError

def mark_as_read(service, message_ids):
    try:
        service.users().messages().batchModify(
            userId='me',
            body={
                'ids': message_ids,
                'removeLabelIds': ['UNREAD']
            }
        ).execute()
        print(f"Marked {len(message_ids)} emails as read!")
    except HttpError as error:
        print(f"Failed to mark emails as read: {error}")

def mark_as_unread(service, message_ids):
    try:
        service.users().messages().batchModify(
            userId='me',
            body={
                'ids': message_ids,
                'addLabelIds': ['UNREAD']
            }
        ).execute()
        print(f"Marked {len(message_ids)} emails as unread!")
    except HttpError as error:
        print(f"Failed to mark emails as unread: {error}")

def move_message(service, message_ids, folder_name):
    folder_map = {
        "Promotions": "CATEGORY_PROMOTIONS",
        "Social": "CATEGORY_SOCIAL",
        "Updates": "CATEGORY_UPDATES",
        "Forums": "CATEGORY_FORUMS",
        "Spam": "SPAM"
    }

    label_id = folder_map.get(folder_name)

    if not label_id:
        print(f"Folder '{folder_name}' does not exist in Gmail. Skipping.")
        return

    try:
        service.users().messages().batchModify(
            userId='me',
            body={
                'ids': message_ids,
                'addLabelIds': [label_id],
                'removeLabelIds': ['INBOX']
            }
        ).execute()
        print(f"Moved {len(message_ids)} emails to '{folder_name}'")
    except HttpError as error:
        print(f"Failed to move emails to '{folder_name}': {error}")
