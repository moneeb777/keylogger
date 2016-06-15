######################################
##
## Initially written as a part of the pyGeolocation project but has more functionality here.
##
######################################

import subprocess

def getWifi():
    results = subprocess.check_output(["netsh", "wlan", "show", "all"]) # netsh command. Try it on CMD to examine the output

    results = results.replace("\r", "")
    ls = results.split("\n")  # Splitting the result of our netsh command into a list containing each line

    compile = {}
    compile['ssids'] = []

    x = 0  # For traversing ls
    y = 0  # For traversing compile json
    while x < len(ls):

        if ls[x].split(" ")[0] == 'SSID':  # When we reach a line which lists properties about a certain SSID
            compile['ssids'].append({})

            ssid = ls[x].split(': ')[1]  # Wifi name
            compile['ssids'][y]['name'] = ssid

            networkType = ls[x+1].split(': ')[1]  # Network type
            compile['ssids'][y]['networkType'] = networkType

            authentication = ls[x+2].split(': ')[1]  # WPA type
            compile['ssids'][y]['authentication'] = authentication

            encryption = ls[x+3].split(': ')[1]  # Encryption type
            compile['ssids'][y]['encryption'] = encryption

            bssid = ls[x+4].split()[3]  # MAC Address
            compile['ssids'][y]['bssid'] = bssid

            signal = ls[x+5].split()[2].split('%')[0]  # Signal strength in percentage
            rssi = (int(signal)/2) - 100  # RSSI value
            compile['ssids'][y]['rssi'] = rssi

            radioType = ls[x+6].split(': ')[1]  # Radio type
            compile['ssids'][y]['radioType'] = radioType

            channel = ls[x+7].split(': ')[1]  # WiFi channel
            compile['ssids'][y]['channel'] = channel

            basicRates = ls[x+8].split(': ')[1]
            compile['ssids'][y]['basicRates'] = basicRates

            otherRates = ls[x+9].split(': ')[1]
            compile['ssids'][y]['otherRates'] = otherRates

            y += 1
        x += 1
    return compile
