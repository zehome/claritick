# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('clariadmin.views',
    url(r'^$', 'list_all', name='list_hosts'),
    url(r'^new/$', 'new', name='new_host'),
    url(r'^new/from/(-?\d+)$', 'new'),
    url(r'^modify/(-?\d+)$', 'modify', name='modify_host'),
    url(r'^list/(all)?$', 'list_all', name='list_hosts'),
    # LC:TODO WTF ??? Learn regexp.
    url(r'^getExtrafieldsForm/(?P<host_type_id>-?\d+)/p(?P<prefix>\d+)(?P<blank>/b)?', 'ajax_extra_fields_form'),
    url(r'^getExtrafieldsForm/(?P<host_type_id>-?\d+)(?P<blank>/b)?', 'ajax_extra_fields_form'),
)
