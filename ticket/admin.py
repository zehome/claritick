# -*- coding: utf-8 -*-

from django.contrib import admin
from dojango import forms as df
from ticket.models import Ticket, Priority, State, Category, Project, Procedure, TicketView, TicketMailTrace
from common.models import Client

class ProjectAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """ Override save_model in order to pass the "client" to wich tickets
        will automatically be affected. """
        
        data = request.POST
        client = data.get("client", None)
        obj.save(client_id=client)
    
    def get_form(self, request, obj=None, **kwargs):
        """ Override get_form to add "client" to project """
        form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["client"] = df.ModelChoiceField(queryset = Client.objects.all(),
                        widget=df.FilteringSelect(attrs={'queryExpr': '${0}*'}), empty_label='', required=False)
        return form

class ProcedureAdmin(admin.ModelAdmin):
    filter_horizontal = ('tickets',)

class TicketViewAdmin(admin.ModelAdmin):
    list_display = ("user", "name")

class TicketMailTraceAdmin(admin.ModelAdmin):
    list_display = ("ticket", "date_sent")
    search_fields = ["ticket__title", "ticket__id", "email"]

#admin.site.register(Ticket)
admin.site.register(State)
admin.site.register(Priority)
admin.site.register(Category)
admin.site.register(TicketView, TicketViewAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(TicketMailTrace, TicketMailTraceAdmin)
