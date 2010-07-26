# -*- coding: utf8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('lock.views',
        url(r'^ajax_lock/(?P<object_pk>\d+)/$', "ajax_lock", name="lock_ajax_lock"),
)
