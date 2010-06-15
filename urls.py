# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.contrib import admin

import reporting

#import settings
import django.contrib.auth.views
from django.template import RequestContext

# Custom models
import claritick.ticket.urls
import claritick.common.urls
import claritick.clariadmin.urls
import claritick.developpements.urls
import claritick.ws.urls

# Init code
admin.autodiscover()
reporting.autodiscover()

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

def raise_trial_exception(*kw, **args):
    raise Exception("Trial exception")

urlpatterns = patterns('',
    (r'^/*$', flatpage("index.html")),
    ## Medias (STATIC Content)
    #(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^ticket/', include(claritick.ticket.urls)),
    (r'^common/', include(claritick.common.urls)),
    (r'^clariadmin/', include(claritick.clariadmin.urls)),
    (r'^developpements/', include(claritick.developpements.urls)),
    (r'^agenda/$', agenda),
    (r'^dojango/', include('dojango.urls')), # Dojango requires
    
    ## Auth
    (r'^accounts/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('django.contrib.auth.urls')),
    
    ## Reporting
    (r'^reporting/', include('reporting.urls')),
    
    ## Backlinks
#    (r'^backlinks/', include('backlinks.urls')),

    ## Error testing
    (r'^error/', raise_trial_exception),
    
    ## Web services
    (r'^ws/', include(claritick.ws.urls)),
)
