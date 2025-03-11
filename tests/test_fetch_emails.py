import pytest
from datetime import datetime
import fetch_emails

saved_emails = []

# --- Fake Gmail API Service and Response Classes ---
class FakeResponse:
    def __init__(self, data):
        self.data = data
    def execute(self):
        return self.data

class FakeGmailService:
    def __init__(self, messages_list_response, messages_get_response):
        self.messages_list_response = messages_list_response
        self.messages_get_response = messages_get_response
        self.list_calls = 0

    def users(self):
        return self

    def messages(self):
        return self

    def list(self, **kwargs):
        self.list_calls += 1
        return FakeResponse(self.messages_list_response)

    def get(self, **kwargs):
        msg_id = kwargs.get("id")
        data = self.messages_get_response.get(msg_id, {})
        return FakeResponse(data)

# --- Fake Database Query ---
class FakeQuery:
    # Always returns no existing email (i.e., every email is new).
    def filter_by(self, **kwargs):
        return self
    def first(self):
        return None

class FakeSession:
    def query(self, model):
        return FakeQuery()

def fake_save_email(email_info):
    saved_emails.append(email_info)

@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    # Patch session in fetch_emails so it always returns FakeSession.
    monkeypatch.setattr(fetch_emails, "session", FakeSession())
    # Patch save_email with our fake function.
    monkeypatch.setattr(fetch_emails, "save_email", fake_save_email)
    saved_emails.clear()

@pytest.fixture
def fake_gmail_service():
    messages_list_response = {
        "messages": [{"id": "123"}, {"id": "456"}],
        "nextPageToken": None
    }
    messages_get_response = {
        "123": {
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject 123"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "receiver@example.com"}
                ]
            },
            "internalDate": "1610000000000",
            "snippet": "Snippet 123"
        },
        "456": {
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject 456"},
                    {"name": "From", "value": "sender2@example.com"},
                    {"name": "To", "value": "receiver2@example.com"}
                ]
            },
            "internalDate": "1620000000000",
            "snippet": "Snippet 456"
        }
    }
    return FakeGmailService(messages_list_response, messages_get_response)

@pytest.fixture
def fake_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "2")

def test_fetch_emails(monkeypatch, fake_gmail_service, fake_input, capsys):
    # Patch authenticate to return dummy creds
    monkeypatch.setattr(fetch_emails, "authenticate", lambda: "dummy_creds")
    # Patch build to return our fake Gmail service
    monkeypatch.setattr(fetch_emails, "build", lambda service, version, credentials: fake_gmail_service)

    # Run fetch_emails
    fetch_emails.fetch_emails()

    assert len(saved_emails) == 2
    email1 = saved_emails[0]
    assert email1["message_id"] == "123"
    assert email1["subject"] == "Test Subject 123"
    assert email1["sender"] == "sender@example.com"
    assert email1["to"] == "receiver@example.com"
    assert isinstance(email1["date"], datetime)
    assert email1["snippet"] == "Snippet 123"

    captured = capsys.readouterr().out
    assert "All emails saved successfully!" in captured

