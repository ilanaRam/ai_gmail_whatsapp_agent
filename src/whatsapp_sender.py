import inspect
from twilio.rest import Client   # to work with Twilio sandbox to send it whatsapp messages
from dotenv import load_dotenv
import os

load_dotenv()

TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
FROM_TWILIO_WHATSAPP_CONTACT_NUMBER = os.getenv('FROM_TWILIO_WHATSAPP_CONTACT_NUMBER')
TO_MY_WHATSAPP = os.getenv('TO_MY_WHATSAPP')




# once message (mail arrived to my gmail, it will be sent to my whatsapp, to my Twilio whatsapp contact
def send_whatsapp(subject,
                  sender):
    func_name = inspect.currentframe().f_code.co_name
    print(f"func: {func_name}() - called")

    # create a Twilio Client side
    print(f"define an Twilio client obj - to work with Twilio sandbox")
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    print(f"Twilio account SID: {client}")

    print(f"Preparing a message to be send to Twilio sandbox that will be sent by him to whatsapp")

    print(f"Message From: {sender}, with Subject: {subject}")
    message_body = f"📬 New Mail!\nFrom: {sender}\nSubject: {subject} "

    print(f"Message to be send. Message body: {message_body}")
    #TODO: suround with try and catch !!!!!!!!!!!!!
    message = client.messages.create(body=message_body,
                                     from_=FROM_TWILIO_WHATSAPP_CONTACT_NUMBER,
                                     to=TO_MY_WHATSAPP)
    print(f"Message sent! Message SID: {message.sid}")