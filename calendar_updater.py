import time
import inspect
import asyncio
import json
import os
import src.calendar_checker as my_calendar_manager # needed only for direct calling to apis

# for call of my apis (mcp tools, = via MCP server)
import src.mcp_server as mcp_obj

from dotenv import load_dotenv
load_dotenv()


async def mcp_main():
    """
    Flow: record voice → Whisper transcribe (Hebrew) → Gemini extracts structured event JSON → validate → create Google Calendar event.
    Runs once and exits

    Explanation about async def:
    When you write 'async def', you are telling Python: "This function will pause and wait for something at some point". This key promises a multitasking
    The way you pause and wait is with 'await' inside the function. key 'wait' actually makes switch to run other task (any other task)
    async def without await = false promise of multitasking

    'await' is needed when you call a function that does network/IO work and has been written as 'async def' itself.
    """
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    # create mcp server
    mcp_obj.run_mcp_server()

    # recording voice and converting to text
    result = await mcp_obj.my_mcp_server.call_tool("tool_record_voice_and_convert_voice_to_text",  # tool name
                                                   {})                                             # tool params
    data = json.loads(result[0].text)
    record_transcribe_status = data["status"]
    print(f"[{func_name}]: Record voice and convertion to text ... resulted with: {record_transcribe_status}")

    if record_transcribe_status == "failed":
        record_transcribe_error_details = data["error"]
        print(f"[{func_name}]: Failure details: {record_transcribe_error_details}")
    else:
        results_path = data["saved_folder"]
        print(f"[{func_name}]: Results path is: {results_path}")

        transcribed_text = data["transcribed_text"]

        analyze_result = await mcp_obj.my_mcp_server.call_tool("tool_analyze_text",       # tool name
                                                              {"text":transcribed_text})  # tool params
        print(f"[{func_name}]: Analyzing the text ... resulted with: {analyze_result}\n")

        if not analyze_result :
            print(f"[{func_name}]: Received empty result from text analyse ###")
        else:
            # Convert the raw JSON string into a proper Python dictionary - deserialization
            event_data_dict = json.loads(analyze_result[0].text)
            if event_data_dict['status'] == 'failed':
                print(f"[{func_name}]: Analyzing the text - Failed ###")
            else:
                # connect to google calendar service via mcp server
                result = await mcp_obj.my_mcp_server.call_tool("tool_set_google_calendar_event",          # tool name
                                                               {"event_data": event_data_dict['result']}) # tool params
                data = json.loads(result[0].text)
                status = data["status"]

                if status == "failed":
                    error_message = data["error"]
                    print(f"[{func_name}]: ### Connection to Google Calendar failed with error: {error_message} ###")
                else:
                    link = data["event_link"]
                    print(f"[{func_name}]: VVV Connection to Google Calendar succeeded, Link to Event: {link} VVVV")



if __name__ == "__main__":
    asyncio.run(mcp_main())
    time.sleep(5) # ← gives daemon thread time to finish cleanly