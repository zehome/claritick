# -*- coding: utf-8 -*-

from django.contrib import admin
from packaging.models import Platform, PackageKind, PackageList, Package

class PackageInline(admin.StackedInline):
    model = Package

class PackageListAdmin(admin.ModelAdmin):
    inlines = [
        PackageInline,
    ]

admin.site.register(Platform)
admin.site.register(PackageKind)
admin.site.register(PackageList, PackageListAdmin)
admin.site.register(Package)
