# -*- coding: utf-8 -*-

from django.db import models
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from common.models import Client, ClientField, ByteaField, OneLineTextField
from ticket.models import Ticket


class BonDeCommandeQuerySet(models.query.QuerySet):
    def filter_by_user(self, user):
        if user.is_superuser:
            return self
        return self.filter(models.Q(client__in=user.clients))


class BonDeCommandeManager(models.Manager):
    def get_query_set(self):
        return BonDeCommandeQuerySet(self.model)


class BonDeCommande(models.Model):
    objects = BonDeCommandeManager()

    class Meta:
        verbose_name = u"Bon de commande"
        ordering = ["-date_creation", ]

    def __unicode__(self):
        return u"Bon de commande n°%s" % (self.id,)

    date_creation = models.DateTimeField(u"Date de création",
                                         auto_now_add=True)
    client = ClientField(Client, verbose_name="Client",
                         blank=False, null=False)
    ticket = models.ForeignKey(Ticket, blank=True, null=True)
    comment = models.TextField(u"Commentaire", blank=True)

    def is_closed(self):
        if self.ticket:
            return self.ticket.is_closed
        return False


## Fichiers associés aux bon de commande
class BonDeCommandeFileManager(models.Manager):
    def get_query_set(self):
        qs = super(BonDeCommandeFileManager, self).get_query_set().\
                defer('data').select_related('bondecommande__id')
        return qs


class BonDeCommandeFile(models.Model):
    objects = BonDeCommandeFileManager()
    with_data = models.Manager()

    filename = models.CharField("Filename", max_length=1024)
    bondecommande = models.ForeignKey(BonDeCommande)
    content_type = OneLineTextField()
    data = ByteaField()
    date = models.DateTimeField(u"Date de création", auto_now_add=True)

    class Meta:
        verbose_name = u"Fichier"

    def __unicode__(self):
        """ LC: Oui, c'est dégeulasse
        Very uggly, I know... """
        name = self.filename and self.filename or "Fichier sans nom"
        if self.id:
            download_url = reverse("bdc_getfile", args=(self.id,))
            return mark_safe(u"<a href='%s'>%s</a>" % (download_url, name,))
        else:
            return name
