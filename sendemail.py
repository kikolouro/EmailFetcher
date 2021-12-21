import smtplib
import ssl


def dataHandler(data):
    total = 0
    text = ''
    for log in data:
        if data[log]['count'] != 0:
            total += data[log]['count'] 
            text += f"Error Count on {log} log: {data[log]['count']}\n{data[log]['errors']}"

    return total, text

def sendEmail(receivers, senderdata, data, port=465, smtpserver='smtp.gmail.com'):
    sender_email = senderdata['email']
    password = senderdata['password']
    total, text = dataHandler(data)
    message = f"""\
    Subject: {total} Errors on log File in 4 hours

    There was {total} errors on log files in the last 4 hours. Here is a summary of them: \n{text}""".encode('utf-8')
    if total != 0:
        SUBJECT = f"{total} Errors on log File in 4 hours"
        TEXT = f"There was {total} errors on log files in the last 4 hours. Here is a summary of them: \n{text}"
    else:
        SUBJECT = f"There was no erros on log files"
        TEXT = f"There was no errors on log files in the last 4 hours."

    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtpserver, port, context=context) as server:
        server.login(sender_email, password)
        for receiver in receivers:
            server.sendmail(sender_email, receiver,
                            message.encode('utf-8'))
    return "Success"
