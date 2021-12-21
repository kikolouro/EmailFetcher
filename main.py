import imaplib
import time
import email
from datetime import datetime, time, date
import datetime
from email import message
from decouple import config, UndefinedValueError
import sys
import sendemail

def findValues(word):
    try:
        temp = [config(f'{word}{i}') for i in range(1, 50) if config(f'{word}{i}')]
    except UndefinedValueError as e:
        pass
    return temp


schedules = {
    1: [
        time(0, 00),
        time(3, 59),
    ],
    2: [
        time(4, 00),
        time(7, 59),
    ],
    3: [
        time(8, 00),
        time(11, 59),
    ],
    4: [
        time(12, 00),
        time(15, 59),
    ],
    5: [
        time(16, 00),
        time(19, 59),
    ],
    6: [
        time(20, 00),
        time(23, 59),
    ]
}


def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return check_time >= begin_time or check_time <= end_time


current_time = datetime.datetime.now().strftime("%H:%M:%S")

flag = True
while flag:
    for i, schedule in enumerate(schedules):
        #print(f"trying {schedules[i +1]}")
        if is_time_between(schedules[i + 1][0], schedules[i + 1][1], datetime.datetime.strptime(current_time, '%H:%M:%S').time()):
            timestamp = i + 1
            flag = not flag
try:
    imap_ssl = imaplib.IMAP4_SSL(host=config(
        'SMTP'), port=imaplib.IMAP4_SSL_PORT)

except Exception as e:
    print("ErrorType : {}, Error : {}".format(type(e).__name__, e))
    imap_ssl = None


print("imap_sslection Object : {}".format(imap_ssl))
print("Logging into mailbox...")
try:
    resp_code, response = imap_ssl.login(config('EMAIL'), config('PASSWORD'))
except Exception as e:
    print("ErrorType : {}, Error : {}".format(type(e).__name__, e))
    resp_code, response = None, None

print("Response Code : {}".format(resp_code))
print("Response      : {}\n".format(response[0].decode()))

imap_ssl.select('inbox')
today = date.today().strftime("%d-%b-%Y")
yesterday = (date.today() - datetime.timedelta(days=1)).strftime("%d-%b-%Y")
tomorrow = (date.today() + datetime.timedelta(days=1)).strftime("%d-%b-%Y")
logs = findValues('LOG')


def init(logs):
    return {log: {'count': 0, 'errors': ''} for log in logs}


def BodyTransform(body):

    temp = body.split("Operational data: ", 1)[1]
    body = temp.split("\r\n")[0]

    return str(body) + "\n"


obj = init(logs)
for i, log in enumerate(logs):

    try:
        emails = imap_ssl.search(
            None, f'(SUBJECT "Problem: Errors on {logs[i]} log" SINCE "{today} BEFORE {tomorrow}")')

        for x in emails[1][0].decode('utf-8').split(' '):

            result, data = imap_ssl.fetch(x, "(RFC822)")

            raw_email = data[0][1]

            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

            # print(email_message)
            date_tuple = email.utils.parsedate_tz(email_message['Date'])

            if date_tuple:
                local_date = datetime.datetime.fromtimestamp(
                    email.utils.mktime_tz(date_tuple))
                local_message_date = "%s" % (
                    str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
                message_time = "%s" % (str(local_date.strftime("%H:%M:%S")))

            if is_time_between(schedules[timestamp][0], schedules[timestamp][1], datetime.datetime.strptime(message_time, '%H:%M:%S').time()):

                email_from = str(email.header.make_header(
                    email.header.decode_header(email_message['From'])))
                email_to = str(email.header.make_header(
                    email.header.decode_header(email_message['To'])))
                subject = str(email.header.make_header(
                    email.header.decode_header(email_message['Subject'])))

                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)

                        obj[log]['count'] += 1
                        
                        obj[log]['errors'] += BodyTransform(body.decode('utf-8'))
                        # print("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\nBody: \n\n%s" % (
                        # email_from, email_to, local_message_date, subject, body.decode('utf-8')))
                    else:
                        continue
    except Exception as e:
        if 'FETCH parse error' in str(e):
            continue
        print("ErrorType : {}, Error : {}".format(type(e).__name__, e))

recipients = findValues('RECIPIENT')
sendemail.sendEmail(recipients, {'email': config(
    'SENDER_EMAIL'), 'password': config('SENDER_PASSWORD')}, obj)
