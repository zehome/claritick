# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('common.views',
    url(r'^client/$', 'modify_client', name="common_client_modify"),
    (r'^trafiquable/$', 'trafiquable'),
    (r'^exportable/$', 'exportable'),
)
