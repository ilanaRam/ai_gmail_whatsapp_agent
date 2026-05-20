import time
import inspect
import os
import asyncio
import json

# for direct call to my apis (not mcp tools, = not via MCP server)
import src.whatsapp_sender as whatsapp_obj
import src.mail_checker as mail_checker_obj

# for call of my apis (mcp tools, = via MCP server)
import src.mcp_server as mcp_obj

from dotenv import load_dotenv


load_dotenv()

MY_EMAIL = os.getenv('MY_EMAIL')

def get_user_input():
    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    print(f"{func_name}: !!! dont forget to send every 24H from your Twilio contact in your whatsapp, this message: 'join deal-clearly' ")

    expected_subject = input("Please enter 'Subject' of the mail you wait to receive: ")
    if not expected_subject or not expected_subject.strip():
        print(f"{func_name}: were not received a Subject of the expected mail, will be awaiting for default Subject None ")
        return "RRR"
    else:
        print(f"{func_name}: were received a Subject of the expected mail: {expected_subject.strip()}, agent will wait to receive this mail\n\n")
        return expected_subject



# direct call to apis - not via mcp server (not mcp tools)
def direct_main():
    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    expected_subject = get_user_input()

    while True:
        print(f"{func_name}: wait for: 5sec before next mail check")
        time.sleep(5)

        mail_subject, mail_sender = mail_checker_obj.check_email(from_sender=MY_EMAIL,
                                                                 subject=f"{expected_subject}")
        if mail_subject and mail_sender and mail_subject == expected_subject and mail_sender == MY_EMAIL:
            whatsapp_obj.send_whatsapp( mail_subject, mail_sender)
        else:
            print(f"{func_name}: NOTHING TO SEND TO WHATSAPP !!!!\n")


async def mcp_main():
    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    expected_subject = get_user_input()

    result = None
    # mcp server thread is will be called - it will run in parallel, it will perform a registration of my apis as mcp tools by itself
    mcp_obj.run_mcp_server()

    while True:
        print(f"{func_name}: wait for: 5sec before next mail check")
        time.sleep(5)

        result = await mcp_obj.my_mcp_server.call_tool("tool_check_email",  # tool name
                                                      {  # params that tool function receives:
                                                          "from_sender": MY_EMAIL,  # from
                                                          "subject": f"{expected_subject}"  # mail title (subject)
                                                      })
        # tool returns a dict, here we unbox the dict:
        # {
        #     "subject": subject_result,
        #     "sender": sender_result
        # }
        print(f"tool_check_email result: {result}\n")
        data = json.loads(result[0].text)
        mail_subject = data["subject"]
        mail_sender = data["sender"]
        print(f"tool_check_email result details: mail_subject = {mail_subject}, mail_sender = {mail_sender}\n")

        if not mail_subject or not mail_sender:
            print(f"No Relevant mail, continue listening ...")
            continue

        if mail_subject and mail_sender and mail_subject == expected_subject and mail_sender == MY_EMAIL:
            result = await mcp_obj.my_mcp_server.call_tool("tool_send_whatsapp",  # tool name
                                                           {  # params that tool function receives:
                                                               "from_sender": mail_sender,  # from
                                                               "subject":  f"{mail_subject}"  # mail title (subject)
                                                           })
            # tool returns a dict, here we unbox the dict:
            # {
            #     "status": "sent",
            #     "subject": subject,
            #     "sender": from_sender
            # }
            print(f"tool_send_whatsapp result: {result}\n")
            data = json.loads(result[0].text)
            status = data["status"]
            mail_subject = data["subject"]
            mail_sender = data["sender"]
            print(f"tool_send_whatsapp result details: mail_subject = {mail_subject}, mail_sender = {mail_sender}, status = {status}\n")
        else:
            print(f"{func_name}: NOTHING TO SEND TO WHATSAPP !!!!\n")


if __name__ == "__main__":
    #direct_main() # the one that doesnt use mcp tools
    asyncio.run(mcp_main()) # the one that doesnt use mcp tools