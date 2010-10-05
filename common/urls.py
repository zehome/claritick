# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('common.views',
    url(r'^client/$', 'infos_login', name="infos_login"),
    url(r'^client/modify/(?P<client_id>\d+)/$', 'modify_client', name="modify_client"),
    url(r'^trafiquable/$', 'trafiquable'),
    url(r'^exportable/$', 'exportable'),
)
