# -*- coding: utf-8 -*-

from django.contrib import admin
from clariadmin.models import OperatingSystem, HostType, Supplier

admin.site.register(OperatingSystem)
admin.site.register(HostType)
admin.site.register(Supplier)
