#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import urllib
import sys
from base64 import encodestring
from optparse import OptionParser

HOST="192.168.1.154"
PORT=9080
BASE_URL="ws"
USERNAME="admin"
PASS="admin"

class DjangoWSException(Exception):
    pass

class DjangoWSClient(object):
    
    def __init__(self, host, port, base_url, username=None, password=None):
        self.base_url = base_url
        
        self.host, self.port = host, port
        self.auth = 'Basic ' + (encodestring(username + ':' + password)).strip()
    
    def request_get(self, resource, args=None, headers={}):
        return self.request(resource, method = 'get', args=args, headers=headers)
        
    def request_put(self, resource, args=None, headers={}):
        return self.request(resource, method = 'put', args=args, headers=headers)
        
    def request_post(self, resource, args=None, headers={}):
        return self.request(resource, method = 'post', args=args, headers=headers)
        
    def request(self, resource, method="get", args=None, body=None, headers={}):
        h = httplib.HTTPConnection(self.host, self.port)
        headers.update({
            "Authorization":self.auth,
            "X-Requested-With":"XMLHttpRequest",
            })
        if method.upper() == 'GET':
            uri_extra = ""
            if args:
                uri_extra = "?" + urllib.urlencode(args)
            h.request(method.upper(), u'/%s/%s%s' % (self.base_url, resource, uri_extra, ), None, headers)
        else:
            h.request(method.upper(), u'/%s/%s' % (self.base_url, resource, ), args, headers)
        resp = h.getresponse()
        r_status  = resp.status
        r_headers = resp.getheaders()
        r_data    = resp.read()

        return r_status, r_headers, r_data

class PyRest(object):
    
    _client = DjangoWSClient(HOST, PORT, BASE_URL, username = USERNAME, password = PASS)
    _resource = 'ticket/'
    
    def __init__(self, pk=None, **kwargs):
        self.pk = pk
        self.dict = kwargs
    
    def retrieve(self):
        if not self.pk:
            return None
        s,h,d = self._client.request_get('%s%s' % (self._resource, self.pk,))
        if s != 200:
            raise DjangoWSException("%s %s %s" % (s,h,d,))
        return d
    
    def save(self):
        if self.pk:
            # update it
            s,h,d = self._client.request_put('%s%s' % (self._resource, self.pk,), urllib.urlencode(self.dict).encode('utf-8'))
            if s != 200:
                raise DjangoWSException("%s %s %s" % (s,h,d,))
        else:
            # create it
            s,h,d = self._client.request_post(self._resource, urllib.urlencode(self.dict).encode('utf-8'))
            if s not in (201, 200):
                raise DjangoWSException("%s %s %s" % (s,h,d,))
        return d

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-t', '--title', dest='title', help='Ticket title')
    parser.add_option('-u', '--user', dest='svn_user', help='Subversion user')
    parser.add_option('-r', '--repository', dest='svn_repo', help='Subversion repository')
    (options, args) = parser.parse_args()
    svn_user = options.svn_user
    svn_repo = options.svn_repo
    title    = options.title
    if not title:
        title = 'Documentation à faire'
    
    texte = sys.stdin.read()
    if not texte:
        texte = 'Texte'
    dict = {
        'contact' : svn_user,
        'title' : title,
        'text' : texte,
        'svn_repo' : svn_repo,
        }
    pr = PyRest(**dict)
    result = pr.save()
    
    print result
