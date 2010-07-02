# -*- coding: utf8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('chuser.views',
        url(r'^change_user/$', 'change_user', name='chuser_change_user'),
)
