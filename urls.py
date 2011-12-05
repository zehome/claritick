# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url, include
from django.shortcuts import render_to_response
from django.contrib import admin
from ticket.views import get_critical_tickets, get_ticket_alarm
from django.http import HttpResponse

import reporting

from django.template import RequestContext

# Custom models
import ticket.urls
import common.urls
import clariadmin.urls
import developpements.urls
import ws.urls
import chuser.urls
import lock.urls
import packaging.urls
import host_history.urls
import desktopnotifications.urls
import bondecommande.urls
import etiquette_printer.urls
import qbuilder.urls

# Init code
admin.autodiscover()
reporting.autodiscover()

# Utilities
def indexpage(template, data={}):
    def render(request):
        if request.user and not request.user.is_anonymous():
            data.update(
                    ticket_dashboard_critical = get_critical_tickets(request),
                    #ticket_dashboard_text_statistics = get_ticket_text_statistics(request),
                    ticket_alarms = get_ticket_alarm(request),
                    )
        return render_to_response(template, data, context_instance=RequestContext(request))
    return render

def iepage(template, data = {}):
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

def ovh_cert(request, data={}):
    return HttpResponse("knqvrjirhctwex")

def raise_trial_exception(*kw, **args):
    raise Exception("Trial exception")

urlpatterns = patterns('',
    (r'^/*$', indexpage("index.html")),
    url(r'^ie/*$', iepage("ie.html"), name="internet_explorer"),
    ## Medias (STATIC Content)
    #(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^ticket/', include(ticket.urls)),
    (r'^common/', include(common.urls)),
    (r'^chuser/', include(chuser.urls)),
    (r'^lock/', include(lock.urls)),
    (r'^clariadmin/', include(clariadmin.urls)),
    (r'^host-history/', include(host_history.urls)),
    (r'^developpements/', include(developpements.urls)),
    (r'^agenda/$', agenda),
    (r'^dojango/', include('dojango.urls')), # Dojango requires
    
    ## Packaging
    (r'^packaging/', include(packaging.urls)),
    
    ## Auth
    (r'^accounts/$', 'django.contrib.auth.views.login'),
    (r'^accounts/', include('django.contrib.auth.urls')),
    
    ## Reporting
    (r'^reporting/', include('reporting.urls')),
    
    ## Error testing
    (r'^error/', raise_trial_exception),
    
    ## Web services
    (r'^ws/', include(ws.urls)),

    ## Ovh cert
    (r'^ovh-cert.txt', ovh_cert),

    ## Desktop notifications
    url(r'^notifications/', include(desktopnotifications.urls)),
    
    ## Bon de commandes
    url(r'^bondecommande/', include(bondecommande.urls)),

    ## Impression d'étiquettes
    url(r'^etiquette/', include(etiquette_printer.urls)),

    ## Stats Qbuilder
    url(r'^qbuilder/', include(qbuilder.urls)),
)
