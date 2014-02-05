# -*- coding: utf-8 -*-

from django.db import models
from common.models import Client


class Smokeping(models.Model):
    class Meta:
        permissions = (("smokeping", u"Acces SmokePing"),)

    client = models.ForeignKey(Client,
                               verbose_name=u"client",
                               blank=False, null=False,
                               related_name='smokeping',
                               unique=True)
    path = models.CharField(u"chemin d'access smokeping",
                            max_length=256,
                            blank=False, null=False)

    def __unicode__(self):
        return u"Smokeping for %s on %s" % (self.client, self.path)
