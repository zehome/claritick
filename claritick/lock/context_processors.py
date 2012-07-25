# -*- coding: utf8 -*-

import lock.settings
from django.utils import simplejson as json

def lock_settings(request):
    ret = {}
    for key in ("LOCK_EXPIRE", "LOCK_UPDATE",
            "LOCK_STATUS_UPDATED", "LOCK_STATUS_LOCKED",
            "LOCK_STATUS_EXPIRED", "LOCK_STATUS_CREATED"):
        ret[key] = getattr(lock.settings, key)
    return {"lock_settings": json.dumps(ret)}

