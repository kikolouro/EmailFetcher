from datetime import time
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import os
import sys
import json
from decouple import config
import pprint

pp = pprint.PrettyPrinter(indent=4)


def render_template(template, **kwargs):
    ''' renders a Jinja template into HTML '''
    # check if template exists
    # print(os.path.exists(template))
    if not os.path.exists(template):
        print('No template file present: %s' % template)
        sys.exit()

    import jinja2
    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template(template)
    #print(templ.render(**kwargs))
    return templ.render(**kwargs)


def dataHandler(data, title):
    total = 0
    final = {'title': title, 'logs': []}
    if 'log' in title:

        for log in data:
            if data[log]['count'] != 0:
                total += data[log]['count']
                errors = []
                for error in data[log]['errors']:
                    temp = error.split(' ', 5)
                    print(temp)
                    timestamp = f"{temp[0]} {temp[1]}"
                    module = temp[4]
                    message = temp[5][2:]
                    errors.append({
                        'timestamp': timestamp,
                        'module': module,
                        'message': message
                    })
                final['logs'].append({
                    'log': log,
                    'errors': errors
                })
    else:
        if data['count'] != 0:
            total += data['count']
            errors = []
            for error in data['errors']:
                errors.append({
                    "host": error['host'],
                    "name": error['name'],
                    "data": error['data'],
                    "id": error['id'],
                    "severity": error['severity']
                })
            final['logs'].append({
                'errors': errors
            })
    return total, final


def sendEmail(receivers, senderdata, data, title, port=465, smtpserver='smtp.gmail.com'):
    sender_email = senderdata['email']
    password = senderdata['password']
    total, bodydata = dataHandler(data, title)
    if total != 0:
        if 'log' in title:
            SUBJECT = f"{total} Errors on log File in 4 hours"
        else:
            SUBJECT = f"{total} Problems in 4 hours"
    else:
        SUBJECT = f"There was no errors on log files"

    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['Subject'] = SUBJECT
    html = render_template(f'{os.getcwd()}/template.j2', data=bodydata)
    msg.attach(MIMEText(html, 'html'))
    context = ssl.create_default_context()
    if total == 0:
        if int(config('NOERRORMAIL')) == 0:
            return
    with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
        server.login(sender_email, password)
        for receiver in receivers:
            msg['To'] = ''.join(receiver)

            server.sendmail(sender_email, receiver,
                            msg.as_string())

    return "Success"
