# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

import email
import imaplib
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import List

from src.secrets.credentials import EMAIL_ADDRESS, EMAIL_PASSWORD


# DIVIDER: --------------------------------------
# INFO: Mail Concrete Class

class MailBox:
    def __init__(self, smtp_ssl_host: str = 'smtp.gmail.com', smtp_ssl_port: int = 465,
                 imap_ssl_host: str = 'imap.gmail.com', imap_ssl_port: int = 993,
                 email: str = EMAIL_ADDRESS, password: str = EMAIL_PASSWORD):

        self._smtp_ssl_host = smtp_ssl_host
        self._smtp_ssl_port = smtp_ssl_port
        self._imap_ssl_host = imap_ssl_host
        self._imap_ssl_port = imap_ssl_port
        self._email = email
        self._password = password

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassType: {}'.format(type(self).__name__))
        tojoin.append('SMTP_SSL_Host: {}'.format(self._smtp_ssl_host))
        tojoin.append('SMTP_SSL_Port: {}'.format(self._smtp_ssl_port))
        tojoin.append('IMAP_SSL_Host: {}'.format(self._imap_ssl_host))
        tojoin.append('IMAP_SSL_Port: {}'.format(self._imap_ssl_port))
        censored_email = str(self._email).replace(str(self._email)[4:-4],
                                                  '*' * len(str(self._email)[4:-4]))
        censored_pass = str(self._password).replace(str(self._password)[:],
                                                    '*' * len(str(self._password)[:]))
        tojoin.append('Email: {}'.format(censored_email))
        tojoin.append('Pass: {}'.format(censored_pass))

        return ', '.join(tojoin)

    def send_mail(self, subject: str, message: str, to_emails: List[str]):
        # Try to log in to server and send email
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self._smtp_ssl_host, self._smtp_ssl_port, context=context) as server:
            try:
                # print("Logging into mailbox...")
                # resp_code, response = server.login(self.email, self.password)
                # print("Response Code : {}".format(resp_code))
                # print("Response      : {}\n".format(response[0].decode()))
                server.login(self._email, self._password)

                # TODO: Send email here
                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['From'] = self._email
                msg['To'] = ', '.join(to_emails)

                server.sendmail(from_addr=self._email, to_addrs=to_emails, msg=msg.as_string())

            except smtplib.SMTPException as err:
                # Print any error messages to stdout
                raise Exception(f"Error: unable to send email - {err}")

    def read_latest(self, from_sender: str = '', subject_title: str = '', is_unread: bool = False):
        # Try to log in to server and read emails
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with imaplib.IMAP4_SSL(host=self._imap_ssl_host, port=self._imap_ssl_port, ssl_context=context) as server:
            try:
                # print("Logging into mailbox...")
                # resp_code, response = server.login(self.email, self.password)
                # print("Response Code : {}".format(resp_code))
                # print("Response      : {}\n".format(response[0].decode()))
                server.login(self._email, self._password)

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
                if mail_ids:
                    last_id = mail_ids[-1]
                else:
                    raise ValueError(f'Target email not found (Subject: {subject_title}, From: {subject_title})')
                resp_code, mail_data = server.fetch(last_id, '(RFC822)')  # Fetch mail data.

                received_message = email.message_from_bytes(mail_data[0][1])  # Construct Message from mail data
                server.store(last_id, "+FLAGS", "\\Seen")
                server.store(last_id, "+FLAGS", "\\Deleted")
                # permanently remove mails that are marked as deleted
                # from the selected mailbox (in this case, INBOX)
                server.expunge()
                # close the mailbox
                server.close()
                # logout from the account
                server.logout()
                return {
                    'from': received_message.get("From"),
                    'date': received_message.get("Date"),
                    'subject': received_message.get("Subject"),
                    'payload': received_message.get_payload(0)._payload
                }

            except imaplib.IMAP4.error as err:
                # Print any error messages to stdout
                raise Exception(f"Error: unable to read email - {err}")


# DIVIDER: --------------------------------------
# INFO: Usage Examples


if __name__ == '__main__':
    is_to_run_test = True

    if is_to_run_test:
        is_read = True
        mailbox = MailBox()
        print(mailbox)
        if is_read:
            data = mailbox.read_latest(from_sender='support@wealthsimple.com',
                                       subject_title='Wealthsimple verification code', is_unread=False)

            pattern = re.compile(r'Wealthsimple:<br><br>\r\n\r\n(.*?)\r\n\r\nThis code will')
            content = pattern.findall(data['payload'])[0]
            censored_content = str(content).replace(str(content)[1:-1], '*' * len(str(content)[1:-1]))
            print(f'Content Received: {censored_content}')
        else:
            # send email
            to_email = 'tungstudies@gmail.com'
            to_sms = '5146388811@msg.telus.com'
            import datetime

            subject = f'This is a test email sent at {datetime.datetime.now().isoformat()}'
            message = 'Hello, World!'

            mailbox.send_mail(subject, message, [to_email, to_sms])

    else:
        pass
