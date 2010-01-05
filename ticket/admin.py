# -*- coding: utf-8 -*-

from django.contrib import admin
from claritick.ticket.models import Ticket, Priority, State, Category, Project

admin.site.register(Ticket)
admin.site.register(State)
admin.site.register(Priority)
admin.site.register(Category)
admin.site.register(Project)