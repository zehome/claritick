# -*- coding: utf8 -*-

import lock.settings

def lock_settings(request):
    ret = {"lock_settings": {}}
    for key in ("LOCK_EXPIRE", "LOCK_UPDATE",
            "LOCK_STATUS_UPDATED", "LOCK_STATUS_LOCKED",
            "LOCK_STATUS_EXPIRED", "LOCK_STATUS_CREATED"):
        ret["lock_settings"][key] = getattr(lock.settings, key)
    return ret

