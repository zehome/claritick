# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('packaging.views',
    url(r'^list/?$', 'list', name="packaging_list"),
    url(r'^list/json/?$', 'listjson', name="packaging_listjson"),
    url(r'^download/(\d+)$', 'download', name="packaging_download"),
    url(r'^getconfig/?$', 'getconfig', name="packaging_getconfig"),
    url(r'^autoupdate/?$', 'autoupdate', name="packaging_autoupdate"),
)
