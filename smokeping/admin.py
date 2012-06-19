# -*- coding: utf-8 -*-

from django.contrib import admin
from common.models import Client
from smokeping.models import Smokeping

admin.site.register(Smokeping)
