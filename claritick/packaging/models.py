# -*- coding: utf-8 -*-

import os

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import permalink

from common.models import ClientField, Client
from packaging.storage import packaging_storage

packagename_validator = RegexValidator(r"^[-+_0-9a-z]{5,}$", message=u"Nom invalide.")


class ClientPackageAuth(models.Model):
    class Meta:
        verbose_name = u"Authorisations client/package"

    client = models.ForeignKey(Client, verbose_name=u"Client", blank=False)
    key = models.CharField(max_length=64, unique=True, blank=False)

    def __unicode__(self):
        return u"Auth for %s" % (self.client,)

class Platform(models.Model):
    """
    system platform.
    linux, linux2, linux3, win32
    as returned by sys.platform in python.
    """
    class Meta:
        verbose_name = u"Plateforme"

    name = models.CharField(max_length=256,
                            verbose_name=u"Nom de la plateforme",
                            blank=False)
    identifier = models.CharField(max_length=1024,
                                  verbose_name=u"Identification plateforme",
                                  blank=False)
    description = models.TextField(verbose_name=u"Description",
                                   blank=False)

    def __unicode__(self):
        return self.name and self.name or u"Toutes"

class Package(models.Model):
    class Meta:
        verbose_name = u"Paquet"
        permissions = (
            ("can_access", u"Accès au système de gestion de paquet"),
        )
    clients = models.ManyToManyField(Client)
    name = models.TextField(verbose_name=u"Nom", blank=False, null=False)

    platform = models.ForeignKey(Platform,
                                 verbose_name=u"Plateforme",
                                 blank=True,
                                 null=True)
    date_add = models.DateTimeField(verbose_name=u"Date d'ajout",
                                    auto_now_add=True,
                                    blank=False)
    version = models.PositiveIntegerField(verbose_name=u"Version",
                                           blank=False,
                                           default=1)
    file = models.FileField(upload_to=".",
                            storage=packaging_storage,
                            blank=True,
                            null=True)

    def __unicode__(self):
        # LC: Do never use and or trick to return "False" value.
        if not self.file:
            fileStr = " (No file attached)"
        else:
            fileStr = ""

        return u"%s version %s (%s)%s" % (self.name, self.version,
            self.platform and self.platform or u"any",
            fileStr)

    def filename(self):
        return self.file and os.path.basename(self.file.name) or None

    @property
    def sha1(self):
        digest = None
        if self.file:
            storage = self.file.storage
            if storage:
                digest = storage.sha1(self.file.name)
        return digest

    @permalink
    def download_url(self):
        return ('packaging_download', [unicode(self.id), ])

class PackageConfig(models.Model):
    class Meta:
        verbose_name = u"Configuration"

    packageauth = models.ForeignKey(ClientPackageAuth, verbose_name=u"PackageAuth", blank=False, null=False)
    name = models.CharField(max_length=128, verbose_name=u"Nom", blank=False)
    pathname = models.CharField(max_length=128, verbose_name=u"Chemin d'installation", blank=False)
    server_ip = models.CharField(max_length=256, verbose_name=u"Server IP", blank=False)
    server_port = models.CharField(max_length=5, verbose_name=u"Server Port", blank=False)
    extra_commandline = models.CharField(max_length=1024, verbose_name=u"Extra command line", blank=True)
    git_url = models.CharField(max_length=1024, verbose_name=u"Git URL", blank=False)
    git_commit = models.CharField(max_length=1024, verbose_name=u"Git Commit", blank=False)
    ssh_rsa_public = models.TextField(verbose_name=u"SSH RSA Public Key", blank=False)
    ssh_rsa_private = models.TextField(verbose_name=u"SSH RSA Private Key", blank=False)

    def todict(self):
        return {
            "id": self.pk,
            "name": self.name,
            "type": "CLARILAB",
            "pathname": self.pathname,
            "server_ip": self.server_ip,
            "server_port": self.server_port,
            "extra_commandline": self.extra_commandline,
            "git_url": self.git_url,
            "git_commit": self.git_commit,
            "ssh_rsa_pub": self.ssh_rsa_public,
            "ssh_rsa_priv": self.ssh_rsa_private,
            "client": unicode(self.packageauth.client),
        }

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.git_url)
