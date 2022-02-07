import imaplib
import time
import email
from datetime import datetime, time, date
import datetime
from email import message
from decouple import config, UndefinedValueError
import sys
from emailhandler import emailHandler
from functions import is_time_between
import sendemail
import pprint
from datahandler import dataHandler

def findValues(word):
    try:
        temp = []
        for i in range(1, 50):
            if config(f'{word}{i}'):
                temp.append(config(f'{word}{i}'))
    except UndefinedValueError as e:
        pass
    return temp

def init(logs):
    return {log: {'count': 0, 'errors': []} for log in logs}

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

titles = [
    "4 Hour summary of zabbix problems",
    "Errors on log Files"
]

current_time = datetime.datetime.now()

current_time = current_time - datetime.timedelta(minutes=1)

current_time = current_time.strftime("%H:%M:%S")

logs = findValues('LOG')
recipients = findValues('RECIPIENT')
pp = pprint.PrettyPrinter(indent=4)

for title in titles:
    if 'log' in title:
        #obj = init(logs)    
        #obj = emailHandler(obj, logs, today, tomorrow, schedules, imap_ssl, timestamp, title, islog=True)
        obj = dataHandler()
        #pp.pprint(obj)
    elif 'zabbix' in title:
        obj = {
            "count": 0,
            "errors": []
        }
        #obj = emailHandler(obj, logs, today, tomorrow, schedules, imap_ssl, timestamp, title, islog=False)
        
        #pp.pprint(obj)
    sendemail.sendEmail(recipients, {'email': config(
    'SENDER_EMAIL'), 'password': config('SENDER_PASSWORD')}, obj, title)
