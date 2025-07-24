import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleAuthenticator:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        
    
    def authenticate(self):
        creds = None
        if os.path.exists(self.token_file):
            print(f"Loading existing credentials from {self.token_file}")
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                print("Staring new authentication flow")
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Credentials file {self.credentials_file} not found.")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            print(f"Saving credentials to {self.token_file}")
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        print("creating Google Calendar service")
        self.service = build('calendar', 'v3', credentials=creds)
        return self.service
    
    def get_service(self):
        if self.service is None:
            print("Service not initialized, authenticating...")
            self.authenticate()
        return self.service