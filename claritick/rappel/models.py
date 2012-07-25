# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from ticket.models import Ticket

class Rappel(models.Model):
    class Meta:
        verbose_name = u"rappel"
        ordering = ['date',]
        unique_together = ('user', 'ticket')
        permissions = (
            ('can_use_rappel', u'Peut utiliser les rappels'),
        )

    date = models.DateTimeField()
    date_email = models.DateTimeField(verbose_name=u"date_email", null=True, blank=True)
    ticket = models.ForeignKey(Ticket,verbose_name=u"Ticket", blank=False, null=False)
    user = models.ForeignKey(User,verbose_name=u"User", null=False, blank=False)
    def __unicode__(self):
        return u"%s" % (self.date,)
