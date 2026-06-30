import json
import inspect

from mcp.server.fastmcp import FastMCP # this class creates my MCP server
import threading # to run MCP server in a thread (9)as it is a blocking functionality)
import sys
import os
#from src.mail_checker import check_email
# from src.whatsapp_sender import send_whatsapp
# from src.calendar_checker import connect_to_google_calendar
import src.mail_checker as check_email
import src.whatsapp_sender as send_whatsapp
import src.calendar_checker as calendar
import src.ai_analyzer as ai_analyzer
import src.voice as voice



from dotenv import load_dotenv
load_dotenv()

# Create the MCP server and give it a name
my_mcp_server = FastMCP("ai_gmail_whatsapp_agent")


# this function actually runs MCP server in the thread
def run_mcp_server():
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    print(f"[{func_name}]: MCP Server thread is starting...")
    # run function 'in a thread' (start MCP server in a background thread)
    mcp_thread = threading.Thread(target=my_mcp_server.run)
    mcp_thread.daemon = True  # thread will stop when main stops
    mcp_thread.start()  # start the threads - here will be called mcp.run()

# tool_check_email is a wrapper function that also decorated by mcp server to be called as a mcp tool
# why we need a wrapper - why we cannot decorate directly the check_email? Because we wish to make "Separation of Concerns"
# check_email() can be called directly when we work without MCP server or as a MCP tool

# @ means => decorator, the wrapper func is now decorated to act as a MCP tool
# tool() is api of the class FastMCP that registers this api as a tool
# tell MCP object (my_mcp_server) to register this function as a tool that AI can use
@my_mcp_server.tool()
def tool_check_email(from_sender: str, subject: str):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    # tool_check_email actually wraps my function check_email() and returns it's result as a dictionary
    subject_result, sender_result = check_email.check_email(from_sender=from_sender, subject=subject)

    # good practice to return dict as AI tools easily work with dicts (read and understand dics)
    return {
            "subject": subject_result,
            "sender": sender_result
           }

# tool_send_whatsapp is a wrapper function that also decorated by mcp server to be called as a mcp tool
# why we need a wrapper - why we cannot decorate directly the send_whatsapp? Because we wish to make "Separation of Concerns"
# send_whatsapp() can be called directly when we work without MCP server or as a MCP tool

# @ means => decorator, the wrapper func is now decorated to act as a MCP tool
# tool() is api of the class FastMCP that registers this api as a tool
# tell MCP object (my_mcp_server) to register this function as a tool that AI can use
@my_mcp_server.tool()
def tool_send_whatsapp(from_sender: str, subject: str):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    # tool_send_whatsapp actually wraps my function send_whatsapp() and returns it's result as a dictionary
    send_whatsapp.send_whatsapp(subject=subject, sender=from_sender)

    # good practice to return dict as AI tools easily work with dicts (read and understand dics)
    return {
            "status": "sent",
            "subject": subject,
            "sender": from_sender
           }


@my_mcp_server.tool()
async def tool_record_voice_and_convert_voice_to_text() -> dict:
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")
    """
    Records audio from the user's microphone array/headset, automatically detects
    silence to stop, and returns the transcribed Hebrew text via Whisper.
    """
    try:
        # 1. Secure the shared directory path
        results_path = voice.create_results_subfolder()

        # 2. Run the recording stream
        result_wav_file_path = voice.record_voice(results_path=results_path)

        if not result_wav_file_path or not os.path.exists(result_wav_file_path):
            return {"status": "failed",
                    "error": "No audio data captured or hardware timeout."
                   }

        # 3. Transcribe immediately using Whisper
        resulted_text_path = voice.convert_voice_to_text(audio_file=result_wav_file_path,
                                                         results_path=results_path)
        if not resulted_text_path or not os.path.exists(resulted_text_path):
            return {"status": "failed",
                    "error": "Whisper failed to transcribe audio to text and text file failed to be created."
                   }

        # Read the generated text asset to pass back to the agent
        with open(resulted_text_path, "r", encoding="utf-8") as f:
            final_text = f.read()

        return {
                "status": "success",
                "transcribed_text": final_text, # !!!! mcp tool returns the text directly to the ai analyzer that will work after him
                "saved_folder": results_path
               }
    except Exception as e:
        return {"status": "failed",
                "error": str(e)}

@my_mcp_server.tool()
def tool_analyze_text(text):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")
    # tool_analyze_text actually wraps my function analyze_text() and should returns it's result as a dictionary

    # Pay attention we receive a python obj DICT here
    analyzed_data = ai_analyzer.analyze_text(text)

    # mcp tool can return DICT
    return analyzed_data


@my_mcp_server.tool()
def tool_set_google_calendar_event(event_data: dict):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    try:
        # Connects to Google Calendar service
        connecting_obj = calendar.connect_to_google_calendar()
        if not connecting_obj:
            return {"status": "failed",
                    "error": "connection to google calendar service - Failed"
                    }
        # set new google calendar event
        event = calendar.create_google_calendar_event(google_calendar_event_data=event_data,
                                                      google_calendar_service=connecting_obj)
        if not event:
            return {"status": "failed",
                    "error": "creation of the google calendar event - Failed"
                    }
        return {"status": "success",
                "message": "Event inserted successfully onto primary grid!",
                "event_link": event.get('htmlLink')
               }
    except Exception as e:
        return {"status": "failed",
                "error": str(e)}


# upon running just the MCP server:
# (.venv) PS C:\Users\PRIVATE_ILANA\PHYTHON_HOW_TO\_repos\ai_gmail_whatsapp_agent> python .\src\mcp_server.py
#
# we should see this output:
# We are about to run MCP in a thread ...
# MCP Server thread is starting...
# Registered tools: ['tool_check_email', 'tool_send_whatsapp']



if __name__ == "__main__":
    print("We are about to run MCP in a thread ...")

    run_mcp_server()

    print(f"Registered tools: {[tool 
                                for tool in my_mcp_server._tool_manager._tools]}")

    # keep main thread alive so daemon thread keeps running
    while True:
        pass