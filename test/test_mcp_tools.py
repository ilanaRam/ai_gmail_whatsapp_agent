import sys
import os
import asyncio
import src.mcp_server as mcp_obj


# ---------------------------------------------------------
# async def      This function may wait for something
# await          Wait here but don't block everything else
# asyncio.run()  Bridge from regular code to async code
# ---------------------------------------------------------

# async means:
# MCP tools run asynchronously — meaning they don't block while waiting for a response.
# to handle this asynchronous way Python has a package , called: asyncio

# by using "async" we tell Python: This function may have to wait for something — don't block everything else while waiting
async def test_check_email_tool():
    # Test tool_check_email
    print("Testing MCP tool tool_check_email()   ... directly()\n")

    # test calls mail checker func (now it is a tool that registered at mcp) it gives it a name of the tool (my func registered) and params

    # await means: "Wait for this to finish — but while waiting, let other things run"
    # await can be used only inside async function !!!
    # await is like a waiter that take orders and give a chef to prepare them, waiter (awaiter) does something else while a chef (async tool func) prepares the dish.
    result = await mcp_obj.my_mcp_server.call_tool("tool_check_email",                               # tool name
                                                    {                                                  # params that tool function receives:
                                                        "from_sender": "ilanaaprilloriram@gmail.com",  # from
                                                        "subject": "RRR"                               # mail title (subject)
                                                    })
    print(f"tool_check_email result: {result}\n")

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


async def test_send_whatsapp_tool():
    print("Testing MCP tool send_whatsapp_tool   ... directly()\n")

    result = await mcp_obj.my_mcp_server.call_tool("tool_send_whatsapp",                               # tool name
                                                    {                                                  # params that tool function receives:
                                                        "from_sender": "ilanaaprilloriram@gmail.com",  # from
                                                        "subject": "RRR"                               # mail title (subject)
                                                    })
    print(f"tool_check_email result: {result}\n")


async def test_connect_to_google_calendar_tool():
    print("Testing MCP tool connect_to_google_calendar ... directly()\n")

    result = await mcp_obj.my_mcp_server.call_tool("tool_connect_to_google_calendar", # tool name
                                                   {})                                # params
    print(f"connect_to_google_calendar_tool result: {result}\n")


if __name__ == "__main__":

    # Your normal main code is not async — it's regular code.
    # So from this regular code to call async function we need asyncio.run() - this will act as a bridge:

    # regular function ------- bridge-------- async function--->
    # main()           -> asyncio.run()   ->  test_check_mail_tool()

    #asyncio.run(test_check_email_tool())
    #asyncio.run(test_send_whatsapp_tool())
    asyncio.run(test_connect_to_google_calendar_tool())