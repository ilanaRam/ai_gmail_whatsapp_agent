from mcp.server.fastmcp import FastMCP # this class creates my MCP server
import threading # to run MCP server in a thread (9)as it is a blocking functionality)
import sys
import os
from src.mail_checker import check_email
from src.whatsapp_sender import send_whatsapp
from dotenv import load_dotenv

load_dotenv()



# Create the MCP server and give it a name
my_mcp_server = FastMCP("ai_gmail_whatsapp_agent")


# this function actually runs MCP server in the thread
def run_mcp_server():
    print("MCP Server thread is starting...")
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
    # tool_check_email actually wraps my function check_email() and returns it's result as a dictionary
    subject_result, sender_result = check_email(from_sender=from_sender, subject=subject)

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
    # tool_send_whatsapp actually wraps my function send_whatsapp() and returns it's result as a dictionary
    send_whatsapp(subject=subject, sender=from_sender)

    # good practice to return dict as AI tools easily work with dicts (read and understand dics)
    return {
            "status": "sent",
            "subject": subject,
            "sender": from_sender
           }


#upon running just the MCP server:
# (.venv) PS C:\Users\PRIVATE_ILANA\PHYTHON_HOW_TO\_repos\ai_gmail_whatsapp_agent> python .\src\mcp_server.py
#
# we should see this output:
# We are about to run MCP in a thread ...
# MCP Server thread is starting...
# Registered tools: ['tool_check_email', 'tool_send_whatsapp']



if __name__ == "__main__":
    print("We are about to run MCP in a thread ...")
    run_mcp_server()
    print(f"Registered tools: {[tool for tool in my_mcp_server._tool_manager._tools]}")

    # keep main thread alive so daemon thread keeps running
    while True:
        pass