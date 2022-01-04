import imaplib
import time
import email
from datetime import datetime, time, date
import datetime
from email import message
from decouple import config, UndefinedValueError
import sys
from functions import is_time_between, isToday
import sendemail

def BodyTransformlog(body):

    temp = body.split("Operational data: ", 1)[1]
    body = temp.split("\r\n")[0]

    return str(body) + "\n"


def BodyTransformZabbix(body):
    id = body.split("Original problem ID: ", 1)[1].split("\r\n")[0]
    name = body.split("Problem name: ", 1)[1].split("\r\n")[0]
    host = body.split("Original problem ID: ", 1)[1].split("\r\n")[0]
    severity = body.split("Original problem ID: ", 1)[1].split("\r\n")[0]
    data = body.split("Operational data: ", 1)[1].split("\r\n")[0]

    return {
        "id": id,
        "name": name,
        "host": host,
        "severity": severity,
        "data": data
    }


def emailHandler(obj, logs, today, tomorrow, schedules, imap_ssl, timestamp, title, islog=None):
    _ = imap_ssl.recent()
    if islog:
        for i, log in enumerate(logs):
            try:
                emails = imap_ssl.search(
                    None, f'(SUBJECT "Problem: Errors on {logs[i]} log" SINCE "{today} BEFORE {tomorrow}")')
                print(emails)

                for x in emails[1][0].decode('utf-8').split(' '):

                    result, data = imap_ssl.fetch(x, "(RFC822)")

                    raw_email = data[0][1]

                    raw_email_string = raw_email.decode('utf-8')
                    email_message = email.message_from_string(raw_email_string)

                    date_tuple = email.utils.parsedate_tz(
                        email_message['Date'])

                    if date_tuple:
                        local_date = datetime.datetime.fromtimestamp(
                            email.utils.mktime_tz(date_tuple))
                        local_message_date = "%s" % (
                            str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
                        message_time = "%s" % (
                            str(local_date.strftime("%H:%M:%S")))

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

                                obj[log]['errors'].append(
                                    BodyTransformlog(body.decode('utf-8')))

                            else:
                                continue
            except Exception as e:
                if 'FETCH parse error' in str(e):
                    continue
                print("ErrorType : {}, Error : {}".format(type(e).__name__, e))
    else:
        try:
            _, emails = imap_ssl.search(None, "ALL")
            for x in emails[0].decode('utf-8').split(' '):
                result, data = imap_ssl.fetch(x, "(RFC822)")
                raw_email = data[0][1]
                # print(raw_email)
                raw_email_string = raw_email.decode('utf-8')
                email_message = email.message_from_string(raw_email_string)

                date_tuple = email.utils.parsedate_tz(email_message['Date'])

                if date_tuple:
                    local_date = datetime.datetime.fromtimestamp(
                        email.utils.mktime_tz(date_tuple))
                    local_message_date = "%s" % (
                        str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
                    message_time = "%s" % (
                        str(local_date.strftime("%H:%M:%S")))
                #print(email_message['Subject'])
                if is_time_between(schedules[timestamp][0], schedules[timestamp][1], datetime.datetime.strptime(message_time, '%H:%M:%S').time()) and isToday(local_date.date()):

                    email_from = str(email.header.make_header(
                        email.header.decode_header(email_message['From'])))
                    email_to = str(email.header.make_header(
                        email.header.decode_header(email_message['To'])))
                    subject = str(email.header.make_header(
                        email.header.decode_header(email_message['Subject'])))
                    if " Log" not in email_message['Subject'] and " log" not in email_message['Subject']:
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True)
                                obj['count'] += 1
                                print(BodyTransformZabbix(
                                    body.decode('utf-8')))
                                obj['errors'].append(
                                    BodyTransformZabbix(body.decode('utf-8')))
                    else:
                        continue
        except Exception as e:
            if 'FETCH parse error' in str(e):
                print("ErrorType : {}, Error : {}".format(type(e).__name__, e))
    return obj
