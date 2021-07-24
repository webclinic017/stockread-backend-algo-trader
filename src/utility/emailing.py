import email
import imaplib
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import List

from src.secrets.credentials import SMTP_SSL_HOST, IMAP_SSL_HOST, SMTP_SSL_PORT, IMAP_SSL_PORT, EMAIL_ADDRESS, \
    EMAIL_PASSWORD


class MailBox:
    def __init__(self):
        self.smtp_ssl_host = SMTP_SSL_HOST
        self.smtp_ssl_port = SMTP_SSL_PORT
        self.imap_ssl_host = IMAP_SSL_HOST
        self.imap_ssl_port = IMAP_SSL_PORT
        self.email = EMAIL_ADDRESS
        self.password = EMAIL_PASSWORD

    def send_mail(self, subject: str, message: str, to_emails: List[str]):
        # Try to log in to server and send email
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_ssl_host, self.smtp_ssl_port, context=context) as server:
            try:
                # print("Logging into mailbox...")
                # resp_code, response = server.login(self.email, self.password)
                # print("Response Code : {}".format(resp_code))
                # print("Response      : {}\n".format(response[0].decode()))
                server.login(self.email, self.password)

                # TODO: Send email here
                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['From'] = self.email
                msg['To'] = ', '.join(to_emails)

                server.sendmail(from_addr=self.email, to_addrs=to_emails, msg=msg.as_string())
                return True, 'Message Sent'

            except smtplib.SMTPException as err:
                # Print any error messages to stdout
                print(f"Error: unable to send email - {err}")

                return False, 'Message Failed to Send'

    def read_latest(self, from_sender: str = '', subject_title: str = '', is_unread: bool = False):
        # Try to log in to server and read emails
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with imaplib.IMAP4_SSL(host=self.imap_ssl_host, port=self.imap_ssl_port, ssl_context=context) as server:
            try:
                # print("Logging into mailbox...")
                # resp_code, response = server.login(self.email, self.password)
                # print("Response Code : {}".format(resp_code))
                # print("Response      : {}\n".format(response[0].decode()))
                server.login(self.email, self.password)

                # Select mailbox
                server.select(mailbox="INBOX", readonly=False)

                factors = list()

                if is_unread:
                    factors.append('UNSEEN')

                if from_sender:
                    factors.append(f'HEADER FROM "{from_sender}"')

                if subject_title:
                    factors.append(f'SUBJECT "{subject_title}"')

                search_query = ' '.join(map(str, factors))

                if str(search_query).strip():
                    search_query = f'({search_query})'
                else:
                    search_query = None

                resp_code, messages = server.search(None, search_query)

                mail_ids = messages[0].decode().split()
                last_id = mail_ids[-1]

                resp_code, mail_data = server.fetch(last_id, '(RFC822)')  ## Fetch mail data.

                message = email.message_from_bytes(mail_data[0][1])  ## Construct Message from mail data
                server.store(last_id, "+FLAGS", "\\Seen")
                server.store(last_id, "+FLAGS", "\\Deleted")
                # permanently remove mails that are marked as deleted
                # from the selected mailbox (in this case, INBOX)
                server.expunge()
                # close the mailbox
                server.close()
                # logout from the account
                server.logout()
                return True, {
                    'from': message.get("From"),
                    'date': message.get("Date"),
                    'subject': message.get("Subject"),
                    'payload': message.get_payload(0)._payload
                }

            except imaplib.IMAP4.error as err:
                # Print any error messages to stdout
                print(f"Error: unable to send email - {err}")

                return False, {'error': 'Message Failed to Read'}


if __name__ == '__main__':
    # pass
    # my_email = 'tungstudies@gmail.com'
    # my_sms = '5146388811@msg.telus.com'
    # subject = 'Hello Test'
    # message = 'Test Hello'
    mailbox = MailBox()

    # mailbox.send_mail(subject, message, [my_email, my_sms])

    _, data = mailbox.read_latest(from_sender='support@wealthsimple.com',
                                  subject_title='Wealthsimple verification code', is_unread=False)

    print(data)
    pattern = re.compile(r'Wealthsimple:<br><br>\r\n\r\n(.*?)\r\n\r\nThis code will')
    print(pattern.findall(data['payload'])[0])
