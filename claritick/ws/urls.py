# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from django_restapi.model_resource import Collection
from django_restapi.responder import XMLResponder
from django_restapi.authentication import HttpBasicAuthentication
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings

svndoc_config = getattr(settings, "SVNDOC_CONFIG", {})

from ticket.models import Ticket, State, Priority, Category, Project, Client
from django.contrib.auth.models import User

class TicketCollection(Collection):
    
    def create(self, request):
        data = self.receiver.get_post_data(request)
        try:
            assigned_to = User.objects.get(pk = svndoc_config.get("ASSIGNED_TO", None))
        except User.DoesNotExist:
            assigned_to = None
        try:
            opened_by = User.objects.get(pk = svndoc_config.get("OPENED_BY", None))
        except User.DoesNotExist:
            return HttpResponseServerError("No user is configured as the default ticket opener")
        try:
            validated_by = User.objects.get(pk = svndoc_config.get("VALIDATOR",None))
        except User.DoesNotExist:
            validated_by = None
        try:
            category = Category.objects.get(pk = svndoc_config.get("CATEGORY", None))
        except Category.DoesNotExist:
            return HttpResponseServerError("No category is configured as the default for new tickets")
        try:
            state = State.objects.get(pk = svndoc_config.get("STATE", None))
        except State.DoesNotExist:
            state = None
        try:
            priority = Priority.objects.get(pk = svndoc_config.get("PRIORITY", None))
        except Priority.DoesNotExist:
            priority = None
        try:
            project = Project.objects.get(pk = svndoc_config.get("SVN_REPOSITORY_TO_CLARITICK_PROJECT",{}).get(data.get('svn_repo',None),None))
        except Project.DoesNotExist:
            project = None
        try:
            client = Client.objects.get(pk = svndoc_config.get("CLIENT", 1))
        except Client.DoesNotExist:
            return HttpResponseServerError("The default client for new tickets does not exist nor does the client #1")
        new_ticket_data = {
            'contact' : data.get("svn_user",''),
            'assigned_to' : assigned_to,
            'opened_by' : opened_by,
            'title' : data.get("title",u"Une documentation est nécessaire"),
            'text' : data.get("text",u"Aucune information disponible"),
            'category' : category,
            'state': state,
            'priority' : priority,
            'project' : project,
            'validated_by' : validated_by,
            'client' : client,
            }
        new_ticket = Ticket(**new_ticket_data)
        new_ticket.save()
        return HttpResponse("%s" % (new_ticket,))

ticket_resource = TicketCollection(
    queryset = Ticket.objects.all(),
    responder = XMLResponder(),
    permitted_methods = ('GET', 'PUT', 'POST', ),
    authentication = HttpBasicAuthentication()
)

urlpatterns = patterns('',
    url(r'^ticket/(.*?)/?$', ticket_resource)
)
