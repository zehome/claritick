# -*- coding: utf-8 -*-

from django.db import models
from django.template.loader import get_template
from django.template import Context

from common.models import Client, ClientField, JsonField

CHOICES_FIELDS_AVAILABLE = (
   (1, u"texte"),
   (2, u"booléen"),
   (3, u"choix" ),
   (4, u"nombre"))


class OperatingSystem(models.Model):
    class Meta:
        verbose_name = u"Système d'exploitation"
        ordering = ['name', 'version']

    depleted = models.BooleanField(u"Obsolete", default=False)
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
    
    depleted = models.BooleanField(u"Obsolete", default=False)
    name = models.CharField(u"Nom", max_length=64)

    def __unicode__(self):
        return u"%s" % (self.name,)

class Host(models.Model):
    class Meta:
        verbose_name = u"Machine"
        ordering = ['site', 'hostname']
        permissions = (
            ("can_access_clariadmin", "Accès CLARIADMIN"),
        )
    
    site = ClientField(Client, verbose_name="Site", limit_choices_to={ 'parent__isnull': False })
    type = models.ForeignKey(HostType, verbose_name=u"Type d'hôte", blank=True, null=True)
    os = models.ForeignKey(OperatingSystem, verbose_name=u"Système d'exploitation", blank=True, null=True)
    hostname = models.CharField(u"Nom d'hôte", max_length=64)
    rootpw = models.CharField(u"Mot de passe root", max_length=64, blank=True, null=True)
    commentaire = models.TextField(blank=True, max_length=4096)
    ip = models.CharField("Adresse IP", max_length=128, blank=True, null=True)
    
    date_add = models.DateTimeField("Date d'ajout", auto_now=True, auto_now_add=True)
    date_start_prod = models.DateField("Date de mise en service", auto_now_add=True, blank=True, null=True)
    date_end_prod = models.DateField("Fin de mise en service", blank=True, null=True)

    supplier = models.ForeignKey(Supplier, verbose_name="Fournisseur", blank=True, null=True)
    model = models.CharField(u"Modèle", blank=True, max_length=64, null=True)

    location = models.CharField(u"Emplacement", blank=True, max_length=128, null=True)
    serial = models.CharField(u"Numéro de série", blank=True, max_length=128, null=True)
    inventory = models.CharField(u"Numéro d'inventaire", blank=True, max_length=128, null=True)

    status = models.CharField(u"Statut", max_length=32, blank=True, null=True)
#    automate = models.CharField(u"Automate", max_length=64, blank=True, null=True)

    # LC: TODO: handle documents

    def get_absolute_url(self):
        return "/clariadmin/modify/%i" % (self.id,)

    def __unicode__(self):
        return u"%s on %s (%s)" % (self.hostname, self.site, self.ip)
    
    def get_text(self):
        """ Text representation for dialog based app """
        template = get_template("clariadmin/host.txt")
        context = Context({"host": self })
        return template.render(context)

class ParamAdditionnalField(models.Model):
    class Meta:
        verbose_name = u"Définition de champs complémentaires"
        ordering = (u"host_type",u"name")
    host_type = models.ForeignKey(HostType, verbose_name=u"Type d'hôte")
    name = models.CharField(u"Nom", max_length=32)
    data_type = models.CharField(u"Type de donnée", max_length=8 , choices=CHOICES_FIELDS_AVAILABLE)
    # Le champ "default_values" peut être traité par la méthode parse.
    # dans un cas de choices il sera stocké en json non indenté. ex: ["a","b","c"]
    default_values = JsonField(u"Valeur par défaut/choix", max_length=512)
    fast_search = models.BooleanField(u"Champ recherché par défaut", default=False)
    def __unicode__(self):
        return u"%s"%(self.name,)

class AdditionnalField(models.Model):
    class Meta:
        verbose_name = u"Champs complémentaires"
        ordering = (u"field",u"value")
    field = models.ForeignKey(ParamAdditionnalField, verbose_name="Origine du champ")
    value = models.CharField(u"Valeur", max_length=128)
    host = models.ForeignKey(Host, verbose_name=u"")

