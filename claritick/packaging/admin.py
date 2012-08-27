# -*- coding: utf-8 -*-

from django.contrib import admin
from packaging.models import ClientPackageAuth, Platform
from packaging.models import PackageKind, PackageTemplate, Package


class PackageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Platform)
admin.site.register(PackageKind)
admin.site.register(PackageTemplate)
admin.site.register(Package, PackageAdmin)
admin.site.register(ClientPackageAuth)
