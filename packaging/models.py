# -*- coding: utf-8 -*-

from django.core.validators import RegexValidator
from django.db import models
from common.models import ClientField, Client

class Platform(models.Model):
    class Meta:
        verbose_name = u"Plateforme"

    name = models.CharField(max_length=256, verbose_name=u"Nom de la plateforme", blank=False)
    identifier = models.CharField(max_length=1024, verbose_name=u"Identification plateforme", blank=False)
    description = models.TextField(verbose_name=u"Description", blank=False)

    def __unicode__(self):
        return u"%s identified by %s" % (self.name, self.identifier)

class PackageKind(models.Model):
    class Meta:
        verbose_name = u"Type de programme"

    name = models.CharField(max_length=64, verbose_name=u"Nom du package")

    def __unicode__(self):
        return self.name

class PackageList(models.Model):
    class Meta:
        verbose_name = u"Liste de paquet"

    kind = models.ForeignKey(PackageKind, verbose_name=u"Type de package", blank=False)
    client = ClientField(Client, verbose_name=u"Client", blank=False)
    production = models.BooleanField(u"Version de production", default=False)

    def __unicode__(self):
        return u"%s pour %s%s" % (self.kind,self.client,self.production and " (PRODUCTION)" or "")

class Package(models.Model):
    class Meta:
        verbose_name = u"Paquet"

    name = models.CharField(max_length=256, verbose_name=u"Nom du paquet", blank=False, validators = [ RegexValidator(r"^[-+_0-9a-z]{5,}$", message=u"Nom invalide.")])
    short_description = models.CharField(max_length=64, verbose_name=u"Description courte", blank=False)
    description = models.TextField(verbose_name=u"Description Longue", null=True, blank=True)
    required = models.BooleanField(verbose_name=u"Obligatoire", default=True)
    platform = models.ForeignKey(Platform, verbose_name=u"Plateforme", blank=False)
    date_add = models.DateTimeField(verbose_name=u"Date d'ajout",auto_now_add=True, blank=False)
    version_major = models.PositiveIntegerField(verbose_name=u"Majeur de version", blank=False)
    version_minor = models.PositiveIntegerField(verbose_name=u"Mineur de version", blank=False)
    revision = models.PositiveIntegerField(verbose_name=u"Release", blank=False)
    package_list = models.ForeignKey(PackageList, verbose_name=u"Liste de paquets")

    def __unicode__(self):
        return u"%s %s.%s+%s platform %s" % (self.name, self.version_major, self.version_minor, self.revision, self.platform)

