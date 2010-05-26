#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import urllib
import sys
from base64 import encodestring
from optparse import OptionParser

ASSIGNED_TO = 9
CATEGORY = 16
STATE = 1
PRIORITY = 2
SVN_USERS_TO_CLARITICK = {
    'gl'   : 6,
    'sheb' : 13,
    }

SVN_REPOSITORY_TO_CLARITICK_PROJECT = {
    '/svn/MCA3' : 4,
    '/svn/MCA2' : 4,
    '/svn/clarilab' : 2,
    }

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
    
    _client = DjangoWSClient("192.168.1.154", 9080, "ws", username = "admin", password = "admin")
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
        else:
            # create it
            s,h,d = self._client.request_post(self._resource, urllib.urlencode(self.dict).encode('utf-8'))
        if s != 200:
            raise DjangoWSException("%s %s %s" % (s,h,d,))
        return d

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-t', '--title', dest='title', help='Ticket title')
    parser.add_option('-u', '--user', dest='svn_user', help='Subversion user')
    parser.add_option('-r', '--repository', dest='svn_repo', help='Subversion repository')
    #~ dwc = DjangoWSClient("192.168.1.9",8888,"ws", username = "admin", password = "admin")
    #~ print dwc.request_get("test/562")
    #~ s, h, d = dwc.request_post("test/",urllib.urlencode({'truc':'piou2'}))
    #~ print s
    #~ print h
    #~ print d
    (options, args) = parser.parse_args()
    svn_user = options.svn_user
    svn_repo = options.svn_repo
    title    = options.title
    if not title:
        title = 'Documentation à faire'
    if not svn_user in SVN_USERS_TO_CLARITICK:
        raise DjangoWSException("This user is not mapped to a claritick user : %s" % (svn_user,))
    if not svn_repo in SVN_REPOSITORY_TO_CLARITICK_PROJECT:
        raise DjangoWSException("This repository is not mapped to a claritick project : %s" % (svn_repo,))
    
    texte = sys.stdin.read()
    if not texte:
        texte = 'Texte'
    pr = PyRest(3613)
    print pr.retrieve()
    dict = {
        'contact' : svn_user,
        'assigned_to' : ASSIGNED_TO,
        'opened_by' : SVN_USERS_TO_CLARITICK[svn_user],
        'title' : title.decode().encode('LATIN9'),
        'text' : texte,
        'category' : CATEGORY,
        'state': STATE,
        'priority' : PRIORITY,
        'project' : SVN_REPOSITORY_TO_CLARITICK_PROJECT[svn_repo],
        'validated_by' : SVN_USERS_TO_CLARITICK[svn_user],
        }
    pr = PyRest(**dict)
    result = pr.save()
    
    print result