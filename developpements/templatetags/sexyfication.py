# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
#~ from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

import os

register = template.Library()

MEDIA_URL = getattr(settings, "MEDIA_URL", "/site_media/")

@register.filter
def boolicon(value):
    "Converti un booleen en icone"
    if value is None:
        icone = str(value)
    else:
        icone = str(bool(value))
    return mark_safe("""<img src="%sicones/bool-%s.png"/>""" % (MEDIA_URL, icone,))
