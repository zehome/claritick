# -*- coding: utf-8 -*-

from django.contrib import admin
from packaging.models import ClientPackageAuth, Platform
from packaging.models import Package, PackageConfig

admin.site.register(ClientPackageAuth)
admin.site.register(Platform)
admin.site.register(Package)
admin.site.register(PackageConfig)
