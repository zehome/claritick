# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.contrib import admin

import settings
import django.contrib.auth.views
from django.template import RequestContext

# Custom models
import claritick.ticket.urls
# Init code
admin.autodiscover()


# Utilities
def flatpage(template, data = {}):
    def render(request):
        return render_to_response(template, data, context_instance=RequestContext(request))
    return render

urlpatterns = patterns('',
    (r'^/*$', flatpage("index.html")),
    ## Medias (STATIC Content)
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^commentaires/', include('django.contrib.comments.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^ticket/', include(claritick.ticket.urls)),
)
