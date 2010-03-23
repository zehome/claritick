# -*- coding: utf-8 -*-

from django.contrib import admin
from common.models import Client, UserProfile, GoogleAccount, Coordinate

class CoordinateAdmin(admin.ModelAdmin):
    fields = ( "destinataire", "address_line1", "address_line2", "address_line3",
        "postalcode", "city",
        "telephone", "fax", "gsm",
        "email", "more")

class ClientAdmin(admin.ModelAdmin):
    search_fields = ["label", "parent__label"]

admin.site.register(Client, ClientAdmin)
admin.site.register(UserProfile)
admin.site.register(GoogleAccount)
admin.site.register(Coordinate, CoordinateAdmin)
