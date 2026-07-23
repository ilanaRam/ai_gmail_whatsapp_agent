import json
import sys
import os
import asyncio
import src.mcp_server as mcp_obj
import pytest

# ---------------------------------------------------------
# async def      This function may wait for something
# await          Wait here but don't block everything else
# asyncio.run()  Bridge from regular code to async code
# ---------------------------------------------------------

# async means:
# MCP tools run asynchronously — meaning they don't block while waiting for a response.
# to handle this asynchronous way Python has a package , called: asyncio

# by using "async" we tell Python: This function may have to wait for something — don't block everything else while waiting
@pytest.mark.asyncio
async def test_check_email_tool():
    # Test tool_check_email
    print("Testing MCP tool: check_email_tool()\n")

    # test calls mail checker func (now it is a tool that registered at mcp) it gives it a name of the tool (my func registered) and params

    # await means: "Wait for this to finish — but while waiting, let other things run"
    # await can be used only inside async function !!!
    # await is like a waiter that take orders and give a chef to prepare them, waiter (awaiter) does something else while a chef (async tool func) prepares the dish.
    result = await mcp_obj.my_mcp_server.call_tool("tool_check_email",                                 # tool name
                                                    {                                                  # params that tool function receives:
                                                        "from_sender": "ilanaaprilloriram@gmail.com",  # from
                                                        "subject": "RRR"                               # mail title (subject)
                                                    })
    data = json.loads(result[0].text)
    print(f"Result of the test for: tool_check_email: {data}")
    assert data['status'] == "received", f"❌ FAIL: The error is: {data['error']}"
    print(f"✅ PASS: Test behaved exactly as expected.")

    # we got the result:
    # tool_check_email result: [TextContent(type='text', text='{\n  "subject": null,\n  "sender": null\n}', annotations=None, meta=None)]
    # Explanation:
    # TextContent — this is how MCP wraps responses, it's a MCP response object
    # text='{\n  "subject": null,\n  "sender": null\n}' — this is the actual result, which in readable format is:
    # {
    #     "subject": null,
    #     "sender": null
    # }
    # because in my GMAIL were no fresh mail with Subject: "RRR", and from sender: "ilanaaprilloriram@gmail.com"
    # so returned null

    # I sent myself RRR and ran the test test_check_mail_tool() and  got this:
    # {
    #     "subject": "RRR",
    #     "sender": "ilana melnik <ilanaaprilloriram@gmail.com>"
    # }
    # in my GMAIL was fresh mail with Subject: "RRR", and from sender: "ilanaaprilloriram@gmail.com"

@pytest.mark.asyncio
async def test_send_whatsapp_tool():
    print("Testing MCP tool: send_whatsapp_tool()\n")

    result = await mcp_obj.my_mcp_server.call_tool("tool_send_whatsapp",                               # tool name
                                                    {                                                  # params that tool function receives:
                                                        "from_sender": "ilanaaprilloriram@gmail.com",  # from
                                                        "subject": "RRR"                               # mail title (subject)
                                                    })
    print(f"Result of the test for: tool_send_whatsapp: {result}\n")
    data = json.loads(result[0].text)
    assert data['status'] == "sent", f"❌ FAIL: The error is: {data['error']}"
    print(f"✅ PASS: Test behaved exactly as expected.")


@pytest.mark.asyncio
async def test_analyze_text_tool():
    print("Testing MCP tool: analyze_text_tool() \n")
    my_text = "היום אנו בתאריך 02/06/2026 בוא נקבע פגישה עם אלכס מחר בשעה שלוש אחר הצהריים לדון בפרויקט"

    result = await mcp_obj.my_mcp_server.call_tool("tool_analyze_text",  # tool name
                                                   {"text": my_text})    # params
    print(f"Result of the test for: tool_analyze_text: {result}\n")
    data = json.loads(result[0].text)
    assert data["status"] == "success", f"❌ FAIL: The error is: {data['error']}"
    print(f"Analyzed data is: {data["result"]}")
    print(f"✅ PASS: Test behaved exactly as expected.")



@pytest.mark.asyncio
async def test_create_google_calendar_event_tool_empty_data():
    print("Testing MCP tool: connect google calendar + create event with empty event data \n")

    """
    MCP:            throws a real exception (ToolError) — not a return value
    pytest.raises:  catches it and marks test as passed ✅
    Without it — the exception causes test to fail ❌
    """

    # we expect that mcp tool raise exception upon empty event - exception is correct behavior
    # so in case exception is expected behavior we must write this way only
    with pytest.raises(Exception) as exception_info:
        result = await mcp_obj.my_mcp_server.call_tool("tool_set_google_calendar_event",
                                                       {}) # empty — MCP will raise before function runs
        # we never reach here! upon exception the execution jumps out of with block immediately
    print(f"✅ PASS: Test behaved exactly as expected, expected exception error is: {exception_info}")



@pytest.mark.asyncio
async def test_create_google_calendar_event_tool_full_data():
    print("Testing MCP tool: create_google_calendar_event_tool() \n")

    print(f"Preparing Mock full and correct event data ...")
    mock_event_data = {
        'title': 'פגישה עם אלכס',
        "participants": ["Alex", "Ilana"],
        "my_calendar": True,
        "alex_calendar": True,
        'date': '2026-06-13',
        'time': '15:00',
        'duration_minutes': 60,
        'description': 'לדון בפרויקט העתידי המשותף',
        'alert_minutes_before': 30,
        "is_urgent": False
    }
    print(f"Mock event data is ready:\n{mock_event_data}")
    print(f"Creating the Google Calendar event ...")
    result = await mcp_obj.my_mcp_server.call_tool("tool_set_google_calendar_event", # tool name
                                                   {"event_data": mock_event_data})  # params
    print(f"Result of the test for: test_create_google_calendar_event_tool_full_data: {result}\n")
    data = json.loads(result[0].text)

    assert data['status'] == 'success', f"❌ FAIL: The error is: {data['error']}"
    print(f"Event message: : {data["message"]}, link to event: {data["event_link"]}")
    print(f"✅ PASS: Test behaved exactly as expected.")


async def create_google_calendar_event_tool_full_data(event_dict_test_data):
    print("Testing MCP tool: create_google_calendar_event_tool() \n")

    print(f"Mock (test) data is: {event_dict_test_data}")

    print(f"Creating the Google Calendar event ...")
    result = await mcp_obj.my_mcp_server.call_tool("tool_set_google_calendar_event", # tool name
                                                   {"event_data": event_dict_test_data})  # params
    print(f"Result of the test: {result}\n")
    return result


# Step 1 - Test cases:
TEST_CASES = [
                # missing fields cases
                {
                    "test_name": "Missing 'title' Field (Should Fail)",
                    "mock_test_data": {
                        # 'title': is commented out intentionally!
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-13",
                        "time": "15:00",
                        "duration_minutes": 60,
                        "description": "לדון בפרויקט העתידי המשותף",
                        "alert_minutes_before": 30,
                        "is_urgent": None
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'participants' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        #"participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'my_calendar' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        #"my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'alex_calendar' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        #"alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'date' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        #"date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'time' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        #"time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'duration_minutes' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        #"duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'description' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        #"description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'alert_minutes_before' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        #"alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Missing 'is_urgent' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        #"is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                # negative values
                {
                    "test_name": "Negative 'duration_minutes' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": -1,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 15,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Negative 'alert_minutes_before' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": -1,
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                # incorrect data type
                {
                    "test_name": "Wrong data type for 'alert_minutes_before' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 'Xa XA I am not an int',
                        "is_urgent": False
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                },
                {
                    "test_name": "Wrong data type for 'alert_minutes_before' Field (Should Fail)",
                    "mock_test_data": {
                        "title": "פגישה תקינה לחלוטין",
                        "participants": ["Alex", "Ilana"],
                        "my_calendar": True,
                        "alex_calendar": False,
                        "date": "2026-06-15",
                        "time": "10:00",
                        "duration_minutes": 45,
                        "description": "בדיקת מערכת תקינה",
                        "alert_minutes_before": 'Xa XA I am not an int',
                        "is_urgent": "XA XA I am not boolean"
                    },
                    "expected_test_status": "failed" # We expect your API or tool to handle this gracefully
                }
            ]

# Step 2 - Building the Parameterized Loop Function - that will run the above test cases
@pytest.mark.asyncio
async def test_create_google_calendar_event_tool_missing_fields():
    print("=== Starting Parameterized MCP Tool Tests, that will handle missing fields cases ===\n")

    # Manual loop through the global TEST_CASES list defined above - it is nice but not pythonic way
    for case in TEST_CASES:
        print(f"\n--- Running Test Case: {case['test_name']} ---")
        result = await create_google_calendar_event_tool_full_data(case)
        print(f"Result of the test case is: {result}\n")

        data = json.loads(result[0].text)
        assert data['status'] == case['expected_test_status'], f"❌ FAIL: expected '{case['expected_test_status']}' but got {data['status']}"

        if data['status'] == 'success':
            print(f"Event message: : {data["message"]}, link to event: {data["event_link"]}")
        print(f"✅ PASS: Test behaved exactly as expected.")
    print("\n=== All Test Cases Completed ===")



 # ============Pytest, Pythonic way ====================================
 # via DAta Driven, Parametrized, with decorator
 # a decorator (@pytest.mark.parametrize) to inject the parameters directly into the function arguments

# 1. Define the parameters layout (Keys, then a list of Tuples containing the data)
@pytest.mark.parametrize("test_case_name, mock_test_data_dict, expected_test_status",
                        [
                            # =================================================================
                            # 1. MISSING FIELDS
                            # =================================================================
                            (
                                "Missing data for 'title' Field (Should Fail)",
                                {
                                    "title": None,
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-13",
                                    "time": "15:00",
                                    "duration_minutes": 60,
                                    "description": "לדון בפרויקט העתידי המשותף",
                                    "alert_minutes_before": 30,
                                    "is_urgent": None
                                },
                                "failed"
                            ),
                            (
                                "Wrong data type for 'title' Field (Should Fail)",
                                {
                                    "title": 10,
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-13",
                                    "time": "15:00",
                                    "duration_minutes": 60,
                                    "description": "לדון בפרויקט העתידי המשותף",
                                    "alert_minutes_before": 30,
                                    "is_urgent": None
                                },
                                "failed"
                            ),
                            (
                                "Missing 'participants' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing data for 'participants' Field (Should Fail)",
                                {
                                    "participants": None,
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
(
                                "Wrong data type for 'participants' Field (Should Fail)",
                                {
                                    "participants": 10,
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing 'my_calendar' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing 'alex_calendar' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing 'date' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing data for 'date' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": None,
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Wrong data type for 'date' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": 10,
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing 'time' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing data for 'time' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": None,
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing data type for 'time' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": 10,
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing 'duration_minutes' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "None 'duration_minutes' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": None,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing 'description' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "None 'description' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "description": None,
                                    "duration_minutes": 45,
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing 'alert_minutes_before' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    #"alert_minutes_before": 15,
                                    "description": "בדיקת מערכת תקינה",
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Missing 'is_urgent' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15
                                },
                                "failed"
                            ),
                            # =================================================================
                            # 2. NEGATIVE VALUES
                            # =================================================================
                            (
                                "Negative 'duration_minutes' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": -1,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Negative 'alert_minutes_before' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": -1,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Wrong data type for 'alert_minutes_before' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 'Xa XA I am not an int',
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "None data for 'alert_minutes_before' Field (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": None,
                                    "is_urgent": False
                                },
                                "failed"
                            ),
                            (
                                "Invalid String Type for 'is_urgent' (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": "XA XA I am not boolean"
                                },
                                "failed"
                            ),
                            (
                                "None data for 'is_urgent' (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": None
                                },
                                "failed"
                            ),
                            (
                                "None data for 'is_urgent' (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": 15,
                                    "is_urgent": None
                                },
                                "failed"
                            ),
                            (
                                "None data for 'is_urgent' (Should Fail)",
                                {
                                    "title": "פגישה תקינה לחלוטין",
                                    "participants": ["Alex", "Ilana"],
                                    "my_calendar": True,
                                    "alex_calendar": False,
                                    "date": "2026-06-15",
                                    "time": "10:00",
                                    "duration_minutes": 45,
                                    "description": "בדיקת מערכת תקינה",
                                    "alert_minutes_before": None,
                                    "is_urgent": None
                                },
                                "failed"
                            )
                        ])
# 2. Tell pytest that this is an async test block - explicitly by adding this: @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_create_google_calendar_event_tool_parameterized(test_case_name, mock_test_data_dict, expected_test_status):
    print(f"\n--- Framework Injected Test Case: {test_case_name} ---")

    print(f"Creating the Google Calendar event ...")
    result = await mcp_obj.my_mcp_server.call_tool("tool_set_google_calendar_event",
                                                    {"event_data": mock_test_data_dict}
                                                  )
    data = json.loads(result[0].text)
    assert data['status'] == expected_test_status, f"❌ FAIL: expected '{expected_test_status}' but got {data['status']}"

    if data['status'] == 'success':
        print(f"Event message: : {data["message"]}, link to event: {data["event_link"]}")
    print(f"✅ PASS: Test behaved exactly as expected.")

def test_2d_list_print():
    #          0 1 2
    my_list = [1,2,3, # 0
               4,5,6, # 1
               7,8,9] # 2
    # row: 0, col (1,2,3)
    # row: 1, col (4,5,6)
    # row: 2, col (7,8,9)
    N=3
    for row in range(N): # 0 1 2
        for col in range(N): # 0,1,2
            print(f"\nthe row is {row}")
            # col shifted by 3 , (row*3 is a shift)
            # in row = 0 we get: [0]=1,[1]=2,[2]=3
            # in row 1 we get: 3+0,3+1,3+2 ([3]=4,[4]=5,[5]=6)
            # in row 2 we get: 6+0,6+1,6+2 ([6]=7,[7]=8,[8]=9)
            col = (row*N) + col  # < ----------------------------------------------- @!!!!@
            print(f"the column is {col}")
            print(f" @@@@@@ the val is {my_list[col]}")




