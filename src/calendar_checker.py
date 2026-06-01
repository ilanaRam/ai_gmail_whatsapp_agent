import json
import os
import inspect

# to work with google tools for exp: calendar (this tool holds personal data so it requires authentications and credentials)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from dotenv import load_dotenv

# to work with .env
load_dotenv()

# SCOPES are permissions (like a keys from your home) you give to your app, these permissions can be:
#--------Permission -------- Meaning------------------------
# calendar.readonly,        Read only — view events
# calendar.events,          Read + Create + Edit + Delete events
# calendar,                 Read + Create + Edit + Delete events + manage settings
#--------------------------------------------------------
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# what is token.json file:
# This file is created automatically the first time you run the app.
# It stores a temporary access token (like a temporary pass) so you don’t have to 'log in' every time. It is like "remember me"
# each time the code will run it will check if token.json exists - if yes it will not rewrite it else it will perform log in and token.json will be re created
TOKEN_FILE = 'token.json'

calendar_service_obj = None  # global google calendar connection obj

def connect_to_google_calendar():
    """
    If first run → opens browser for Google login → saves token.json
    Then every next run after → uses token.json automatically — no login needed
    :return: calendar_service_obj
    """

    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    global calendar_service_obj  # ← use globaly

    my_app_creds = None

    client_config_dict = {
        "installed": {
            "client_id": os.getenv('GOOGLE_CALENDAR_CLIENT_ID'),
            "project_id": os.getenv('GOOGLE_CALENDAR_PROJECT_ID'),
            "auth_uri": os.getenv('GOOGLE_CALENDAR_AUTH_URI'),
            "token_uri": os.getenv('GOOGLE_CALENDAR_TOKEN_URI'),
            "client_secret": os.getenv('GOOGLE_CALENDAR_CLIENT_SECRET'),
            "redirect_uris": ["http://localhost"] # cannot be loaded from .env (as .env is good for simple key value and all is stored as string, here we need a list
        }
    }
    # token.json stores the user's access token
    # it is created automatically on first login
    if os.path.exists(TOKEN_FILE):
        my_app_creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # if no valid credentials available, or they exist by not valid any longer (not up to dated) then ... ask user to login again
    if not my_app_creds or not my_app_creds.valid:
        if my_app_creds and my_app_creds.expired and my_app_creds.refresh_token:
            my_app_creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_config_dict, # dict with credentials
                                                       SCOPES)             # list of scopes (permissions)
            my_app_creds = flow.run_local_server(port=0)

        # save credentials for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(my_app_creds.to_json())

    # update the 'global' calendar service obj
    calendar_service_obj = build('calendar',
                                'v3',
                                credentials=my_app_creds)
    if calendar_service_obj:
        print(f"{func_name}: App is connected to Google Calendar successfully, calendar_service_obj is: {calendar_service_obj}")
    else:
        print(f"{func_name}: App failed to connect to Google Calendar ###")


if __name__ == "__main__":
    connect_to_google_calendar()
