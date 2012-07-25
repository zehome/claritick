# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('bondecommande.views',
       url(r'^getfile/(\d+)/?$', 'getfile', name='bdc_getfile'),
   )
