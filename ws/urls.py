# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from django_restapi.model_resource import Collection
from django_restapi.responder import XMLResponder
from django_restapi.authentication import HttpBasicAuthentication

from ticket.models import Ticket

ticket_resource = Collection(
    queryset = Ticket.objects.all(),
    responder = XMLResponder(),
    permitted_methods = ('GET', 'PUT', 'POST', ),
    authentication = HttpBasicAuthentication()
)

urlpatterns = patterns('',
    url(r'^ticket/(.*?)/?$', ticket_resource)
)
