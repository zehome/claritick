# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from common.models import Client, UserProfile, GoogleAccount, Coordinate, ClaritickUser
from common.forms import ClaritickUserCreationForm

class CoordinateAdmin(admin.ModelAdmin):
    fields = ( "destinataire", "address_line1", "address_line2", "address_line3",
        "postalcode", "city",
        "telephone", "fax", "gsm",
        "email", "more")

class ClientAdmin(admin.ModelAdmin):
    search_fields = ["label", "parent__label"]

class UserProfileInline(admin.TabularInline):
    model = UserProfile

class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]
    list_display = ["username", "email", "first_name", "last_name", "is_staff", "get_client"]

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',)}
        ),
    )
    add_form = ClaritickUserCreationForm

admin.site.register(Client, ClientAdmin)
admin.site.register(ClaritickUser, UserAdmin)
admin.site.register(GoogleAccount)
admin.site.register(Coordinate, CoordinateAdmin)
