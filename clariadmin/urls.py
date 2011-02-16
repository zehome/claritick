# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('clariadmin.views',
    url(r'^new/$',                 'new'),
    url(r'^new/from/(-?\d+)$', 'new'),
    url(r'^modify/(-?\d+)$',          'modify'),
    url(r'^list/(all)*$',          'list_all'),
    url(r'^new_extra_field/$',     'new_extra_field'),
    url(r'^mod_extra_field/(\d+)', 'mod_extra_field'),
    url(r'^getExtrafieldsForm/(-?\d+)', 'ajax_extra_fields_form'),
)
