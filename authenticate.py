from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def authenticate():
    creds = None

    # Check if token.json exists (token already generated)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        # If token has expired, refreshing it without login
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Token was expired and successfully refreshed!")

    # If no valid credentials, perform login flow
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        print("New token generated and saved.")

    # save the token (even after refreshing)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    return creds


if __name__ == "__main__":
    authenticate()
    print("Authentication successful!")
