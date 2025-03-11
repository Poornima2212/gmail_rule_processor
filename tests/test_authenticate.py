
import os
from io import StringIO
from unittest.mock import MagicMock
from authenticate import authenticate, SCOPES

def fake_open_factory():
    def fake_open(*args, **kwargs):
        return StringIO()
    return fake_open

def test_authenticate_with_valid_token(monkeypatch):
    # Simulate token.json exists
    monkeypatch.setattr(os.path, "exists", lambda path: True if path == "token.json" else False)
    fake_creds = MagicMock()
    fake_creds.valid = True
    fake_creds.to_json.return_value = '{"token": "valid"}'
    
    def fake_from_authorized_user_file(filename, scopes):
        assert filename == "token.json"
        assert scopes == SCOPES
        return fake_creds
    monkeypatch.setattr("authenticate.Credentials.from_authorized_user_file", fake_from_authorized_user_file)
    
    # Patch open to prevent actual file writes.
    monkeypatch.setattr("builtins.open", fake_open_factory())
    
    # Run the authentication function.
    creds = authenticate()
    assert creds == fake_creds

def test_authenticate_with_expired_token(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda path: True if path == "token.json" else False)
    
    fake_creds = MagicMock()
    fake_creds.valid = False
    fake_creds.expired = True
    fake_creds.refresh_token = True
    fake_creds.to_json.return_value = '{"token": "refreshed"}'
    
    def fake_from_authorized_user_file(filename, scopes):
        return fake_creds
    monkeypatch.setattr("authenticate.Credentials.from_authorized_user_file", fake_from_authorized_user_file)
    
    fake_creds.refresh = MagicMock()
    fake_creds.valid = True
    
    monkeypatch.setattr("builtins.open", fake_open_factory())
    
    creds = authenticate()
    fake_creds.refresh.assert_called_once()
    assert creds == fake_creds

def test_authenticate_no_token(monkeypatch):
    # Simulate that token.json does not exist.
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    
    fake_creds = MagicMock()
    fake_creds.valid = True
    fake_creds.to_json.return_value = '{"token": "new"}'
    
    fake_flow = MagicMock()
    fake_flow.run_local_server.return_value = fake_creds
    
    def fake_from_client_secrets_file(filename, scopes):
        assert filename == "credentials.json"
        assert scopes == SCOPES
        return fake_flow
    monkeypatch.setattr("authenticate.InstalledAppFlow.from_client_secrets_file", fake_from_client_secrets_file)
    
    monkeypatch.setattr("builtins.open", fake_open_factory())
    
    creds = authenticate()
    fake_flow.run_local_server.assert_called_once()
    assert creds == fake_creds
