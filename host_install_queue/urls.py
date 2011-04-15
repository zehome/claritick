#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
urlpatterns = patterns('host_install_queue.views',
    url(r'^$','modify'),)

# vim:set et sts=4 ts=4 tw=80:
