# -*- coding: utf-8 -*-

from django.contrib import admin
from clariadmin.models import OperatingSystem, HostType, Supplier, Host, ParamAdditionnalField, AdditionnalField

class HostAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Client", {'fields': ('site', 'location')}),
        ("Hote", {'fields': ('hostname', 'ip', 'serial', 'rootpw', 'type', 'os',
            'supplier', 'model')}),
        ("Plus", {'fields': ('commentaire', 'date_end_prod',
            'inventory', 'status')}),
    )

    search_fields = ['hostname', 'ip', 'inventory']
    list_filter = ['type', 'os', 'site']

admin.site.register(OperatingSystem)
admin.site.register(HostType)
admin.site.register(Supplier)
admin.site.register(Host, HostAdmin)
#admin.site.register(ParamAdditionnalField)
#admin.site.register(AdditionnalField)
