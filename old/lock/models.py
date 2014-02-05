# -*- coding: utf8 -*-

from lock.settings import *

from datetime import datetime, timedelta

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User


class ExpiredLockManager(models.Manager):
    def get_query_set(self, *a, **kw):
        return super(ExpiredLockManager, self) \
            .get_query_set(*a, **kw) \
            .filter(updated__lt=(datetime.now() - timedelta()))


class LockManager(models.Manager):
    def get_query_set(self, *a, **kw):
        return super(LockManager, self) \
            .get_query_set(*a, **kw) \
            .select_related('user')


class Lock(models.Model):

    objects = LockManager()
    expired = ExpiredLockManager()

    user = models.ForeignKey(User, related_name="locked_by")
    updated = models.DateTimeField()
    last_modif_field = models.CharField(blank=True, null=True, max_length=100)
    content_type = models.ForeignKey(ContentType)
    object_pk = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_pk')

    @property
    def is_expired(self):
        return bool(datetime.now() - self.updated > timedelta(seconds=LOCK_EXPIRE))

    def save(self, *a, **kw):
        self.updated = datetime.now()
        return super(Lock, self).save(*a, **kw)

    def __unicode__(self):
        ret = self.user.username
        if self.user.email:
            ret += u" <%s>" % (self.user.email)
        return ret
