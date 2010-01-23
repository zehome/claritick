# -*- coding: utf-8 -*-

from django.contrib import admin
from claritick.ticket.models import Ticket, Priority, State, Category, Project, Procedure

#class ProjectAdmin(admin.ModelAdmin):
#    fieldsets = [
#        (None, )
#    ]

class ProcedureAdmin(admin.ModelAdmin):
    filter_horizontal = ('tickets',)

admin.site.register(Ticket)
admin.site.register(State)
admin.site.register(Priority)
admin.site.register(Category)
admin.site.register(Project)
admin.site.register(Procedure, ProcedureAdmin)
