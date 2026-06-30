import json
import os
import inspect

# to work with google tools for exp: calendar (this tool holds personal data so it requires authentications and credentials)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta

from dotenv import load_dotenv

# to work with .env
load_dotenv()

# hint so the events() will be known to PyCharm:
from googleapiclient.discovery import Resource

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

def validity_check(google_calendar_event: dict):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    if not google_calendar_event:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is EMPTY ###")
        return None

    # title
    if google_calendar_event.get('title',None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'title' ")
        return None
    if not google_calendar_event['title']:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing data in field: 'title' ")
        return None

    # participants
    if google_calendar_event.get('participants',None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'participants' ")
        return None
    if not google_calendar_event['participants']:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing data in field: 'participants' ")
        return None

    # my_calendar
    if google_calendar_event.get('my_calendar',None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'my_calendar' ")
        return None
    if google_calendar_event['my_calendar'] == None:
        print(f"[{func_name}]: ERROR — was not indicated if to set 'my_calendar' with new event")
        return None

    # alex_calendar
    if google_calendar_event.get('alex_calendar',None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'alex_calendar' ")
        return None
    if google_calendar_event['alex_calendar'] == None:
        print(f"[{func_name}]: ERROR — was not indicated if to set 'alex_calendar' with new event")
        return None

    # date
    if google_calendar_event.get('date', None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'date' ")
        return None
    if google_calendar_event['date'] == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing data in field: 'date'")
        return None
    if not isinstance(google_calendar_event['date'], str):
        print(f"[{func_name}]: ERROR — google_calendar_event_data has incorrect data type in field: 'date': {google_calendar_event['alert_minutes_before']}")
        return None

    # time
    if google_calendar_event.get('time', None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'time' ")
        return None
    if google_calendar_event['time'] == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing data in field: 'time'")
        return None
    if not isinstance(google_calendar_event['time'], str):
        print(f"[{func_name}]: ERROR — google_calendar_event_data is wrong data type in field: 'time'")
        return None

    # duration_minutes
    if google_calendar_event.get('duration_minutes', None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'duration_minutes' ")
        return None
    if google_calendar_event['duration_minutes'] == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing data in field: 'duration_minutes'")
        return None
    if google_calendar_event['duration_minutes'] == 0:
        print(f"[{func_name}]: ERROR — google_calendar_event_data has 0 in field: 'duration_minutes'")
        return None
    if google_calendar_event['duration_minutes'] < 0:
        print(f"[{func_name}]: ERROR — google_calendar_event_data has negative value in field: 'duration_minutes'")
        return None

    # description
    if google_calendar_event.get('description', None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'description' ")
        return None
    if google_calendar_event['description'] == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing data in field: 'description'")
        return None

    # alert_minutes_before
    if google_calendar_event.get('alert_minutes_before', None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'alert_minutes_before' ")
        return None
    if google_calendar_event['alert_minutes_before'] == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing data in field: 'alert_minutes_before'")
        return None
    if not isinstance(google_calendar_event['alert_minutes_before'], int):
        print(f"[{func_name}]: ERROR — google_calendar_event_data has incorrect data type in field: 'alert_minutes_before': {google_calendar_event['alert_minutes_before']}")
        return None
    if google_calendar_event['alert_minutes_before'] < 0:
        print(f"[{func_name}]: ERROR — google_calendar_event_data has negative data in field: 'alert_minutes_before'")
        return None


    # is_urgent
    if google_calendar_event.get('is_urgent', None) == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing field 'is_urgent' ")
        return None
    if google_calendar_event['is_urgent'] == None:
        print(f"[{func_name}]: ERROR — google_calendar_event_data is missing data in field: 'is_urgent'")
        return None
    if not isinstance(google_calendar_event['is_urgent'], bool):
        print(f"[{func_name}]: ERROR — google_calendar_event_data incorrect data type for field: 'is_urgent'")
        return None
    return True

def connect_to_google_calendar():
    """
    This api opens connection to Google Calendar - it actually creates calendar_service - it is like access to Google Calendar service
    Later in the api: create_calendar_event() we will use this calendar_service object to create Google Calendar event

    At the first run: will be opened a browser for Google login → saves token.json
    Then every next run after → uses token.json automatically — no login needed
    :return: calendar_service_obj  --> this obj to the google calendar connection
    """

    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

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
        print(f"[{func_name}]: App is connected to Google Calendar successfully, calendar_service_obj is: {calendar_service_obj}")
        return calendar_service_obj
    else:
        print(f"[{func_name}]: App failed to connect to Google Calendar ###")
        return None


def create_google_calendar_event(google_calendar_event_data: dict,
                                 google_calendar_service):
    """
    This api uses the calendar_service object that was created by me before to create Google Calendar event using a data received as input
    :param calendar_event_data:
    :return: Google Calendar event
    """
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    if not google_calendar_event_data:
        print(f"[{func_name}]: ERROR — event structure isn't correct ###")
        return None

    if not google_calendar_service:
        print(f"[{func_name}]: ERROR — Google Calendar service isn't ready - it means Google Calendar service NOT CONNECTED ###")
        return None

    result = validity_check(google_calendar_event_data)
    if not result:
        raise ValueError(f"[{func_name}]: Error found during creating event structure, some data is missing")

    print(f"[{func_name}]: Google Calendar service obj is ready, we can proceed to creating Calendar event obj VVV")

    # 1. Parse the string date and time into a real Python datetime object
    start_str = f"{google_calendar_event_data['date']} {google_calendar_event_data['time']}"
    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")

    # 2. Get the duration from your Gemini data (defaulting to 60 if missing)
    duration = google_calendar_event_data.get('duration_minutes', 60)

    # 3. Add the duration to calculate the exact end time
    end_dt = start_dt + timedelta(minutes=duration)

    # 4. Format them back into the ISO string format Google requires
    start_iso = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
    end_iso = end_dt.strftime("%Y-%m-%dT%H:%M:%S")

    # build google calendar event obj that Google Calendar API expects
    event = {
            'summary': google_calendar_event_data['title'],
            'description': google_calendar_event_data.get('description', ''),
            'start': {
                'dateTime': start_iso,
                'timeZone': 'Asia/Jerusalem'
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': 'Asia/Jerusalem'
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup',
                     'minutes': google_calendar_event_data.get('alert_minutes_before', 30)
                     }
                ]
            }
    }

    # insert event into calendar
    # !!! connect_to_google_calendar() must run first to initiate the calendar_service_obj, else it will be None and will not have .events()
    print(f"[{func_name}]: Google Calendar event structure is ready, we can create the event")
    created_event = google_calendar_service.events().insert(calendarId='primary',
                                                            body=event).execute()

    print(f"[{func_name}]: Google Calendar event - created in the Google Calendar successfully VVV")
    print(f"[{func_name}]: Event link: {created_event.get('htmlLink')}")
    return created_event




if __name__ == "__main__":
    # 1.creates (initiates) the global google calendar service obj
    connect_to_google_calendar()

    # 2.create moc data - as if the data came from ai_analyzer tool
    mock_event = {
            'title': 'תור לאלכס לרופא שיניים',
            "participants": ["Alex", "Ilana"],
            "my_calendar": True,
            "alex_calendar": True,
            'date': '2026-06-13',
            'time': '15:00',
            'duration_minutes': 60,
            'description': 'תור לאלכס לרופא שיניים דר דב בר טורא בעמישב בשבוע הבא - להביא צילומים ',
            'alert_minutes_before': 30,
            "is_urgent": False
        }

    # 3.create google calendar event basing on moc data in my calendar
    result = create_google_calendar_event(google_calendar_event_data=mock_event)
    if result:
        print(f"\nSuccess! Event created in Google Calendar.")
        print(f"Event Link: {result.get('htmlLink')}")


