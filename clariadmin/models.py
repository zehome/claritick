# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.template.loader import get_template
from django.template import Context
from django.utils.datastructures import SortedDict
from django.contrib.auth.models import User
from django.conf import settings
from common.rc4 import b64rc4crypt

from common.models import Client, ClientField, JsonField, ColorField
from datetime import date

FIELD_TYPES = (
   (u'1', u"texte"),            # CharField
   (u'2', u"booléen"),          # BooleanField
   (u'3', u"choix" ),           # ChoiceField
   (u'4', u"nombre"),           # IntegerField
   (u'5',u'date'),              # DateField
   (u'6',u'choix multiple'),    # MultipleChoiceField
   )

ACTIONS_LOG = [
    (0, u"consulté"),
    (1, u"créé"),
    (2, u"modifié")
    (3, u"supprimé")]

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
    color_fg = ColorField(name="Couleur texte", blank=True, null=True)
    color_bg = ColorField(name="Couleur fond", blank=True, null=True)
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

class HostQuerySet(models.query.QuerySet):
    def filter_by_site(self, site):
        return self.filter(Q(site__exact=site)
                        |Q(site__parent__exact=site)
                        |Q(site__parent__parent__exact=site))

    def filter_by_user(self, user):
        return self.filter(site__in=user.clients)

class HostManager(models.Manager):
    def get_query_set(self):
        return HostQuerySet(self.model).\
            select_related("site", "site__parent", "site__parent__parent",
                "type", "os", "supplier")
    def filter_by_user(self, user):
        return self.all().filter_by_user(user)


class ChromeCryptoStr(object):
    def __init__(self, data):
        self.data = data
    def __len__(self):
        return len(self.data)
    def __eq__(self, other):
        return self.data == other
    def __cmp__(self, other):
        return cmp(self.data, other)
    def __adapt__(self):
        pass
    def __unicode__(self):
        return u"{chromecrypto:%s}" % (self.data,)
    def __repr__(self):
        return u"{chromecrypto:%s}" % (self.data,)

class ChromeCryptoField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None: return value
        if isinstance(value, ChromeCryptoStr):
            return value
        return ChromeCryptoStr(value)

    def _encrypt(self, data):
        return b64rc4crypt(data, settings.CHROMECRYPTO_KEY)

    def get_prep_value(self, value):
        if value.data.startswith("{chromecrypto:"):
            return value.data[14:-1]
        return self._encrypt(value.data)

class Host(models.Model):
    class Meta:
        verbose_name = u"Machine"
        ordering = ['site', 'hostname']
        permissions = (
            ("can_access_clariadmin", u"Accès CLARIADMIN"),
        )

    objects = HostManager()

    site = ClientField(Client, verbose_name="Client", limit_choices_to={ 'parent__isnull': False })
    type = models.ForeignKey(HostType, verbose_name=u"Type d'hôte", blank=True, null=True)
    os = models.ForeignKey(OperatingSystem, verbose_name=u"Système d'exploitation", blank=True, null=True)
    hostname = models.CharField(u"Nom d'hôte", max_length=64)
    rootpw = ChromeCryptoField(u"Mot de passe root", max_length=64, blank=True, null=True)
    commentaire = models.TextField(blank=True, max_length=4096)
    ip = models.CharField("Adresse IP", max_length=128, blank=True, null=True)

    date_add = models.DateTimeField("Date d'ajout", auto_now_add=True)
    date_start_prod = models.DateField("Date de mise en service", blank=True, null=True)
    date_end_prod = models.DateField("Fin de mise en service", blank=True, null=True)

    supplier = models.ForeignKey(Supplier, verbose_name="Fournisseur", blank=True, null=True)
    model = models.CharField(u"Modèle", blank=True, max_length=64, null=True)

    location = models.CharField(u"Emplacement", blank=True, max_length=128, null=True)
    serial = models.CharField(u"Numéro de série", blank=True, max_length=128, null=True)
    inventory = models.CharField(u"Numéro d'inventaire", blank=True, max_length=128, null=True)

    status = models.CharField(u"Statut", max_length=32, blank=True, null=True)

    def get_absolute_url(self):
        return "/clariadmin/modify/%i" % (self.id,)

    def __unicode__(self):
        return u"%s on %s (%s)" % (self.hostname, self.site, self.ip)

    def get_text(self):
        """ Text representation for dialog based app """
        template = get_template("clariadmin/host.txt")
        context = Context({"host": self })
        return template.render(context)

    def copy_instance(self):
        """Return an unsaved copy of self and self's `AdditionnalFlied`s"""
        h = Host(site=self.site, type=self.type, hostname=self.hostname+'_copy',
            os=self.os, status=self.status, date_end_prod=self.date_end_prod,
            supplier=self.supplier, commentaire=self.commentaire +
            u"\n -> Copie de la machine %s(ip:%s, le:%s)"%(self.hostname, self.ip, date.today()),
             date_start_prod=self.date_start_prod
             , model=self.model, location=self.location)
        afs=SortedDict()
        for af in self.additionnalfield_set.all():
            AdditionnalField(field=af.field, host=h, value=af.value)#.save()
            afs['val_'+str(af.field.id)]=af.value
        return (h, afs)

    def available_for(self,user):
        return (self.site in user.clients)
    
class ParamAdditionnalField(models.Model):
    class Meta:
        verbose_name = u"Définition de champs complémentaires"
        ordering = (u"host_type",u"sorting_priority")
    host_type = models.ForeignKey(HostType, verbose_name=u"Type d'hôte")
    name = models.CharField(u"Nom", max_length=32)
    data_type = models.CharField(u"Type de donnée", max_length=4 , choices=FIELD_TYPES)
    # dans un cas de choices il sera stocké en json non indenté. ex: ["a","b","c"]
    default_values = JsonField(u"Valeur par défaut/choix", max_length=8192)
    fast_search = models.BooleanField(u"Champ recherché par défaut", default=False)
    sorting_priority = models.IntegerField(u"Priorité d'affichage", default=100)
    api_key = models.CharField(u"Nom d'exposition api", blank=True, max_length=64)
    def __unicode__(self):
        return u"%s"%(self.name,)

class AdditionnalFieldManager(models.Manager):
    def get_query_set(self):
        return super(AdditionnalFieldManager,self).get_query_set().\
            select_related("field")

class AdditionnalField(models.Model):
    objects = AdditionnalFieldManager()
    class Meta:
        verbose_name = u"Champs complémentaires"
        ordering = (u"field__sorting_priority",u"field__name")
    field = models.ForeignKey(ParamAdditionnalField, verbose_name="Origine du champ")
    value = models.CharField(u"Valeur", max_length=512)
    host = models.ForeignKey(Host, verbose_name=u"")

class HostEditLog(models.Model):
    class Meta:
        ordering = ('date',)
    host = models.ForeignKey(Host, verbose_name=u"", blank=True, null=True)
    user = models.ForeignKey(User, verbose_name=u"", blank=True, null=True)
    date = models.DateTimeField(u"Date d'ajout", auto_now_add=True)
    ip = models.CharField(u'Ip utilisateur', max_length=1024)
    action = models.IntegerField(u"Action" ,choices=ACTIONS_LOG)
    message = models.CharField(u'Action répertoriée', max_length=1024)
    def __init__(self,*args,**kwargs):
        print "#### Here HostEditLogArgs :->",args,kwargs
        action = kwargs.pop("action",None)
        if isinstance(str, action):
            action = dict((v,k) for k,v in ACTIONS_LOG)[action]
        super(HostEditLog,self).__init__(*args, action=action, **kwargs)

