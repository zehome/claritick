# -*- coding: utf8 -*-

from django.contrib.contenttypes.models import ContentType
from lock.models import Lock

def locked_content(func):
    """ Model.save() decorator, when save an object remove the lock """
    obj = None
    def decorator(self, *a, **kw):
        ret = func(self, *a, **kw)
        if self.pk:
            Lock.objects.\
                    filter(content_type=ContentType.objects.get_for_model(self)).\
                    filter(object_pk=self.pk).delete()
        return ret
    return decorator
