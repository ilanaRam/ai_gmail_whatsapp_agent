import time
import inspect
import asyncio
import json
import src.calendar_checker as my_calendar_manager # needed only for direct calling to apis

# for call of my apis (mcp tools, = via MCP server)
import src.mcp_server as mcp_obj

from dotenv import load_dotenv
load_dotenv()


async def mcp_main():
    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    mcp_obj.run_mcp_server()

    result = await mcp_obj.my_mcp_server.call_tool("tool_connect_to_google_calendar",  # tool name
                                                   {})
    print(f"{func_name}:Result: {result}\n")
    data = json.loads(result[0].text)
    connection_status = data["status"]

    print(f"{func_name}:Connection status: {connection_status}")


if __name__ == "__main__":
    asyncio.run(mcp_main())
    time.sleep(5)  # ← gives daemon thread time to finish cleanly