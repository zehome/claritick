#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from clariadmin.models import Supplier
from common.models import ClientField, Client

class InstallationOrder(models.Model):
    serial = models.CharField("Numéreau de série",blank=False,null=False,max_length=64)
    hostname = models.CharField("nom d'hote",max_length=128,null=True,blank=True)
    site = ClientField(Client, verbose_name="Client", limit_choices_to={ 'parent__isnull': False })
    fai_classes = models.CharField("Classes FAI",max_length=256)
    ip = models.CharField("Adresse IP",max_length=64)
    netmask = models.CharField("Netmask",default="255.255.255.0",max_length=64)
    gateway = models.CharField("Gateway",max_length=64)
    dns1 = models.CharField("ip du serveur DNS 1",max_length=64)
    dns2 = models.CharField("ip du serveur DNS 2",max_length=64,null=True,blank=True)
    ip_mca = models.CharField("ip du serveur MCA",max_length=64,null=True,blank=True)
    ip_clarilab = models.CharField("ip du serveur Clarilab",max_length=64,null=True,blank=True)
    supplier = models.ForeignKey(Supplier, verbose_name="Fournisseur",null=True)
    inventory = models.CharField("N° d'inventaire",max_length=64,null=True,blank=True)
    commentaire = models.TextField("commentaire",max_length=4096,null=True,blank=True)
    location = models.CharField("emplacement",max_length=128,null=True,blank=True)
    rootpw = models.CharField("mot de passe",max_length=64)
    #model = models.CharField("modele",max_length=64)

