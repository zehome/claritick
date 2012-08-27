#-*- coding: utf-8 -*-

from django.contrib import admin
from rappel.models import Rappel


class ListRappel(admin.ModelAdmin):
    list_display = ('ticket', 'date_email', 'date')

admin.site.register(Rappel, ListRappel)
