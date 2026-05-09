
import imaplib                   # to work with imap protocol that makes receiving of the mails available
import email                     # to work with email
import inspect
from dotenv import load_dotenv
import os

load_dotenv()

# --- GMAIL CONFIGURATION ---
MY_EMAIL= os.getenv('MY_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD') # this is a password i created in my gmail account for Python application called 'AI agent'
IMAP_SERVER = os.getenv('IMAP_SERVER')

def check_email(from_sender,
                subject,):
    func_name = inspect.currentframe().f_code.co_name
    print(f"func: {func_name}() - called")

    try:
        # Connect to the gmail mail IMAP server (protocol IMAP to receive mails) in secure way (SSL)

        print(f"define an object to work with mail IMAP server of GMAIL")
        mail_gmail_server = imaplib.IMAP4_SSL(IMAP_SERVER)

        print(f"Using this object to login gmail mail server")
        mail_gmail_server.login(MY_EMAIL, EMAIL_PASSWORD)

        print(f"Connecting to inbox only of the gmail mail server")
        mail_gmail_server.select("inbox")

        print(f"Search for unread (UNSEEN) (=newly received) emails, of Subject: {subject}, from: {from_sender}")

        search_criteria = f'(UNSEEN SUBJECT "{subject}" FROM "{from_sender}")' # IMAP treats them as AND

        status, mails_respond = mail_gmail_server.search(None,
                                                         search_criteria) # here we search for UNSEEN (unreaded) mails and also with specific Subject
        if not mails_respond:
            print(f"There were NO new (UNSEEN) mails in gmail mail server ...")
            return None, None

        email_ids_list = mails_respond[0].split() # create a list of newly received mails  (later on I will learn how to listen for the only specific mails not to all

        # if there are newly receive mails, then act, else keep iterate
        if not email_ids_list:
            return None, None

        print(f"There were new mail/s in gmail mail server ... with Subject: {subject}")

        # !!!  take the latest unread mail that arrived ONLY
        email_id = email_ids_list[-1]

        print(f"Fetching the newly received messages data ...")
        # Fetch the email content from the server
        _, data = mail_gmail_server.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        ''' ==================== Explanation to what is RFC822 ========================
        RFC = Request for comments, in other wards it is a format of the mail. We define in what format we ask to get the mail from the server.
        
        If we will not define it, we might get just send you the size of the email or just the headers.
        By saying fetch(latest_email_id, '(RFC822)'), we tell Gmail: 
        "Give me the whole thing—the sender, the date, the subject, and the body—formatted exactly according to the international standard."
        
        Then we must convert a bytes (data) we get into the email obj into the email object (to be able to request from it the subject, the sender and so on)
        so we did: email.message_from_bytes(data[0][1])            
        ==============================================================================='''
        print(f"Looking for subject: {subject} ...")

        if any(item in subject.split()
               for item in msg['Subject'].split()):
            subject = msg['Subject']
        else:
            subject = None

        if MY_EMAIL in msg['From']:
            from_sender = msg['From']
        else:
            from_sender = None

        if subject and from_sender:
            print(f"New mail received with: \nSubject is: {subject}, received From: {from_sender}")

        # after each mail receive - log out
        mail_gmail_server.logout()

        # return any way
        return subject, from_sender
    except Exception as e:
        print(f"Error: {e}")
        return None, None  # Always return a pair so the caller doesn't crash!