# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('packaging.views',
    url(r'^/*$', 'list', name="packaging_list"),
    url(r'^list/$', 'list', name="packaging_list"),
    url(r'^list/xml/$', 'listxml', name="packaging_list_xml"),
    url(r'^list/json/$', 'listjson', name="packaging_list_json"),
    url(r'^get/(\d+)$', 'get_id', name="packaging_get_id"),
    url(r'^get/(\d+)/(\w+)$', 'get_id'),
)
