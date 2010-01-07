# -*- coding: utf-8 -*-

from django.contrib import admin
from common.models import Groupement, Site, UserProfile, GoogleAccount

admin.site.register(Groupement)
admin.site.register(Site)
admin.site.register(UserProfile)
admin.site.register(GoogleAccount)