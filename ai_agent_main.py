
import time
import inspect

import src.whatsapp_sender as whatsapp_obj
import src.mail_waiter as mail_waiter_obj

MY_EMAIL= 'ilanaaprilloriram@gmail.com'


def main():
    func_name = inspect.currentframe().f_code.co_name
    print(f"{func_name}: called")

    while True:
        subject, sender = mail_waiter_obj.check_email(from_sender=MY_EMAIL,
                                                      subject='RRR')
        if subject and sender:
            time.sleep(5)
            whatsapp_obj.send_whatsapp(subject, sender)
        else:
            print(f"{func_name}: NOTHING TO SEND TO WHATSAPP !!!!\n")



if __name__ == "__main__":
    main()