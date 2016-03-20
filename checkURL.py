##################################################################
#
# Takes in two arguments; URL and timeout. Upon calling checkURL(url, timeout)
# function, it tries to connect to the supplied url. If a connection is made it
# returns 'Internet connected' or 'No internet connection' if a connection is not made
#
#################################################################


import urllib2


def checkURL(url='http://www.google.com', timeout=1):
    try:
        response = urllib2.urlopen(url, timeout=timeout)
    except Exception, e:
        print 'connection to ' + str(url) +' failed'
        print str(e)
        return False
    response.close()
    return True
