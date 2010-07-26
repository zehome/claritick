# -*- coding: utf8 -*-

from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class LockManager(models.Manager):
    def get_query_set(self, *a, **kw):
        return super(LockManager, self).get_query_set(*a, **kw).\
                select_related('user')


class Lock(models.Model):

    objects = LockManager()

    user = models.ForeignKey(User, related_name="locked_by")
    updated = models.DateTimeField()
    last_modif_field = models.CharField(blank=True, null=True, max_length=100)
    content_type = models.ForeignKey(ContentType)
    object_pk = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_pk')

    def save(self, *a, **kw):
        self.updated = datetime.now()
        return super(Lock, self).save(*a, **kw)

    def __unicode__(self):
        ret = self.user.username
        if self.user.email:
            ret += u" <%s>" % (self.user.email)
        return ret

