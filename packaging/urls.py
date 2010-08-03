# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('packaging.views',
    url(r'^/*$', 'list', name="packaging_list"),
    url(r'^list/$', 'list', name="packaging_list"),
)
