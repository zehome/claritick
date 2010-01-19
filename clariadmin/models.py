# -*- coding: utf-8 -*-

from django.db import models
from claritick.common.models import Client, ClientField

class OperatingSystem(models.Model):
    class Meta:
        verbose_name = u"Système d'exploitation"
        ordering = ['name', 'version']
    
    name = models.CharField(u"Nom", max_length=64)
    version = models.CharField(u"Version", max_length=64)

    def __unicode__(self):
        return "%s %s" % (self.name, self.version)

class HostType(models.Model):
    class Meta:
        verbose_name = u"Type d'hôte"
        ordering = ['text']
    
    gateway = models.BooleanField("Gateway", default=False)
    text = models.TextField("Description", blank=True)

    def __unicode__(self):
        return u"%s" % (self.text,)

class Supplier(models.Model):
    class Meta:
        verbose_name = u"Fournisseur"
        ordering = ['name']
    
    name = models.CharField(u"Nom", max_length=64)

    def __unicode__(self):
        return u"%s" % (self.name,)

class Host(models.Model):
    class Meta:
        verbose_name = u"Machine"
        ordering = ['site', 'hostname']
    
    site = ClientField(Client, verbose_name="Site", limit_choices_to={ 'parent__isnull': False })
    type = models.ForeignKey(HostType, verbose_name=u"Type d'hôte", blank=True)
    os = models.ForeignKey(OperatingSystem, verbose_name=u"Système d'exploitation", blank=True)
    hostname = models.CharField(u"Nom d'hôte", max_length=64)
    rootpw = models.CharField(u"Mot de passe root", max_length=64, blank=True)
    commentaire = models.TextField(blank=True, max_length=4096)
    ip = models.CharField("Adresse IP", max_length=128, blank=True)
    
    date_add = models.DateTimeField("Date d'ajout", auto_now=True, auto_now_add=True)
    date_start_prod = models.DateField("Date de mise en service", auto_now_add=True, blank=True, null=True)
    date_end_prod = models.DateField("Fin de mise en service", blank=True, null=True)

    supplier = models.ForeignKey(Supplier, verbose_name="Fournisseur", blank=True)
    model = models.CharField(u"Modèle", blank=True, max_length=64)

    location = models.CharField(u"Emplacement", blank=True, max_length=128)
    serial = models.CharField(u"Numéro de série", blank=True, max_length=128)
    inventory = models.CharField(u"Numéro d'inventaire", blank=True, max_length=128)

    status = models.CharField(u"Statut", max_length=32, blank=True)
    automate = models.CharField(u"Automate", max_length=64, blank=True)

    # LC: TODO: handle documents

    def get_absolute_url(self):
        return "/clariadmin/modify/%i" % (self.id,)

    def __unicode__(self):
        return u"%s on %s (%s)" % (self.hostname, self.site, self.ip)

