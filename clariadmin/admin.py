# -*- coding: utf-8 -*-

from django.contrib import admin
from clariadmin.models import OperatingSystem, HostType, Supplier, Host, ParamAdditionnalField, AdditionnalField

admin.site.register(OperatingSystem)
admin.site.register(HostType)
admin.site.register(Supplier)
