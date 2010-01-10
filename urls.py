# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.contrib import admin

import settings
import django.contrib.auth.views
from django.template import RequestContext

# Custom models
import claritick.ticket.urls
import claritick.clariadmin.urls
# Init code
admin.autodiscover()


# Utilities
def flatpage(template, data={}):
    def render(request):
        return render_to_response(template, data, context_instance=RequestContext(request))
    return render

def agenda(request, data={}):
    template="agenda.html"
    user = request.user
    if user:
        try:
            profile = user.get_profile()
            data["google_account"] = profile.google_account
        except:
            pass
    
    return render_to_response(template, data, context_instance=RequestContext(request))

urlpatterns = patterns('',
    (r'^/*$', flatpage("index.html")),
    ## Medias (STATIC Content)
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^ticket/', include(claritick.ticket.urls)),
    (r'^clariadmin/', include(claritick.clariadmin.urls)),
    (r'^agenda/$', agenda),
    (r'^dojango/', include('dojango.urls')), # Dojango requires
)
