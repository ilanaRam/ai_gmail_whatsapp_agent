import inspect
from twilio.rest import Client   # to work with Twilio sandbox to send it whatsapp messages
from dotenv import load_dotenv
import os

"""
This is a whatsapp message sender - is knows only about Whatsapp, it knows nothing about the MCP 
it will work even if we never connect MCP 
it is called "Separation of Concerns"
"""


load_dotenv()


TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_CONTACT_NUMBER = os.getenv('TWILIO_WHATSAPP_CONTACT_NUMBER')
MY_WHATSAPP_CONTACT_NUMBER = os.getenv('MY_WHATSAPP_CONTACT_NUMBER')




# once message (mail arrived to my gmail, it will be sent to my whatsapp, to my Twilio whatsapp contact
def send_whatsapp(subject,
                  sender):
    """
    this function does:
    1. creates client of Twillio to work with Twillio (to send via Twillio whatsapp messages to the contact)
    2. use api create (to send) whatsapp messages
    3. print message_sid as a result of send
    """
    func_name = inspect.currentframe().f_code.co_name
    print(f"func: {func_name}() - called")

    # create a Twilio Client side
    print(f"define 'real' Twilio client connection obj - to work with Twilio sandbox")
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    print(f"Twilio account SID: {client}")

    print(f"Preparing a message to be send to Twilio sandbox that will be sent by him to whatsapp")

    print(f"Message From: {sender}, with Subject: {subject}")
    message_body = f"📬 New Mail arrived!\n   From: {sender}\n   Subject: {subject} "
    print(f"Message body is: {message_body}")

    print(f"I am about making a 'real' sending of the 'real' whatsapp message ...")
    try:
        message = client.messages.create(body=message_body,
                                         from_=TWILIO_WHATSAPP_CONTACT_NUMBER,
                                         to=MY_WHATSAPP_CONTACT_NUMBER)
        print(f"Message sent! Message SID: {message.sid}")

        return {"status": "sent",
                "message_sid": message.sid}

    except Exception as e:
        print(f"Error: failed to send WhatsApp message: {e}")

        return {"status": "failed",
                "error": str(e)}