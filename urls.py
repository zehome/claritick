# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.contrib import admin
from ticket.context_processors import get_ticket_text_statistics, get_critical_tickets, get_ticket_alarm
from claritick.ticket.models import TicketAlarm

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
import claritick.chuser.urls

# Init code
admin.autodiscover()
reporting.autodiscover()

# Utilities
def indexpage(template, data={}):
    def render(request):
        if request.user and not request.user.is_anonymous():
            data.update(
                    ticket_dashboard_critical = get_critical_tickets(request),
                    ticket_dashboard_text_statistics = get_ticket_text_statistics(request),
                    ticket_alarms = get_ticket_alarm(request),
                    )
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
    (r'^/*$', indexpage("index.html")),
    ## Medias (STATIC Content)
    #(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^ticket/', include(claritick.ticket.urls)),
    (r'^common/', include(claritick.common.urls)),
    (r'^chuser/', include(claritick.chuser.urls)),
    (r'^clariadmin/', include(claritick.clariadmin.urls)),
    (r'^developpements/', include(claritick.developpements.urls)),
    (r'^agenda/$', agenda),
    (r'^dojango/', include('dojango.urls')), # Dojango requires
    
    ## Auth
    (r'^accounts/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('django.contrib.auth.urls')),
    
    ## Reporting
    (r'^reporting/', include('reporting.urls')),
    
    ## Error testing
    (r'^error/', raise_trial_exception),
    
    ## Web services
    (r'^ws/', include(claritick.ws.urls)),
)
