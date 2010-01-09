# -*- coding: utf-8 -*-

from django.contrib import admin
from common.models import Client, UserProfile, GoogleAccount

admin.site.register(Client)
admin.site.register(UserProfile)
admin.site.register(GoogleAccount)
