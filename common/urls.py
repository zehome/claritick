# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('claritick.common.views',
    url(r'^client/$',         'modify_client', name="common_client_modify"),
)
