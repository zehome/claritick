# -*- coding: utf8 -*-

from datetime import datetime, timedelta
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from lock.models import Lock
from lock.settings import *

@login_required
def ajax_lock(request, object_pk):
    model = request.GET.get("model", None)
    last_timestamp_field = request.GET.get("last_timestamp_field", None)
    timestamp = float(request.GET.get("timestamp", 0))
    user = request.user

    app_label, name = model.split('.', 1)

    try:
        lock = Lock.objects.get(content_type__name=name, \
                content_type__app_label=app_label, \
                object_pk=object_pk)
    except Lock.DoesNotExist:
        lock = None

    ret = {}
    content_type = ContentType.objects.get(app_label=app_label, name=name)

    obj = content_type.get_object_for_this_type(pk=object_pk)
    # Claritick specifics
    if obj.client and (not obj.client in request.user.clients):
        raise PermissionDenied

    if lock:

        if lock.user == user:
            lock.save()
            ret = LOCK_STATUS_UPDATED
        elif lock.is_expired:
            lock.user = user # get lock
            ret = LOCK_STATUS_EXPIRED
        else:
            ret = LOCK_STATUS_LOCKED
    else:
        lock = Lock(content_object=obj, user=user, last_modif_field=last_timestamp_field)
        ret = LOCK_STATUS_EXPIRED

    if ret == LOCK_STATUS_EXPIRED: # check for update
        if last_timestamp_field and timestamp:
            last_timestamp = getattr(obj, last_timestamp_field)
            from_date = datetime.fromtimestamp(timestamp)
            if last_timestamp - from_date < timedelta(seconds=LOCK_DELTA_MODIFICATION):
                ret = LOCK_STATUS_CREATED # get lock now
        lock.save()

    data = '{"status": %s' % (unicode(ret),)
    if ret == LOCK_STATUS_LOCKED:
        data += ', "locker": "%s"' % (unicode(lock.user),)
    data += '}'

    return HttpResponse(data, content_type="application/json; charset=utf-8")

