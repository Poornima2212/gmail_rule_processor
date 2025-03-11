import json
from db.db import session
from config import RULES_FILE
from actions import mark_as_read, mark_as_unread, move_message
from sqlalchemy import text

def load_rules():
    with open(RULES_FILE) as f:
        return json.load(f)["rules"]

def map_field_to_column(field):
    # Mapping a rule field to the corresponding database column name.
    mapping = {
        "subject": "subject",
        "from": "sender",
        "to": "to_address",
        "date": "date",
        "received_date": "date",
        "message": "snippet",
        "body": "snippet"
    }
    return mapping.get(field.lower(), field)

def build_where_clause(conditions, predicate):
    # where clause from a list of rule conditions
    # raises a valueError if a date condition is not in the format "< number >  < unit >."
    clauses = []
    for cond in conditions:
        field = cond["field"]
        operator = cond["predicate"].lower()
        value = cond["value"]
        column = map_field_to_column(field)
        
        if field.lower() in ["date", "received_date"]:
            parts = value.split()
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid format for date field '{field}' in rules.json. "
                    f"Value '{value}' should be in format '<integer> <unit>' (e.g., '7 days')."
                )
            try:
                time_value = int(parts[0])
            except ValueError:
                raise ValueError(
                    f"Invalid number for date field '{field}' in rules.json. "
                    f"Value '{parts[0]}' should be an integer."
                )
            time_unit = parts[1].lower()
            interval = f"-{time_value} {time_unit}"
            formatted_value = f"datetime('now', '{interval}')"
        else:
            formatted_value = f"'{value}'"
        operator_map = {
            "less than": f"{column} > {formatted_value}",
            "greater than": f"{column} < {formatted_value}",
            "equals": f"{column} = {formatted_value}" if field.lower() in ["date", "received_date"] else f"{column} = '{value}'",
            "does not equal": f"{column} <> {formatted_value}" if field.lower() in ["date", "received_date"] else f"{column} <> '{value}'",
            "contains": f"{column} LIKE '%{value}%'" if field.lower() not in ["date", "received_date"] else "",
            "does not contain": f"{column} NOT LIKE '%{value}%'" if field.lower() not in ["date", "received_date"] else ""
        }

        clause = operator_map.get(operator, "")
 
        if clause:
            clauses.append(clause)
    
    joiner = " AND " if predicate.lower() == "all" else " OR "
    return joiner.join(clauses)


def process_rule(selected_rule_name, service):
    rules = load_rules()
    selected_rule = next((rule for rule in rules if rule["name"] == selected_rule_name), None)
    if not selected_rule:
        print(f"Rule '{selected_rule_name}' not found.")
        return

    conditions = selected_rule.get("conditions", [])
    actions = selected_rule.get("actions", [])
    predicate = selected_rule.get("predicate", "all").lower()
    
    where_clause = build_where_clause(conditions, predicate)
    if not where_clause:
        print("No valid conditions found for this rule.")
        return
    
    query = f"SELECT * FROM emails WHERE {where_clause};"
    print(f"Executing query: {query}")
    
    result = session.execute(text(query))
    emails = result.mappings().all()
    print(f"Found {len(emails)} matching emails.")

    mark_read_emails = []
    mark_unread_emails = []
    move_emails_by_folder = {}


    for email in emails:
        for action in actions:
            action_type = action["type"].lower()
            if action_type == "mark_as_read":
                mark_read_emails.append(email["message_id"])
            elif action_type == "mark_as_unread":
                mark_unread_emails.append(email["message_id"])
            elif action_type == "move_message":
                folder_name = action["folder_name"]
                if folder_name not in move_emails_by_folder:
                    move_emails_by_folder[folder_name] = []
                move_emails_by_folder[folder_name].append(email["message_id"])

    if mark_read_emails:
        print(f"Marking {len(mark_read_emails)} emails as read...")
        mark_as_read(service, mark_read_emails)

    if mark_unread_emails:
        print(f"Marking {len(mark_unread_emails)} emails as unread...")
        mark_as_unread(service, mark_unread_emails)

    for folder, email_ids in move_emails_by_folder.items():
        print(f"Moving {len(email_ids)} emails to '{folder}'...")
        move_message(service, email_ids, folder)

    print("Rule processing completed.")
