
import time
import inspect
import os

import src.whatsapp_sender as whatsapp_obj
import src.mail_checker as mail_checker_obj
from src.mcp_server import *



load_dotenv()

MY_EMAIL = os.getenv('MY_EMAIL')

def get_user_input():
    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    print(f"{func_name}: !!! dont forget to send every 24H from your Twilio contact in your whatsapp, this message: 'join deal-clearly' ")

    expected_subject = input("Please enter 'Subject' of the mail you wait to receive: ")
    if not expected_subject or not expected_subject.strip():
        print(f"{func_name}: were not received a Subject of the expected mail, will be awaiting for default Subject 'RRR' ")
    else:
        print(f"{func_name}: were received a Subject of the expected mail: {expected_subject.strip()}, agent will wait to receive this mail\n\n")




def main():
    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    expected_subject = get_user_input()

    # mcp server thread is inside
    run_mcp_server()

    while True:
        print(f"{func_name}: wait for: 5sec before next mail check")
        time.sleep(5)

        mail_subject, mail_sender = mail_checker_obj.check_email(from_sender=MY_EMAIL,
                                                       subject=f"{expected_subject}")
        if mail_subject and mail_sender and mail_subject == expected_subject and mail_sender == MY_EMAIL:
            whatsapp_obj.send_whatsapp( mail_subject, mail_sender)
        else:
            print(f"{func_name}: NOTHING TO SEND TO WHATSAPP !!!!\n")



if __name__ == "__main__":
    main()