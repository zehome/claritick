# -*- coding: utf-8 -*-

from django.contrib import admin
from claritick.clariadmin.models import OperatingSystem, HostType, Supplier, Host

admin.site.register(OperatingSystem)
admin.site.register(HostType)
admin.site.register(Supplier)
admin.site.register(Host)
