# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from customer.models import Customer
from positions import PositionField, PositionManager


class Priority(models.Model):
    class Meta:
        verbose_name = _("Priority")
        ordering = ['index', 'label']

    objects = PositionManager('index')

    label = models.CharField(_("Label"), max_length=64, blank=True)
    alarm = models.CharField(_("Automatic alarm"), max_length=128,
        null=True, blank=True)
    index = PositionField()

    def __unicode__(self):
        return self.label


class State(models.Model):
    class Meta:
        verbose_name = _("State")
        verbose_name_plural = _("State")
        ordering = ['index', 'label']

    objects = PositionManager('index')

    label = models.CharField(_("Label"), max_length=64)
    index = PositionField()

    def __unicode__(self):
        return self.label


class Ticket(models.Model):
    class Meta:
        verbose_name = _("Ticket")
        ordering = ['-last_modification']
        permissions = (
            ("add_ticket_full", _("Can create full tickets")),
            ("can_resolve", _("Can close tickets")),
            ("can_view_internal_comments", _("Can view internal comments")),
        )
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"),
        blank=True, null=True)
    contact = models.CharField(_("Contact"), max_length=128, blank=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    date_open = models.DateTimeField(_("Open date"), auto_now_add=True)
    last_modification = models.DateTimeField(_("Last modification"),
        auto_now_add=True, auto_now=True)
    date_close = models.DateTimeField(_("Close date"), blank=True, null=True)
    state = models.ForeignKey(State, verbose_name=_("State"),
        blank=True, null=True)
    priority = models.ForeignKey(Priority, verbose_name=_("Priority"),
        blank=True, null=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,
        verbose_name=_("Assigned to"),
        related_name="assigned_to",
        blank=True, null=True)
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        verbose_name=_("Opened by"),
        related_name="opened_by") 
    title = models.CharField(_("Title"), max_length=128)
    text = models.TextField(_("Text"), blank=True, null=True)
    email_message_id = models.TextField(null=True, blank=True)
    
    tags = TaggableManager()
