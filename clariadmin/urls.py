# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('claritick.clariadmin.views',
    url(r'^new/$',                 'new'),
    url(r'^modify/(\d*)',          'modify'),
    url(r'^list/(all)*$',          'list_all'),
)
