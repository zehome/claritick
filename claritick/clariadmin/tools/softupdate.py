#!/usr/bin/env python

# Uses softupdate API in claritick to update some
# sensible informations regarding to hosts:
# 
# serial / hostname / ip address

import subprocess
import traceback
import urllib2
import urllib
import socket
import sys
import re

IP_RE = re.compile(r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})")
DNSSERVER = "8.8.8.8"
SOFTUPDATE_URL="http://10.31.254.49:3000/clariadmin/softupdate/ip/"
SOFTUPDATE_TIMEOUT=15
SOFTUPDATE_KEY="engee4keiShequ1YiuRieyaejohcohjae9naefeisie2eenaeliequahshaShaed"

def dns_host_cmd(hostname):
    """If the dns_sytem is not working, we try using the "host" command."""
    try:
        output = subprocess.check_output(["host", hostname, DNSSERVER])
        ip=None
        for line in output.split("\n"):
            if "has address" in line:
                try:
                    ip = IP_RE.search(line).group(1)
                except:
                    continue
                if ip:
                    break
    except:
        traceback.print_exc()
        ip = None
    return ip

def dns_getip(hostname):
    """DNS resolv with fallback on host / DNSSERVER"""
    try:
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        return dns_host_cmd(hostname)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    localip = s.getsockname()[0]
    return localip

def get_hostname():
    return socket.gethostname()

def get_systemid():
    try:
        output = subprocess.check_output(["/usr/sbin/getSystemId", "--service-tag"])
        return output.split()[-1]
    except:
        print "Unable to get service tag."
    
    return None

if __name__ == "__main__":
    # Backward python compatible
    socket.setdefaulttimeout(SOFTUPDATE_TIMEOUT)
    
    datadict = {
        'serial': get_systemid(),
        'hostname': get_hostname(),
        'ip': get_local_ip(),
        'key': SOFTUPDATE_KEY,
    }
    
    url ="%s%s" % (SOFTUPDATE_URL, get_local_ip())
    request = urllib2.Request(url=url,
        data=urllib.urlencode(datadict))
    request.add_header('User-agent', 'SoftUpdate/1.0')
    
    try:
        resp = urllib2.urlopen(request)
    except Exception, e:
        print "Unable to perform softupdate."
        print e.read()
        sys.exit(1)
    
    sys.exit(0)