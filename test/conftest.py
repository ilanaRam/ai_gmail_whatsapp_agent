from unittest.mock import patch, MagicMock   # <- for mock tests
import pytest

# conftest.py is special file - pytest automatically finds and loads it without any imports needed!

# my mocks Fixtures
# should be in separate file and not part of the test file.
# This way Fixtures shared across multiple test files, Cleaner separation, Professional standard


@pytest.fixture(autouse=True)
def mock_gmail_IMAP():
    # my real code makes several actions and not a chain, it does:
    # create gmail_imap_server
    # login() - my real code never uses a returned value of login, so no need to mock
    # select() -  my real code never uses a returned value of select, so no need to mock
    # search() - my code does use the returned values from search() so NEED to mock
    # fetch()
    with patch ('src.mail_checker.imaplib.IMAP4_SSL') as fake_gmail_imap_ssl:
        # ONE fake server object — all methods live on it
        fake_imap_server = MagicMock()

        fake_imap_server.search.return_value = ('OK', [b'1']) # tuple[str, list]
        fake_imap_server.fetch.return_value = ('OK',  [(b'', b'From: ilanaaprilloriram@gmail.com\r\nSubject: RRR\r\n\r\nTest body')])

        fake_gmail_imap_ssl.return_value = fake_imap_server
        yield

        print("teardown — fake mock_gmail_IMAP creator is removed")


@pytest.fixture(autouse=True)
def mock_gemini_ai_analyzer():
    # my real code makes:
    # creates client
    # client.models.generate_content()
    with patch ('src.ai_analyzer.genai.Client') as fake_gemini_ai_analayser:
        # ONE fake server object — all methods live on it
        fake_gemini_ai_client = MagicMock()
        fake_gemini_ai_client.models.generate_content.return_value.text = '''{  "title": "פגישה עם אלכס",
                                                                                "date": "2026-06-02",
                                                                                "time": "15:00",
                                                                                "duration_minutes": 60,
                                                                                "description": "לדון בפרויקט",
                                                                                "participants": ["אלכס"],
                                                                                "my_calendar": true,
                                                                                "alex_calendar": true,
                                                                                "is_urgent": false,
                                                                                "alert_minutes_before": 30
                                                                            }'''
        fake_gemini_ai_analayser.return_value = fake_gemini_ai_client
        yield

        print("teardown — fake mock_gemini_ai_analyzer creator is removed")


@pytest.fixture(autouse=True)
def mock_gmail_to_whatsapp():
    """
    this func is fixture - will be called by pytest package automatically
    'autouse' means context, this fixture (func mock_external_services) will be called for each test that will run without explicitly calling it by each test

    so we have here a factory (Twillio)
    we use factory Twillio to create a client to create a message (to send)
    so we need here to mock (to fake) 3 things:
    1.Twillio factory (we do it by 'with' object)
    2.client
    3.create() operation that creates message and returns message.sid
    """

    print("PART 1 - SETUP - all before yield - creation of all fakes")

   # patch means replace true by fake, it requires a path for the true, path is built from: package/module/class. Package = src, module = whatsapp_sender, class = Client
    with patch('src.whatsapp_sender.Client') as fake_twilio_client:
        """
        patch fakes the Twillio class         
        """
        # client = Client(...)
        # message = client.messages.create(...)

        # Client   <- patched
        # messages <- mocked
        # create   <- followed by return_value

        # fake object 3 — fake WhatsApp message (result of messages.create() is message.sid)
        # When code calls client.messages.create(...) — returns our fake message.
        fake_whatsapp_client  = MagicMock()
        fake_whatsapp_client.messages.create.return_value.sid = "WHATSAPP_MSG_ID_000"

        # now connect the chain that will replace real api and real object by faked one during the test run
        # tell patch: when Client(...) is called → return fake_twilio_client_instance
        fake_twilio_client.return_value = fake_whatsapp_client

        yield  # ← pause here, test runs
        # PART 2 - after yield (cleanup)
        # 'with' block closes automatically here — real Client restored
        print("teardown — fake mock_gmail_to_whatsapp is removed")


@pytest.fixture(autouse=True)
def mock_voice_to_calendar():
    """
    this func is fixture - will be called by pytest package automatically
    'autouse' means context, this fixture (func mock_external_services) will be called for each test that will run without explicitly calling it by each test
    """

    print("PART 1 - SETUP - all before yield - creation of all fakes")

    # our fake chain is: connect, service.events.insert().execute()

    # 1. use function src.calendar_checker.connect_to_google_calendar to connect   <- this will be 'patched'
    # 2. service.                                                                  <- this will be 'mocked'
    # 3. events.
    # 4. insert()                                                                  <- this will be followed by return_value
    # 5. execute()                                                                 <- this will be followed by return_value, and we stop

    # at each place we see () means return_value
    # at each place we see . means concatenate (the mock will be done automatically)

    with patch('src.calendar_checker.connect_to_google_calendar') as fake_Google_Calendar_connect:
        """
        patch fakes the connect_to_google_calendar api that connects us to Google Calendar class 
        that produces Google_Calendar_class obj for us to use 
        that creates event        
        """
        # this is my real code: service.events().insert().execute(), so the chain must mimic the real chain of calls
        # return_value goes where we see ()
        fake_Google_Calendar_service = MagicMock()

        # configure what execute() returns
        fake_Google_Calendar_service.events.return_value.insert.return_value.execute.return_value = {"htmlLink": "https://calendar.google.com/mock-event-link"}

        # tell fake_connect: when connect_to_google_calendar() is called → return fake_service
        fake_Google_Calendar_connect.return_value = fake_Google_Calendar_service

        yield  # ← pause here, test runs

        # PART 2 - after yield (cleanup)
        # 'with' block closes automatically here — real Client is restored
        print("teardown — fake mock_voice_to_calendar is removed")