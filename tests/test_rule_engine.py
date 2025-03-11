import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import text
from rule_engine import process_rule, build_where_clause, map_field_to_column

# Sample rules for testing
MOCK_RULES = {
    "rules": [
        {
            "name": "Unread Personal Emails",
            "conditions": [
                {"field": "from", "predicate": "does not contain", "value": "naukri.com"},
                {"field": "from", "predicate": "does not contain", "value": "linkedin.com"},
                {"field": "subject", "predicate": "does not contain", "value": "Job"}
            ],
            "actions": [
                {"type": "mark_as_unread"},
                {"type": "move_message", "folder_name": "Updates"}
            ],
            "predicate": "all"
        }
    ]
}

# Mock email data
MOCK_EMAILS = [
    {"message_id": "123abc", "sender": "friend@example.com", "subject": "Hello"},
    {"message_id": "456def", "sender": "newsletter@example.com", "subject": "Weekly Update"},
]

@pytest.fixture
def mock_service():
    """Mock Google API service."""
    return MagicMock()

@pytest.fixture
def mock_db_session():
    with patch("rule_engine.session.execute") as mock_execute:
        mock_execute.return_value.mappings().all.return_value = MOCK_EMAILS
        yield mock_execute

@pytest.fixture
def mock_load_rules():
    with patch("rule_engine.load_rules", return_value=MOCK_RULES["rules"]):
        yield

def test_map_field_to_column():
    assert map_field_to_column("subject") == "subject"
    assert map_field_to_column("from") == "sender"
    assert map_field_to_column("message") == "snippet"
    assert map_field_to_column("received_date") == "date"

def test_build_where_clause():
    conditions = [
        {"field": "from", "predicate": "contains", "value": "example.com"},
        {"field": "subject", "predicate": "does not contain", "value": "spam"}
    ]
    where_clause = build_where_clause(conditions, "all")
    assert "sender LIKE '%example.com%'" in where_clause
    assert "subject NOT LIKE '%spam%'" in where_clause

def test_process_rule(mock_service, mock_db_session, mock_load_rules):
    """Test the process_rule function with mocked dependencies."""
    process_rule("Unread Personal Emails", mock_service)

    args, _ = mock_db_session.call_args
    expected_query = (
        "SELECT * FROM emails WHERE sender NOT LIKE '%naukri.com%' "
        "AND sender NOT LIKE '%linkedin.com%' AND subject NOT LIKE '%Job%';"
    )
    assert str(args[0]) == str(text(expected_query))

    mock_service.users().messages().batchModify.assert_any_call(
        userId='me', body={'ids': ['123abc', '456def'], 'addLabelIds': ['UNREAD']}
    )
    mock_service.users().messages().batchModify.assert_any_call(
        userId='me', body={'ids': ['123abc', '456def'], 'addLabelIds': ['CATEGORY_UPDATES'], 'removeLabelIds': ['INBOX']}
    )
